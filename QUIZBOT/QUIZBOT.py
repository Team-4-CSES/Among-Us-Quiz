import csv
import discord
import pandas as pd
import time
import asyncio
import string, random
# import uuid
from discord.ext import commands

client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    print("quizbot online")

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

        def filenamechecker(filename):
            with open("unique ids.csv", "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if filename in row:
                        filename = ''.join(random.choice(string.ascii_uppercase) for i in range(4)) + ".csv"
                        filenamechecker(filename)

        try:
            message = await client.wait_for('message', timeout=10.0, check=check)
            file = message.attachments
            unique_quizcode = ''.join(random.choice(string.ascii_uppercase) for i in range(4))
            unique_filename = unique_quizcode + ".csv"


            filenamechecker(unique_filename)

            with open("unique ids.csv", "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([unique_filename])

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
                    await ctx.channel.send("Success! Your quiz set ID is " + unique_quizcode)
                elif userAnswer.content.lower() == "n":
                    await ctx.channel.send("Got it. Quizset deleted.")
                    os.remove(unique_filename)
                    #FIXME delete the last row within the CSV aka the new unique code

            except asyncio.TimeoutError:
                await ctx.channel.send("You timed out!")
                await ctx.channel.send("Please resend the command if you still wish to upload a quiz set.")

        except asyncio.TimeoutError:
            await ctx.channel.send("You timed out!")
            await ctx.channel.send("Please resend the command if you still wish to upload a quiz set.")


@client.command()
async def run(ctx, quizcode):
    channel = ctx.channel
    quizname = quizcode + ".csv"
    with open(quizname, newline='') as q:
        reader = csv.reader(q, delimiter='~')
        i = 1
        answer_dict = {'🇦': "A", '🇧': "B", '🇨': "C", '🇩': "D",
                           '🇪': "E", '🇫': "F", '🇬': "G", '🇭': "F",
                           '🇮': "I", '🇯': "J"}
        for row in reader:
            def check(rxn, user):
                if user.name != "Bobby Bot":
                    return True
                else:
                    return False


            # tracks the amount of time elapsed from question start
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
            await ctx.channel.send(embed=embed)
            emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
            msg = await ctx.channel.history().get(author__name='Bobby Bot')
            for emoji in emojis[:int(row[4])]:
                await msg.add_reaction(emoji)
            answer = "Fail"
            t0 = time.perf_counter()
            try:
                answer = await client.wait_for("reaction_add", timeout=float(row[3]), check=check)
            except:
                await ctx.channel.send("No Response Given")
            if type(answer) != str:
                t1 = time.perf_counter()
                times = t1 - t0
                pts = equation(times)
                if pts < 10:
                    pts = 10
                print("Time:", times)
                if answer[0].emoji in answer_dict.keys() and answer_dict[answer[0].emoji] == row[2]:
                    await ctx.channel.send(
                        "Correct!  " + answer[1].name + " will be awarded " + str(int(round(pts, 0))) + " points.")
                else:
                    await ctx.channel.send("WRONG!")
                    await ctx.channel.send(answer[1].name + " will be kicked!")



#use only if we want an on_message for something // await client.process_commands(message)
#also leaving this here ''' since apostrophes are weird on IDEs


tokenIn = open("token.txt", "r+").readline()
token = tokenIn
client.run(token)