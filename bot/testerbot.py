import discord
import csv
from discord.ext import commands

print ('loading bot')
intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '.', intents = intents)

@client.event
async def on_connect():
    print('discord is connected')

@client.event
async def on_ready():
    print('Bot is ready')

@client.event
async def on_member_join(member):
    print('{member} has joined a server.')

@client.command()
async def ping(ctx):
    await ctx.send('Pong!')

@client.command()
async def question(ctx):
    with open('TestSheet.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ',')
        for row in csv_reader:
            await ctx.send(','.join(row))



client.run('NzY4Mjg3MTgzMzY2MTI3NjY2.X4-RMg.sHXghTn0SIp6ubkrHGJz_SgFQ1s')
