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
    print("Bobby bot online >:)")

@client.command()
async def upload(ctx, filetype, quiztype):

    validquiztypes = ["fitb", "mc", "tf"]
    validfiletypes = ["url", "csv", "excel", "xls"]


    # FIXME check for valid arguments

    filetypechecker = False
    quiztypechecker = False
    for i in range(len(validfiletypes)):
        if validfiletypes[i] in filetype.lower():
            filetypechecker = True
    for j in range(len(validquiztypes)):
        if validquiztypes[j] in quiztype.lower():
            quiztypechecker = True

    if not filetypechecker:
        await ctx.send("Error! Unsupported file type!")
        await ctx.send("The command's syntax goes as follows: !upload <filetype> <quiztype>.")
    elif not quiztypechecker:
        await ctx.send("Error! Invalid quiz type!")
        await ctx.send("The command's syntax goes as follows: !upload <filetype> <quiztype>.")

    if filetype == "csv" and quiztype == "tf":

        await ctx.send("Please upload your True/False .CSV file.")

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
                    reader = csv.reader(q)
                    for row in reader:
                        await ctx.channel.send(row)

            await ctx.channel.send("--------------")
            await ctx.channel.send("Is this the quiz set you wish to create? (Y/N)")

            def checkanswer(message):
                return message.content.lower() == "y" and message.channel == ctx.channel
            try:
                userAnswer = await client.wait_for('message', timeout=15.0, check=checkanswer)
                print(userAnswer.content)
                if userAnswer.content.lower() == "y":
                    await ctx.channel.send("Success! Your quiz set ID is " + unique_quizcode)
                elif userAnswer.content.lower() == "n":
                    await ctx.channel.send("Got it. Quizset deleted.")


            except asyncio.TimeoutError:
                await ctx.channel.send("You timed out!")
                await ctx.channel.send("Please resend the command if you still wish to upload a quiz set.")

        except asyncio.TimeoutError:
            await ctx.channel.send("You timed out!")
            await ctx.channel.send("Please resend the command if you still wish to upload a quiz set.")

    '''
    if (filetype == "csv" and quiztype == "mc"):
        await ctx.send("Please upload your Multiple Choice .CSV file.")

    if (filetype == "csv" and quiztype == "fitb"):
        await ctx.send("Please upload your Fill in the Blank .CSV file.")
    '''

@client.command()
async def run(ctx, quizcode):
    channel = ctx.channel
    quizname = quizcode + ".csv"
    with open(quizname, newline='') as q:
        reader = csv.reader(q)
        i = 1
        answer_dict = {'🇦': "T", '🇧': "F"}
        for row in reader:
            def check(rxn, user):
                if user.name != "Bobby Bot":
                    return True
                else:
                    return False

            embed = discord.Embed(
                title="Question " + str(i),
                description=row[1],

                colour=discord.Colour.blue()
            )
            embed.add_field(name='🇦', value='true')
            embed.add_field(name='🇧', value='false')
            embed.add_field(name='Time:', value=row[3] + " seconds", inline=False)
            await channel.send(embed=embed)
            # emojis = ['🇦', '🇧', '🇨', '🇩']
            emojis = ['🇦', '🇧']
            msg = await channel.history().get(author__name='Bobby Bot')
            for emoji in emojis:
                await msg.add_reaction(emoji)
            i += 1
            answer = "Fail"
            try:
                answer = await client.wait_for("reaction_add", timeout=float(row[3]), check=check)
            except:
                await channel.send("No Response Given")
            if type(answer) != str:
                if answer[0].emoji in answer_dict.keys() and answer_dict[answer[0].emoji] == row[2]:
                    await channel.send("Correct!")
                else:
                    await channel.send("WRONG!")
                    await channel.send(answer[1].name + " will be kicked!")



#use only if we want an on_message for something // await client.process_commands(message)
#also leaving this here ''' since apostrophes are weird on IDEs


tokenIn = open("token.txt", "r+").readline()
token = tokenIn
client.run(token)