import discord
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
    print(f'{member} has joined a server.')

@client.command()
async def ping(ctx):
    await ctx.send('Pong!')


client.run('NzY4Mjg3MTgzMzY2MTI3NjY2.X4-RMg.sHXghTn0SIp6ubkrHGJz_SgFQ1s')
