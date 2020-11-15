import csv
import discord
import asyncio
import nest_asyncio
import string, random
from discord.ext import commands
import time
import os
import math
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

client = commands.Bot(command_prefix="!")

tokenIn = open("token.txt", "r+")
token = tokenIn.readline()

cluster = MongoClient(tokenIn.readline())

db = cluster["quizInfo"]
collection = db["quizinfos"]

client.quiz = cluster.quizInfo.quizinfos
client.elimination = None
client.players = {}

@client.event
async def on_ready():
    print("Team 4 QuizBot Online!")

@client.command()
async def upload(ctx, filetype):

    validfiletypes = ["url", "csv", "excel", "xls"]

#checks if parameter is good
    filetypechecker = False
    for i in range(len(validfiletypes)):
        if validfiletypes[i] in filetype.lower():
            filetypechecker = True

    if not filetypechecker:
        await ctx.send("Error! Unsupported file type!")
        await ctx.send("The command's syntax goes as follows: !upload <filetype> <quiztype>.")

    if filetype == "csv":

        await ctx.send("Please upload your .CSV file.")

        def check(message):
            return message.attachments[0].filename.endswith('.csv') and message.author == ctx.author


        # checks if the 4 letter id is unique. If not, creates a new one.

        def quizcodemaker():
            filename = ''.join(random.choice(string.ascii_uppercase) for i in range(4))
            doc = collection.find_one({"_id": "Key"})
            codes = doc["Codes"]
            for row in codes:
                if filename in row:
                    quizcodemaker()
            return filename


        try:
            message = await client.wait_for('message', timeout=10.0, check=check)
            file = message.attachments
            unique_quizcode = quizcodemaker()
            unique_filename = unique_quizcode + ".csv"

            if len(file) > 0 and file[0].filename.endswith('.csv'):
                await file[0].save(unique_filename)
                with open(unique_filename, newline='') as q:
                    reader = csv.reader(q, delimiter='~')
                    for row in reader:
                        await ctx.channel.send(row)

            await ctx.channel.send("--------------")
            await ctx.channel.send("Is this the quiz set you wish to create? (Y/N)")

            def checkanswer(message):
                return (message.content.lower() == "y" or message.content.lower() == "n") and message.channel == ctx.channel

            try:
                userAnswer = await client.wait_for('message', timeout=15.0, check=checkanswer)
                print(userAnswer.content)
                if userAnswer.content.lower() == "y":

                    #inserts the code into the quiz key documents
                    x = client.quiz.update({"_id": "Key"}, {'$addToSet': {"Codes": unique_quizcode}})

                    client.quiz.insert_one({"_id": unique_quizcode, "questions": []})

                    with open(unique_filename, newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for row in reader:
                            y = ''.join(row)
                            x = client.quiz.update({"_id": unique_quizcode}, {'$addToSet': {"questions": y}})

                    await ctx.channel.send("Success! Your quiz set ID is " + unique_quizcode)
                    os.remove(unique_filename)


                elif userAnswer.content.lower() == "n":
                    await ctx.channel.send("Got it... the quizset has been deleted.")
                    os.remove(unique_filename)

            except asyncio.TimeoutError:
                await ctx.channel.send("You timed out!")
                await ctx.channel.send("Please resend the command if you still wish to upload a quiz set.")
                os.remove(unique_filename)

        except asyncio.TimeoutError:
            await ctx.channel.send("You timed out!")
            await ctx.channel.send("Please resend the command if you still wish to upload a quiz set.")


@client.command()
async def run(message, Id):
    channel = message.channel
    try:
        doc = collection.find_one({"_id": Id})
        questions = doc["questions"]
        answer_dict = {'🇦': "A", '🇧': "B", '🇨': "C", '🇩': "D",
                       '🇪': "E", '🇫': "F", '🇬': "G", '🇭': "F",
                       '🇮': "I", '🇯': "J"}

        await channel.send(
            embed=discord.Embed(title="You have 10 seconds to react to the reaction below and join the game.",
                                color=discord.Colour.blue()))
        InvMsg = await channel.history().get(author__name='Bobby Bot')
        await InvMsg.add_reaction("💩")
        time.sleep(10)
        InvMsg = await channel.history().get(author__name='Bobby Bot')
        if InvMsg.reactions[0].count <= 1:
            await channel.send(
                embed=discord.Embed(title="No players joined.  Ending the game.", color=discord.Colour.red()))
            return
        await channel.send(embed=discord.Embed(
            title="Press 🇦 to play by elimination (wrong answers get you kicked) or 🇧 for subtraction (wrong answers lead to a score deduction).",
            color=discord.Colour.blue()))
        OptMsg = await channel.history().get(author__name='Bobby Bot')
        await OptMsg.add_reaction("🇦")
        await OptMsg.add_reaction("🇧")

        # MAKE IT SO THAT ONLY PEOPLE IN THE GAME CAN VOTE
        def setCheck(rxn, user):
            print(user.name, rxn.emoji, client.players.keys())
            if rxn.emoji in ["🇦", "🇧"] and user.name in client.players.keys():
                if rxn.emoji == "🇦":
                    client.elimination = True
                else:
                    client.elimination = False
                return True
            else:
                return False

        setting = await client.wait_for("reaction_add", check=setCheck)
        if client.elimination:
            await channel.send(embed=discord.Embed(title="You are playing by elimination", color=discord.Colour.blue()))
        else:
            await channel.send(
                embed=discord.Embed(title="You are playing with score deductions", color=discord.Colour.blue()))
        await channel.send("Starting")
        for iteration, row in enumerate(questions):
            if len(list(client.players.keys())) == 1:
                await channel.send(
                    embed=discord.Embed(title=list(client.players.keys())[0] + " wins for being the last survivor!",
                                        color=discord.Colour.blue()))
                podium = discord.Embed(
                    title="Final Podium",

                    color=discord.Colour.gold()
                )
                podium.add_field(name="🥇", value=list(client.players.keys())[0], inline=False)
                await channel.send(embed=podium)
                break
            row = row.split("~")

            def check(rxn, user):
                if user.name != "Bobby Bot" and user.name in client.players.keys():
                    return True
                else:
                    return False

            def equation(x):
                return 300 - 300 * (x / (int(row[3]) / 1.5)) ** 2

            embed = discord.Embed(
                title="Question " + row[0],
                description=row[1],

                colour=discord.Colour.blue()
            )
            emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
            for i, e in enumerate(emojis[:int(row[4])]):
                embed.add_field(name=e, value=row[5 + i])
            embed.add_field(name='Time:', value=row[3] + " seconds", inline=False)
            await channel.send(embed=embed)
            emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
            msg = await channel.history().get(author__name='Bobby Bot')
            for emoji in emojis[:int(row[4])]:
                await msg.add_reaction(emoji)
            answer = "Fail"
            t0 = time.perf_counter()
            try:
                answer = await client.wait_for("reaction_add", timeout=float(row[3]), check=check)
            except:
                await channel.send("No Response Given")
            if type(answer) != str:
                t1 = time.perf_counter()
                times = t1 - t0
                pts = equation(times)
                if pts < 10:
                    pts = 10
                print("Time:", times)
                if answer[0].emoji in answer_dict.keys() and answer_dict[answer[0].emoji] == row[2]:
                    await channel.send(
                        "Correct!  " + answer[1].name + " will be awarded " + str(int(round(pts, 0))) + " points.")
                    client.players[answer[1].name] += int(round(pts, 0))
                else:
                    await channel.send("WRONG! The correct answer is " + row[2])
                    if client.elimination:
                        client.players.pop(answer[1].name, None)
                        await channel.send(answer[1].name + " will be kicked!")
                    else:
                        client.players[answer[1].name] -= int(round(pts, 0))
                        await channel.send(answer[1].name + " will lose " + str(int(round(pts, 0))) + " points!")
            client.players = dict(sorted(client.players.items(), key=lambda kv: kv[1], reverse=True))
            print(client.players)
            rankings = discord.Embed(
                title="Rankings",

                color=discord.Colour.red()
            )
            rank = 1
            for player in client.players.keys():
                rankings.add_field(name=str(rank) + ". " + player, value=str(client.players[player]) + " point",
                                   inline=False)
                rank += 1
            await channel.send(embed=rankings)
            if iteration == len(questions) - 1:
                Final = discord.Embed(
                    title="Final Podium",

                    color=discord.Colour.gold()
                )
                rank = 1
                medals = ["🥇", "🥈", "🥉"]
                for player in list(client.players.keys())[:3]:
                    Final.add_field(name=medals[rank - 1], value=player, inline=False)
                    rank += 1
                await channel.send(embed=Final)
                client.players = {}
                break
    except:
        await channel.send("Invalid Quiz Code Given")



#use only if we want an on_message for something // await client.process_commands(message)
#also leaving this here ''' since apostrophes are weird on IDEs
@client.event
async def on_reaction_add(rxn, user):
    message = rxn.message
    reactions = message.reactions
    if reactions[0].emoji == ":poop:" and user.name != "Bobby Bot" and message.author.name == "Bobby Bot":
        client.players[user.name] = 0

tokenIn = open("token.txt", "r+").readline()
token = tokenIn
client.run(token)

#hello

#hi