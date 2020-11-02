import csv
import discord
import pandas as pd
from discord.ext import commands

client = commands.Bot(command_prefix="!")

# validquiztypes = ["fitb", "mc", "tf"]
# validfiletypes = ["url", "csv", "excel", "xls"]

@client.command()
async def upload(ctx, filetype, quiztype):
    if (filetype == "csv" and quiztype == "tf"):
        await ctx.send("Please upload your True/False .CSV file.")

    if (filetype == "csv" and quiztype == "mc"):
        await ctx.send("Please upload your Multiple Choice .CSV file.")

    if (filetype == "csv" and quiztype == "fitb"):
        await ctx.send("Please upload your Fill in the Blank .CSV file.")


@client.event
async def on_ready():
    print("Test Bot is ready")

@client.event
async def on_message(message):
    author = message.author
    content = message.content
    ctx = message.channel
    file = message.attachments
    if len(file)>0 and file[0].filename.endswith('.csv'):
        await file[0].save('quiz.csv')
        with open('quiz.csv', newline='') as q:
            reader = csv.reader(q)
            for row in reader:
                await ctx.send(row)


client.run("NzY2NDE4ODg4NzY1NzM0OTcy.X4jFNg.2KqfdDAIp1apUUa2wE5aG6tL374")
# client.run("woaTuHveX1K5Fer0sKRC9x_VNTGRhfHl")