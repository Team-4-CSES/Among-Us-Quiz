import csv
import discord
import pandas as pd
import time
import asyncio
from discord.ext import commands

client = commands.Bot(command_prefix="!")

@client.command()
async def upload(ctx, filetype, quiztype):

    validquiztypes = ["fitb", "mc", "tf"]
    validfiletypes = ["url", "csv", "excel", "xls"]

    #FIXME check for valid arguments
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

        try:
            message = await client.wait_for('message', timeout=5.0, check=check)
            file = message.attachments
            if len(file) > 0 and file[0].filename.endswith('.csv'):
                await file[0].save('quiz.csv')
                with open('quiz.csv', newline='') as q:
                    reader = csv.reader(q)
                    for row in reader:
                        await ctx.channel.send(row)
            await ctx.channel.send("--------------")
            await ctx.channel.send("Is this the question you wish to create? (Y/N)")
        except asyncio.TimeoutError:
            await ctx.channel.send("You timed out! Please resend the command if you still wish to upload a quiz set.")

    '''
    if (filetype == "csv" and quiztype == "mc"):
        await ctx.send("Please upload your Multiple Choice .CSV file.")

    if (filetype == "csv" and quiztype == "fitb"):
        await ctx.send("Please upload your Fill in the Blank .CSV file.")
'''

@client.event
async def on_ready():
    print("Test Bot is ready")

async def on_message(message):

    await client.process_commands(message)




# client.run("NzY2NDE4ODg4NzY1NzM0OTcy.X4jFNg.2KqfdDAIp1apUUa2wE5aG6tL374")
client.run("NzcyNjIzNTE5ODgzNTkxNzYw.X59XuQ.6PEw5Dwt_IDHUs09TWottYqMExE")