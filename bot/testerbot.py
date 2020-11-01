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

client = discord.Client()

#Lets us see who is playing
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

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

#Stores questions and answers in dictionary
#quizdict = { "q1":"ans1" , "q2":"ans2" }

#Reads the csv url and sorts data into chart?
#url='csv url'
#quizdata=pd.read_csv(url)
#quizdata

#Reads csv through file opposed to url
@client.event
async def on_message(message):
    author = message.author
    content = message.content
    ctx = message.channel
    file = message.attachments
    if file[0].filename.endswith('.csv'):
        await file[0].save('quiz.csv')
        with open('quiz.csv', newline='') as q:
            reader = csv.reader(q)
            for row in reader:
                await ctx.send(row)
        
client.run('NzY4Mjg3MTgzMzY2MTI3NjY2.X4-RMg.sHXghTn0SIp6ubkrHGJz_SgFQ1s')
