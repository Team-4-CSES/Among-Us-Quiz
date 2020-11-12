# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:07:08 2020

@author: derph
"""

import discord
from discord.ext import commands
import asyncio
#import numpy as np
import csv
import time

token = open("token.txt", "r+").readline()

client = commands.Bot(command_prefix = '.')

client.players = {}

@client.event
async def on_ready():
    print("Bot is Ready")

@client.event
async def on_message(message):
    author = message.author
    content = message.content
    channel = message.channel
    image = message.attachments
    reactions = message.reactions
    morse = False
    pic_ext = ['.jpg','.png','.jpeg']
    if len(image)>0 and image[0].filename.endswith('.csv'):
        await channel.send(embed = discord.Embed(title = "You have 10 seconds to react to the reaction below and join the game.", color = discord.Colour.blue()))
        InvMsg = await channel.history().get(author__name='Nicole Tran')
        await InvMsg.add_reaction("💩")
        time.sleep(10)
        await channel.send("Starting")
        print("reading csv")
        await image[0].save('quiz.csv')
        with open('quiz.csv', newline='') as q:
            reader = csv.reader(q, delimiter='~')
            i = 1
            answer_dict = {'🇦': "A", '🇧': "B", '🇨': "C", '🇩': "D", 
                           '🇪': "E", '🇫': "F", '🇬': "G", '🇭': "F", 
                           '🇮': "I", '🇯': "J"}
            for row in reader:
                print(row)
                if row[0] == "done":
                    Final = discord.Embed(
                        title = "Final Podium",
                        
                        color = discord.Colour.gold()
                        )
                    rank = 1
                    medals = ["🥇", "🥈", "🥉"]
                    for player in list(client.players.keys())[:3]:
                        Final.add_field(name= medals[rank-1], value= player, inline=False)
                        rank += 1
                    await channel.send(embed=Final)
                    client.players = {}
                    break
                def check(rxn, user):
                    if user.name != "Nicole Tran" and user.name in client.players.keys():
                        return True
                    else:
                        return False
                def equation(x):
                    return 300-300*(x/(int(row[3])/1.5))**2
                embed = discord.Embed(
                    title = "Question " + row[0],
                    description = row[1],
                    
                    colour = discord.Colour.blue()
                )
                emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯'] 
                for i, e  in enumerate(emojis[:int(row[4])]):
                    embed.add_field(name=e, value=row[5+i])                    
                embed.add_field(name='Time:', value=row[3]+" seconds",inline=False)
                await channel.send(embed = embed)
                emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯'] 
                msg = await channel.history().get(author__name='Nicole Tran')
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
                        await channel.send("Correct!  " + answer[1].name + " will be awarded " + str(int(round(pts, 0))) + " points.")
                        client.players[answer[1].name] += int(round(pts, 0))
                    else: 
                        client.players.pop(answer[1].name, None)
                        await channel.send("WRONG! The correct answer is " + row[2])
                        await channel.send(answer[1].name + " will be kicked!")
                client.players = dict(sorted(client.players.items(), key = lambda kv:kv[1], reverse=True))
                print(client.players)
                rankings = discord.Embed(
                    title = "Rankings",
                    
                    color = discord.Colour.red()
                    )
                rank = 1
                for player in client.players.keys():
                    rankings.add_field(name= str(rank)+". "+player, value= str(client.players[player])+" point", inline=False)
                    rank += 1
                await channel.send(embed=rankings)

@client.event
async def on_reaction_add(rxn, user):
    message = rxn.message
    reactions = message.reactions
    if reactions[0].emoji == "💩" and user.name != "Nicole Tran" and message.author.name == "Nicole Tran":
        client.players[user.name] = 0
    
@client.event
async def on_message_delete(message):
    author = message.author
    content = message.content
    channel = message.channel
    await channel.send('{} just deleted a message at {}'.format(author, channel))
    
client.run(token)
    