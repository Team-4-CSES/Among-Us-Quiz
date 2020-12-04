# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:07:08 2020

@author: derph
"""

import discord
from discord.ext import commands
import nest_asyncio
import asyncio
import urllib.request
import numpy as np
import math
import string
import random
import csv
import time
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import keep_alive

nest_asyncio.apply()

tokenIn = open("token.txt", "r+")
token = tokenIn.readline().rstrip()

client = commands.Bot(command_prefix='!')
client.remove_command('help')
mongo = MongoClient(tokenIn.readline().rstrip())
db = mongo["quizInfo"]
client.quiz = mongo.quizInfo.quizinfos
client.elimination = None
client.shuffle = None
client.players = {}
botname = tokenIn.readline().rstrip()


@client.event
async def on_ready():
    print("Bot is Ready")
    await client.change_presence(activity=discord.Game("!help | <insert url here>"))


@client.event
async def on_reaction_add(rxn, user):
    message = rxn.message
    channel = message.channel

    LastMsg = await channel.history().get(author__name=botname)
    if rxn.emoji == "✔️" and user.name != botname and message.author.name == botname and LastMsg == message:
        client.players[user.name] = 0


@client.command()
async def run(message, Id):
    channel = message.channel
    try:
        doc = client.quiz.find_one({"_id": Id})
        if doc["privacy"] == "private":
            if doc["name"] != str(message.author.id):
                await channel.send(
                    embed=discord.Embed(title="You are not authorized to run this quiz.", colour=discord.Colour.red()))
                return
        questions = doc["questions"]
        answer_dict = {'🇦': "A", '🇧': "B", '🇨': "C", '🇩': "D",
                       '🇪': "E", '🇫': "F", '🇬': "G", '🇭': "F",
                       '🇮': "I", '🇯': "J"}

        await channel.send(
            embed=discord.Embed(title="You have 10 seconds to react to the reaction below and join the game.",
                                color=discord.Colour.blue()))
        InvMsg = await channel.history().get(author__name=botname)
        await InvMsg.add_reaction("✔️")
        time.sleep(10)
        InvMsg = await channel.history().get(author__name=botname)
        if InvMsg.reactions[0].count <= 1:
            await channel.send(
                embed=discord.Embed(title="No players joined.  Ending the game.", color=discord.Colour.red()))
            return
        await channel.send(embed=discord.Embed(
            title="Press 🇦 to play by elimination (wrong answers get you kicked) or 🇧 for subtraction (wrong answers lead to a score deduction).",
            color=discord.Colour.blue()))
        OptMsg = await channel.history().get(author__name=botname)
        await OptMsg.add_reaction("🇦")
        await OptMsg.add_reaction("🇧")

        # MAKE IT SO THAT ONLY PEOPLE IN THE GAME CAN VOTE
        def setCheck(rxn, user):
            if rxn.emoji in ["🇦", "🇧"] and user.name in client.players.keys():
                if rxn.emoji == "🇦":
                    client.elimination = True
                else:
                    client.elimination = False
                return True
            else:
                return False

        setting = await client.wait_for("reaction_add", check=setCheck)
        await OptMsg.clear_reaction("🇦")
        await OptMsg.clear_reaction("🇧")
        if client.elimination:
            await OptMsg.edit(embed=discord.Embed(title="You are playing by elimination", color=discord.Colour.blue()))
        else:
            await OptMsg.edit(
                embed=discord.Embed(title="You are playing with score deductions", color=discord.Colour.blue()))

        await channel.send(embed=discord.Embed(
            title="Would you like questions to be randomized?",
            color=discord.Colour.blue()))
        RandQ = await channel.history().get(author__name=botname)
        await RandQ.add_reaction("✔️")
        await RandQ.add_reaction("❌")

        # Function for checking for reaction given
        def randCheck(rxn, user):
            if rxn.emoji in ["✔️", "❌"] and user.name in client.players.keys():
                if rxn.emoji == "✔️":
                    random.shuffle(questions)
                    client.shuffle = True
                else:
                    client.shuffle = False
                return True
            else:
                return False

        setting = await client.wait_for("reaction_add", check=randCheck)
        await RandQ.clear_reaction("✔️")
        await RandQ.clear_reaction("❌")
        if client.shuffle:
            await RandQ.edit(embed=discord.Embed(title="Questions have been shuffled", color=discord.Colour.blue()))
        else:
            await RandQ.edit(
                embed=discord.Embed(title="Question order maintained", color=discord.Colour.blue()))

        await channel.send(embed=discord.Embed(title="Starting", color=discord.Colour.green()))
        Qnum = 1
        for iteration, row in enumerate(questions):
            if len(list(client.players.keys())) == 1 and client.elimination:
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
            row = row.split("ȟ̵̢̨̤͕̔͊̓͒ͅ")
            for i in range(0, len(row)):
                if row[i] == '':
                    row[i] = False
            for i in range(0, row.count(False)):
                row.remove(False)
            row[0] = str(Qnum)
            Qnum += 1
            print(row)

            def check(rxn, user):
                message = rxn.message
                if len(message.embeds) == 0:
                    print("No embeds")
                    return False
                if user.name != botname and user.name in client.players.keys() and message.embeds[
                    0].title == "Question " + str(row[0]):
                    return True
                else:
                    return False

            def equation(x):
                return 300 - 300 * (x / (int(row[4]) / 1.5)) ** 2

            embed = discord.Embed(
                title="Question " + row[0],
                description=row[1],

                colour=discord.Colour.blue()
            )
            if row[2] != "None":
                embed.set_image(url=row[2])
                # await channel.send(row[2])
            emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
            await channel.send(embed=embed)
            msg = await channel.history().get(author__name=botname)
            for emoji in emojis[:len(row[5:])]:
                await msg.add_reaction(emoji)
            time.sleep(1.5)
            for i, e in enumerate(emojis[:len(row[5:])]):
                if row[5 + i] == "TRUE":
                    row[5 + i] = "True"
                elif row[5 + i] == "FALSE":
                    row[5 + i] = "False"
                embed.add_field(name=e, value=row[5 + i])
            embed.set_footer(text="You have " + row[4] + " seconds")
            await msg.edit(embed=embed)
            answer = "Fail"
            t0 = time.perf_counter()
            try:
                answer = await client.wait_for("reaction_add", timeout=float(row[4]), check=check)
            except:
                await channel.send("No Response Given")
            if type(answer) != str:
                t1 = time.perf_counter()
                times = t1 - t0
                pts = equation(times)
                if pts < 10:
                    pts = 10
                print("Time:", times)
                if answer[0].emoji in answer_dict.keys() and answer_dict[answer[0].emoji] == row[3]:
                    await channel.send(
                        "Correct!  " + answer[1].name + " will be awarded " + str(int(round(pts, 0))) + " points.")
                    client.players[answer[1].name] += int(round(pts, 0))
                else:
                    await channel.send("WRONG! The correct answer is " + row[3])
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
            time.sleep(5)
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
        await channel.send(embed=discord.Embed(title="Invalid Quiz Code Given or Invalid Quiz Set",
                                               color=discord.Colour.red()))


@client.command()
async def upload(ctx, filetype):
    author = ctx.author
    channel = ctx.channel
    quiz = ""
    if filetype == "csv":

        await ctx.send("Please upload your .CSV file.")

        def check(message):
            return message.attachments[0].filename.endswith('.csv') and message.author == ctx.author

        # creates a 4 letter id and checks if it is unique. If not, reiterates. Returns unique id.

        def quizcodemaker(col):
            filename = ''.join(random.choice(string.ascii_uppercase) for i in range(4))
            doc = col.find_one({"_id": "Key"})
            codes = doc["Codes"]
            for row in codes:
                if filename in row:
                    quizcodemaker()
            return filename

        try:
            message = await client.wait_for('message', timeout=25.0, check=check)
            file = message.attachments
            unique_quizcode = quizcodemaker(client.quiz)

            if len(file) > 0 and file[0].filename.endswith('.csv'):
                quiz = requests.get(file[0].url).content.decode("utf-8")
                quiz = quiz.split("\n")
                quiz = list(csv.reader(quiz))
                EmbedList = []

                # checks if you used the template
                templatecheck = "Question No.,Question,Image URL,Answer,Time,A,B,C,D,E,F,G,H,I,J"
                if templatecheck not in ",".join(quiz[5]):
                    await channel.send(embed=discord.Embed(
                        title="Invalid .csv format! Please follow the template and follow the instructions listed. You can find the quiz template at https://docs.google.com/spreadsheets/d/1H1Fg5Lw1hNMRFWkorHuAehRodlmHgKFM8unDjPZMnUg/edit#gid=196296521",
                        colour=discord.Colour.red()))
                    return

                for row in quiz[6:]:
                    if set(list(row)) == {''}:
                        continue
                    for i in range(0, len(row)):
                        if row[i] == "":
                            row[i] = False
                    for i in range(0, row.count(False)):
                        row.remove(False)
                    embed = discord.Embed(
                        title="Question " + row[0],
                        description=row[1],

                        colour=discord.Colour.blue()
                    )
                    if row[2] != "None":
                        # checks if the image link works
                        if "cdn" in row[2]:
                            types = [".jpg", ".jpeg", ".png", ".gif"]
                            if not any(x in row[2] for x in types):
                                await channel.send(embed=discord.Embed(
                                    title="Invalid image URL for question " + row[
                                        0] + "! Please double check that you inputted a proper image URL (Right-click, \"copy image address\", paste).",
                                    colour=discord.Colour.red()))
                                return

                        else:
                            r = urllib.request.urlopen(row[2])
                            if r.headers.get_content_maintype() != "image":
                                await channel.send(embed=discord.Embed(
                                    title="Invalid image URL for question " + row[
                                        0] + "! Please double check that you inputted a proper image URL (Right-click, \"copy image address\", paste).",
                                    colour=discord.Colour.red()))
                                return

                        embed.set_image(url=row[2])
                    # await channel.send(row[2])
                    ANSWERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
                    emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
                    for i, e in enumerate(emojis[:len(row[5:])]):
                        if row[5 + i] == "TRUE":
                            row[5 + i] = "True"
                        elif row[5 + i] == "FALSE":
                            row[5 + i] = "False"

                        # checks if you have a correct answer choice
                        validanswerchoice = False
                        if row[3].islower():
                            await channel.send(
                                "Answer choices are case sensitive! Please change your correct answer choice for question " +
                                row[0])
                            return
                        if row[3] in ANSWERS[:len(row[5:])]:
                            validanswerchoice = True
                        if not validanswerchoice:
                            await channel.send(
                                "Question " + row[0] + " does not have a valid correct answer! (\"" + row[
                                    3] + "\") Please check the template for correct formatting.")
                            return
                        if ANSWERS[i] == row[3]:
                            embed.add_field(name=e, value=row[5 + i] + " (answer)")
                        else:
                            embed.add_field(name=e, value=row[5 + i])

                        # checks if time is valid

                        if not row[4].isdigit():
                            await channel.send(
                                "Question " + row[0] + " does not have a valid time! (\"" + row[
                                    4] + "\")")
                            return

                    embed.set_footer(text="You have " + row[4] + " seconds")
                    EmbedList.append(embed)

                j = 0
                await channel.send(embed=EmbedList[j])
                embed = await channel.history().get(author__name=botname)
                await embed.add_reaction("⬅️")
                await embed.add_reaction("➡️")
                await embed.add_reaction("✔️")
                await channel.send(
                    embed=discord.Embed(
                        title="These are the questions you made. Please navigate through them using the arrow keys. Press the checkmark reaction once you're done checking",
                        colour=discord.Colour.dark_magenta()))
                msg = await channel.history().get(author__name=botname)
                doneChecking = False

                def checkdirection(reaction, user):
                    return (user == message.author and str(reaction.emoji) == '✔️' or str(
                        reaction.emoji) == '⬅️' or str(
                        reaction.emoji) == '➡️') and reaction.message == embed

                while not doneChecking:
                    quizCheck = await client.wait_for("reaction_add", check=checkdirection)
                    if quizCheck[0].emoji == "⬅️":
                        j -= 1
                        if j < 0:
                            j = len(EmbedList) - 1
                        await embed.edit(embed=EmbedList[j])
                    if quizCheck[0].emoji == "➡️":
                        j += 1
                        if j > len(EmbedList) - 1:
                            j = 0
                        await embed.edit(embed=EmbedList[j])
                    if quizCheck[0].emoji == "✔️":
                        doneChecking = True
                        await embed.delete()
            await msg.edit(
                embed=discord.Embed(title="Is this the quiz set you wish to create?", colour=discord.Colour.purple()))
            await msg.add_reaction("✔️")
            await msg.add_reaction("❌")

            def checkanswer(reaction, user):
                return user == message.author and (str(reaction.emoji) == '✔️' or str(reaction.emoji) == '❌')

            try:
                userAnswer = await client.wait_for('reaction_add', timeout=20.0, check=checkanswer)
                if userAnswer[0].emoji == "✔️":
                    privacySetting = "public"
                    quizname = quiz[2][0]

                    await msg.clear_reaction("✔️")
                    await msg.clear_reaction("❌")

                    await msg.edit(embed=discord.Embed(
                        title="This quiz set is currently set as public. Would you like it private?",
                        colour=discord.Colour.green()))

                    await msg.add_reaction("✔️")
                    await msg.add_reaction("❌")
                    try:

                        privacy = await client.wait_for("reaction_add", timeout=20.0, check=checkanswer)
                        if privacy[0].emoji == "✔️":
                            privacySetting = "private"
                    except asyncio.TimeoutError:
                        await msg.clear_reaction("✔️")
                        await msg.clear_reaction("❌")
                        await msg.edit(embed=discord.Embed(
                            title="You timed out!",
                            colour=discord.Colour.red()))
                        return

                    await msg.clear_reaction("✔️")
                    await msg.clear_reaction("❌")

                    await msg.edit(embed=discord.Embed(
                        title="Okay, your quiz set will be " + privacySetting + ". Your current quiz name is **\"" + quizname + "\"**. Would you like to change it?",
                        colour=discord.Colour.red()))

                    await msg.add_reaction("✔️")
                    await msg.add_reaction("❌")

                    # creates quiz and uploads it into the database
                    def createquiz():
                        x = client.quiz.update_one({"_id": "Key"},
                                                   {'$addToSet': {"Codes": unique_quizcode}})

                        client.quiz.insert_one(
                            {"_id": unique_quizcode, "name": str(author.id), "quizName": quizname,
                             "questions": [], "privacy": privacySetting})

                        quiz = requests.get(file[0].url).content.decode("utf-8")
                        quiz = quiz.split("\n")
                        quiz = list(csv.reader(quiz))
                        for row in quiz[6:]:
                            if set(list(row)) == {''}:
                                continue
                            y = 'ȟ̵̢̨̤͕̔͊̓͒ͅ'.join(row)
                            x = client.quiz.update_one({"_id": unique_quizcode},
                                                       {'$addToSet': {"questions": y}})

                    try:
                        changeName = await client.wait_for('reaction_add', timeout=20.0, check=checkanswer)
                        if changeName[0].emoji == "✔️":
                            nameDesired = False
                            while not nameDesired:

                                await msg.clear_reaction("✔️")
                                await msg.clear_reaction("❌")

                                await msg.edit(embed=discord.Embed(
                                    title="Please type what you would like to name your quiz.",
                                    colour=discord.Colour.orange()))

                                def checkName(message):
                                    return message.channel == ctx.channel and message.author == ctx.author

                                try:
                                    desiredName = await client.wait_for("message", timeout=20.0, check=checkName)

                                    await msg.clear_reaction("✔️")
                                    await msg.clear_reaction("❌")

                                    await msg.edit(embed=discord.Embed(
                                        title="Your quiz's name is currently **\"" + desiredName.content + "\"**. Is this correct?",
                                        colour=discord.Colour.purple()))

                                    await msg.add_reaction("✔️")
                                    await msg.add_reaction("❌")

                                    try:
                                        nameConfirmation = await client.wait_for("reaction_add", timeout=20.0,
                                                                                 check=checkanswer)
                                        if nameConfirmation[0].emoji == "✔️":
                                            nameDesired = True
                                            quizname = desiredName.content

                                            createquiz()

                                            await msg.clear_reaction("✔️")
                                            await msg.clear_reaction("❌")

                                            if privacySetting == "public":
                                                await msg.edit(embed=discord.Embed(
                                                    title="Success! Your quiz set ID is " + unique_quizcode,
                                                    colour=discord.Colour.green()))
                                            elif privacySetting == "private":
                                                await author.send(embed=discord.Embed(
                                                    title="Success! Your private quiz set ID is " + unique_quizcode,
                                                    colour=discord.Colour.green()))
                                                await author.send(embed=discord.Embed(
                                                    title="You can also message this bot directly to run quizzes!",
                                                    colour=discord.Colour.green()))
                                        elif nameConfirmation[0].emoji == "❌":
                                            continue

                                    except asyncio.TimeoutError:
                                        await msg.clear_reaction("✔️")
                                        await msg.clear_reaction("❌")
                                        await msg.edit(embed=discord.Embed(
                                            title="You timed out!",
                                            colour=discord.Colour.red()))
                                        return

                                except asyncio.TimeoutError:
                                    await msg.edit(embed=discord.Embed(
                                        title="You timed out!",
                                        colour=discord.Colour.red()))
                                    return

                        elif changeName[0].emoji == "❌":

                            createquiz()

                            await msg.clear_reaction("✔️")
                            await msg.clear_reaction("❌")

                            if privacySetting == "public":
                                await msg.edit(embed=discord.Embed(
                                    title="Success! Your quiz set ID is " + unique_quizcode,
                                    colour=discord.Colour.green()))
                            elif privacySetting == "private":
                                await author.send(embed=discord.Embed(
                                    title="Success! Your private quiz set ID is " + unique_quizcode,
                                    colour=discord.Colour.green()))
                                await author.send(embed=discord.Embed(
                                    title="You can also message this bot directly to run quizzes!",
                                    colour=discord.Colour.green()))

                    except asyncio.TimeoutError:
                        await msg.clear_reaction("✔️")
                        await msg.clear_reaction("❌")
                        await msg.edit(embed=discord.Embed(
                            title="You timed out!",
                            colour=discord.Colour.red()))
                        return

                elif userAnswer[0].emoji == "❌":
                    await msg.clear_reaction("✔️")
                    await msg.clear_reaction("❌")
                    await msg.edit(embed=discord.Embed(
                        title="Got it. This quiz set won't be created.",
                        colour=discord.Colour.red()))
                    return

            except asyncio.TimeoutError:
                await msg.clear_reaction("✔️")
                await msg.clear_reaction("❌")
                await msg.edit(embed=discord.Embed(
                    title="You timed out!",
                    colour=discord.Colour.red()))
                return

        except asyncio.TimeoutError:
            await ctx.channel.send("You timed out!")
            return

        except:
            await ctx.channel.send("There was an issue reading your .csv file. Please retry the command.")


@client.command()
async def myQuiz(ctx):
    author = ctx.author
    channel = ctx.channel

    embed = discord.Embed(
        title="Quizzes made by " + str(author),

        color=discord.Colour.purple()
    )
    docs = client.quiz.find({"name": str(author.id)})
    for doc in docs:
        privacySetting = ""
        if doc["privacy"] == "private":
            privacySetting = " (private)"
        code = doc["_id"]
        name = doc["quizName"] + privacySetting
        embed.add_field(name=code, value=name, inline=False)
    await author.send(embed=embed)


@client.command()
async def delete(ctx, quizcode):
    try:
        channel = ctx.channel
        doc = client.quiz.find_one({"_id": quizcode})
        questions = doc["questions"]
        if doc["name"] != str(ctx.author.id):
            await channel.send(
                embed=discord.Embed(title="You are not authorized to delete this quiz", colour=discord.Colour.red()))
            return
        EmbedList = []
        for iteration, row in enumerate(questions):
            row = row.split("ȟ̵̢̨̤͕̔͊̓͒ͅ")
            for i in range(0, len(row)):
                if row[i] == '':
                    row[i] = False
            for i in range(0, row.count(False)):
                row.remove(False)
            embed = discord.Embed(
                title="Question " + row[0],
                description=row[1],

                colour=discord.Colour.blue()
            )
            if row[2] != "None":
                embed.set_image(url=row[2])
            ANSWERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
            for i, e in enumerate(emojis[:len(row[5:])]):
                if row[5 + i] == "TRUE":
                    row[5 + i] = "True"
                elif row[5 + i] == "FALSE":
                    row[5 + i] = "False"
                if ANSWERS[i] == row[3]:
                    embed.add_field(name=e, value=row[5 + i] + " (answer)")
                else:
                    embed.add_field(name=e, value=row[5 + i])
            embed.set_footer(text="You have " + row[4] + " seconds")
            EmbedList.append(embed)

        def checkdirection(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✔️' or str(reaction.emoji) == '⬅️' or str(
                reaction.emoji) == '➡️'

        j = 0
        await channel.send(embed=EmbedList[j])
        msg = await channel.history().get(author__name=botname)
        await channel.send(
            embed=discord.Embed(
                title="Verify that this is the correct quiz. Navigate using the arrow keys and click the check mark when you're done checking.",
                colour=discord.Colour.light_gray()))
        await msg.add_reaction("⬅️")
        await msg.add_reaction("➡️")
        await msg.add_reaction("✔️")

        doneChecking = False

        while not doneChecking:
            quizCheck = await client.wait_for("reaction_add", check=checkdirection)
            if quizCheck[0].emoji == "⬅️":
                j -= 1
                if j < 0:
                    j = len(EmbedList) - 1
                await msg.edit(embed=EmbedList[j])
            if quizCheck[0].emoji == "➡️":
                j += 1
                if j > len(EmbedList) - 1:
                    j = 0
                await msg.edit(embed=EmbedList[j])
            if quizCheck[0].emoji == "✔️":
                doneChecking = True
        await msg.delete()
        msg = await channel.history().get(author__name=botname)
        await msg.edit(
            embed=discord.Embed(title="Is this the quiz set you wish to delete?", colour=discord.Colour.orange()))
        await msg.add_reaction("✔️")
        await msg.add_reaction("❌")

        def checkanswer(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == '✔️' or str(reaction.emoji) == '❌')

        try:
            userAnswer = await client.wait_for('reaction_add', timeout=20.0, check=checkanswer)
            if userAnswer[0].emoji == "✔️":
                client.quiz.delete_one({"_id": quizcode})
                client.quiz.update_one({"_id": "Key"}, {"$pull": {"Codes": quizcode}})
                await msg.clear_reaction("✔️")
                await msg.clear_reaction("❌")
                await msg.edit(embed=discord.Embed(
                    title="Success! " + quizcode + " has been deleted",
                    colour=discord.Colour.green()))

            elif userAnswer[0].emoji == "❌":

                await msg.clear_reaction("✔️")
                await msg.clear_reaction("❌")
                await msg.edit(embed=discord.Embed(
                    title="Got it. Your quiz set won't be deleted.",
                    colour=discord.Colour.green()))
                return

        except asyncio.TimeoutError:
            await msg.clear_reaction("✔️")
            await msg.clear_reaction("❌")
            await msg.edit(embed=discord.Embed(
                title="You timed out!",
                colour=discord.Colour.red()))
            return

    except:
        await ctx.channel.send(
            embed=discord.Embed(title="Invalid code entered!", colour=discord.Colour.red()))


@client.command()
async def help(ctx):
    channel = ctx.channel
    embed = discord.Embed(
        title="All Commands",

        color=discord.Colour.gold()
    )
    uploadCSV = "This command lets you upload a quiz csv to the database. \n You can find the quiz template at https://docs.google.com/spreadsheets/d/1H1Fg5Lw1hNMRFWkorHuAehRodlmHgKFM8unDjPZMnUg/edit#gid=196296521"
    embed.add_field(name="!upload csv", value=uploadCSV, inline=False)
    run = "This command searches our database for a quiz of key QUIZKEY.  If QUIZKEY is valid, it will start the quiz."
    embed.add_field(name="!run QUIZKEY", value=run, inline=False)
    embed.add_field(name="!myQuiz", value="Direct messages you the keys and names of the quizzes you uploaded",
                    inline=False)
    embed.add_field(name="!delete QUIZKEY", value="Asks you for confirmation then deletes this QUIZKEY from your bot.")
    embed.add_field(name="!edit QUIZKEY", value="Allows you to edit quizzes that you have created.")
    embed.add_field(name="Bot Invitation Link",
                    value="https://discord.com/oauth2/authorize?client_id=765746012282683393&scope=bot&permissions=355392")
    await channel.send(embed=embed)


@client.command()
async def edit(ctx, quizKey):
    try:
        channel = ctx.channel
        doc = client.quiz.find_one({"_id": quizKey})
        if doc["name"] != str(ctx.author.id):
            await channel.send(
                embed=discord.Embed(title="You are not authorized to edit this quiz.", colour=discord.Colour.red()))
            return
        await channel.send(embed=discord.Embed(title="You are now editing " + quizKey + ": " + doc["quizName"],
                                               color=discord.Colour.green()))
        privacy = discord.Embed(title="This quiz's privacy is set to " + doc["privacy"],
                                description="Are you fine with this?",
                                color=discord.Colour.blue())
        await channel.send(embed=privacy)
        msg = await channel.history().get(author__name=botname)
        await msg.add_reaction("✔️")
        await msg.add_reaction("❌")

        def setCheck(reaction, user):
            return user == ctx.author and (
                        str(reaction.emoji) == '✔️' or str(reaction.emoji) == '❌') and reaction.message == msg

        try:
            setting = await client.wait_for("reaction_add", timeout=10.0, check=setCheck)
            private = ""
            if doc["privacy"] == "private":
                private = "public"
            if doc["privacy"] == "public":
                private = "private"
            await msg.clear_reaction("✔️")
            await msg.clear_reaction("❌")
            if setting[0].emoji == "❌":
                await msg.edit(embed=discord.Embed(description="Would you like to switch this quiz to " + private + "?",
                                                   color=discord.Colour.blue()))
                await msg.add_reaction("✔️")
                await msg.add_reaction("❌")
                try:
                    setting = await client.wait_for("reaction_add", timeout=10.0, check=setCheck)
                    await msg.clear_reaction("✔️")
                    await msg.clear_reaction("❌")
                    if setting[0].emoji == "✔️":
                        x = client.quiz.update_one({"_id": quizKey},
                                                   {"$set": {"privacy": private}})
                        await msg.edit(embed=discord.Embed(description="Alright! Changed privacy to " + private + "!",
                                                           color=discord.Colour.green()))
                    else:
                        await msg.edit(embed=discord.Embed(description="Not changing privacy.",
                                                           color=discord.Colour.green()))
                except asyncio.TimeoutError:
                    await msg.clear_reaction("✔️")
                    await msg.clear_reaction("❌")
                    await msg.edit(embed=discord.Embed(
                        title="You timed out!",
                        colour=discord.Colour.red()))
                    return
            else:
                await msg.edit(embed=discord.Embed(description="Not changing privacy", color=discord.Colour.green()))
        except asyncio.TimeoutError:
            await msg.clear_reaction("✔️")
            await msg.clear_reaction("❌")
            await msg.edit(embed=discord.Embed(
                    title="You timed out!",
                    colour=discord.Colour.red()))
            return
        question = discord.Embed(title="The quiz's name is " + doc["quizName"],
                                 description="Would you like to keep this?",
                                 color=discord.Colour.blue())
        await channel.send(embed=question)
        msg = await channel.history().get(author__name=botname)
        await msg.add_reaction("✔️")
        await msg.add_reaction("❌")

        def validQuestion(message):
            if message.author != ctx.author:
                return False
            elif message.content == "":
                return False
            else:
                return True

        try:
            setting = await client.wait_for("reaction_add", timeout=10.0, check=setCheck)
            await msg.clear_reaction("✔️")
            await msg.clear_reaction("❌")
            if setting[0].emoji == "❌":
                await msg.edit(
                    embed=discord.Embed(description="Write up what would you like to change the quiz name to.",
                                        color=discord.Colour.blue()))
                try:
                    question = await client.wait_for("message", timeout=20.0, check=validQuestion)
                    name = question.content
                    await msg.edit(
                        embed=discord.Embed(description="Would you like to set the quiz name to " + name + "?",
                                            color=discord.Colour.blue()))
                    await msg.add_reaction("✔️")
                    await msg.add_reaction("❌")
                    try:
                        rxn = await client.wait_for("reaction_add", check=setCheck)
                        await msg.clear_reaction("✔️")
                        await msg.clear_reaction("❌")
                        if rxn[0].emoji == "✔️":
                            x = client.quiz.update_one({"_id": quizKey},
                                                       {"$set": {"quizName": name}})
                            await msg.edit(embed=discord.Embed(description="Alright changed name to " + name + "!",
                                                               color=discord.Colour.green()))
                        else:
                            await msg.edit(embed=discord.Embed(description="Keeping name as " + doc["quizName"] + ".",
                                                               color=discord.Colour.green()))
                    except asyncio.TimeoutError:
                        await msg.clear_reaction("✔️")
                        await msg.clear_reaction("❌")
                        await msg.edit(embed=discord.Embed(
                            title="You timed out!",
                            colour=discord.Colour.red()))
                        return
                except asyncio.TimeoutError:
                    await msg.edit(embed=discord.Embed(
                        title="You timed out!",
                        colour=discord.Colour.red()))
                    return
            else:
                await msg.edit(embed=discord.Embed(description="Keeping name as " + doc["quizName"] + ".",
                                                   color=discord.Colour.green()))
        except asyncio.TimeoutError:
            await msg.clear_reaction("✔️")
            await msg.clear_reaction("❌")
            await msg.edit(embed=discord.Embed(
                title="You timed out!",
                colour=discord.Colour.red()))
            return
        questions = doc["questions"]
        EmbedList = []
        for iteration, row in enumerate(questions):
            row = row.split("ȟ̵̢̨̤͕̔͊̓͒ͅ")
            for i in range(0, len(row)):
                if row[i] == '':
                    row[i] = False
            for i in range(0, row.count(False)):
                row.remove(False)
            embed = discord.Embed(
                title="Question " + row[0],
                description=row[1],

                colour=discord.Colour.blue()
            )
            if row[2] != "None":
                embed.set_image(url=row[2])
            ANSWERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
            for i, e in enumerate(emojis[:len(row[5:])]):
                if row[5 + i] == "TRUE":
                    row[5 + i] = "True"
                elif row[5 + i] == "FALSE":
                    row[5 + i] = "False"
                if ANSWERS[i] == row[3]:
                    embed.add_field(name=e, value=row[5 + i] + " (answer)")
                else:
                    embed.add_field(name=e, value=row[5 + i])
            embed.set_footer(text="You have " + row[4] + " seconds")
            EmbedList.append(embed)

        def checkdirection(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✔️' or str(reaction.emoji) == '⬅️' or str(
                reaction.emoji) == '➡️'

        j = 0
        await channel.send(embed=EmbedList[j])
        msg = await channel.history().get(author__name=botname)
        await channel.send(
            embed=discord.Embed(
                description="These are the questions this quiz has. Navigate using the arrow keys and click the check mark when you're done checking.",
                colour=discord.Colour.light_gray()))
        await msg.add_reaction("⬅️")
        await msg.add_reaction("➡️")
        await msg.add_reaction("✔️")

        doneChecking = False

        while not doneChecking:
            quizCheck = await client.wait_for("reaction_add", check=checkdirection)
            if quizCheck[0].emoji == "⬅️":
                j -= 1
                if j < 0:
                    j = len(EmbedList) - 1
                await msg.edit(embed=EmbedList[j])
            if quizCheck[0].emoji == "➡️":
                j += 1
                if j > len(EmbedList) - 1:
                    j = 0
                await msg.edit(embed=EmbedList[j])
            if quizCheck[0].emoji == "✔️":
                doneChecking = True
        await msg.delete()
        msg = await channel.history().get(author__name=botname)
        await msg.edit(
            embed=discord.Embed(description="Are you fine with these questions?", colour=discord.Colour.orange()))
        await msg.add_reaction("✔️")
        await msg.add_reaction("❌")
        try:
            setting = await client.wait_for("reaction_add", timeout=10.0, check=setCheck)
            await msg.clear_reaction("✔️")
            await msg.clear_reaction("❌")
            if setting[0].emoji == "❌":
                await msg.edit(embed=discord.Embed(description="Please upload the csv of this updated quiz",
                                                   colour=discord.Colour.orange()))

                def check(message):
                    return message.attachments[0].filename.endswith('.csv') and message.author == ctx.author

                try:
                    message = await client.wait_for('message', timeout=15.0, check=check)
                    await msg.delete()
                    file = message.attachments

                    if len(file) > 0 and file[0].filename.endswith('.csv'):
                        quiz = requests.get(file[0].url).content.decode("utf-8")
                        quiz = quiz.split("\n")
                        quiz = list(csv.reader(quiz))
                        EmbedList = []
                        # checks if you used the template
                        templatecheck = "Question No.,Question,Image URL,Answer,Time,A,B,C,D,E,F,G,H,I,J"
                        if templatecheck not in ",".join(quiz[5]):
                            await channel.send(embed=discord.Embed(
                                title="Invalid .csv format! Please follow the template and follow the instructions listed. You can find the quiz template at https://docs.google.com/spreadsheets/d/1H1Fg5Lw1hNMRFWkorHuAehRodlmHgKFM8unDjPZMnUg/edit#gid=196296521",
                                colour=discord.Colour.red()))
                            return

                        for row in quiz[6:]:
                            if set(list(row)) == {''}:
                                continue
                            for i in range(0, len(row)):
                                if row[i] == "":
                                    row[i] = False
                            for i in range(0, row.count(False)):
                                row.remove(False)
                            embed = discord.Embed(
                                title="Question " + row[0],
                                description=row[1],

                                colour=discord.Colour.blue()
                            )
                            if row[2] != "None":
                                embed.set_image(url=row[2])
                            # await channel.send(row[2])
                            ANSWERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
                            emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
                            for i, e in enumerate(emojis[:len(row[5:])]):
                                if row[5 + i] == "TRUE":
                                    row[5 + i] = "True"
                                elif row[5 + i] == "FALSE":
                                    row[5 + i] = "False"

                                # checks if you have a correct answer choice
                                validanswerchoice = False
                                if row[3].islower():
                                    await channel.send(
                                        "Answer choices are case sensitive! Please change your correct answer choice for question " +
                                        row[0])
                                    return
                                if row[3] in ANSWERS[:len(row[5:])]:
                                    validanswerchoice = True
                                if not validanswerchoice:
                                    await channel.send(
                                        "Question " + row[0] + " does not have a valid correct answer! (\"" + row[
                                            3] + "\") Please check the template for correct formatting.")
                                    return
                                if ANSWERS[i] == row[3]:
                                    embed.add_field(name=e, value=row[5 + i] + " (answer)")
                                else:
                                    embed.add_field(name=e, value=row[5 + i])

                                # checks if time is valid

                                if not row[4].isdigit():
                                    await channel.send(
                                        "Question " + row[0] + " does not have a valid time! (\"" + row[
                                            4] + "\")")
                                    return

                            embed.set_footer(text="You have " + row[4] + " seconds")
                            EmbedList.append(embed)

                        j = 0
                        await channel.send(embed=EmbedList[j])
                        embed = await channel.history().get(author__name=botname)
                        await embed.add_reaction("⬅️")
                        await embed.add_reaction("➡️")
                        await embed.add_reaction("✔️")
                        await channel.send(
                            embed=discord.Embed(
                                title="These are the new questions you made. Please navigate through them using the arrow keys. Press the checkmark reaction once you're done checking",
                                colour=discord.Colour.dark_magenta()))
                        msg = await channel.history().get(author__name=botname)
                        doneChecking = False

                        def checkdirection(reaction, user):
                            return (user == message.author and str(reaction.emoji) == '✔️' or str(
                                reaction.emoji) == '⬅️' or str(
                                reaction.emoji) == '➡️') and reaction.message == embed

                        while not doneChecking:
                            quizCheck = await client.wait_for("reaction_add", check=checkdirection)
                            if quizCheck[0].emoji == "⬅️":
                                j -= 1
                                if j < 0:
                                    j = len(EmbedList) - 1
                                await embed.edit(embed=EmbedList[j])
                            if quizCheck[0].emoji == "➡️":
                                j += 1
                                if j > len(EmbedList) - 1:
                                    j = 0
                                await embed.edit(embed=EmbedList[j])
                            if quizCheck[0].emoji == "✔️":
                                doneChecking = True
                    await embed.delete()
                    await msg.edit(embed=discord.Embed(title="Is this the updated quiz set you wish to create?",
                                                       colour=discord.Colour.purple()))
                    await msg.add_reaction("✔️")
                    await msg.add_reaction("❌")
                    try:
                        setting = await client.wait_for("reaction_add", timeout=10.0, check=setCheck)
                        await msg.clear_reaction("✔️")
                        await msg.clear_reaction("❌")
                        if setting[0].emoji == "❌":
                            await msg.edit(embed=discord.Embed(description="Keeping the questions same",
                                                               colour=discord.Colour.green()))
                        else:
                            quiz = requests.get(file[0].url).content.decode("utf-8")
                            quiz = quiz.split("\n")
                            quiz = list(csv.reader(quiz))
                            x = client.quiz.update_one({"_id": quizKey},
                                                       {'$set': {"questions": []}})
                            for row in quiz[6:]:
                                if set(list(row)) == {''}:
                                    continue
                                y = 'ȟ̵̢̨̤͕̔͊̓͒ͅ'.join(row)
                                x = client.quiz.update_one({"_id": quizKey},
                                                           {'$addToSet': {"questions": y}})
                            await msg.edit(embed=discord.Embed(description="Questions have been successfully updated",
                                                               colour=discord.Colour.green()))
                    except asyncio.TimeoutError:
                        await msg.clear_reaction("✔️")
                        await msg.clear_reaction("❌")
                        await msg.edit(embed=discord.Embed(
                            title="You timed out!",
                            colour=discord.Colour.red()))
                        return
                except asyncio.TimeoutError:
                    await msg.edit(embed=discord.Embed(
                        title="You timed out!",
                        colour=discord.Colour.red()))
                    return
            else:
                await msg.edit(
                    embed=discord.Embed(description="Keeping the questions same", colour=discord.Colour.green()))
        except asyncio.TimeoutError:
            await msg.clear_reaction("✔️")
            await msg.clear_reaction("❌")
            await msg.edit(embed=discord.Embed(
                title="You timed out!",
                colour=discord.Colour.red()))
            return
        await channel.send(embed=discord.Embed(title="Finished editing", color=discord.Colour.green()))
    except:
        await ctx.channel.send(
            embed=discord.Embed(title="Invalid code entered!", colour=discord.Colour.red()))


keep_alive.keep_alive()
client.run(token)
