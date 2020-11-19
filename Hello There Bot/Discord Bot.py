# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:07:08 2020

@author: derph
"""

import discord
from discord.ext import commands
import nest_asyncio
import asyncio
import os
import cv2
from PIL import Image
from PIL import ImageColor
from scipy import signal as sg
import numpy as np
import math
import string, random
import csv
import re
import time
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
nest_asyncio.apply()

tokenIn = open("Token Key.txt", "r+")
token = tokenIn.readline()

client = commands.Bot(command_prefix = '!')
mongo = MongoClient(tokenIn.readline())
db = mongo["quizInfo"]
client.quiz = mongo.quizInfo.quizinfos
client.elimination = None
client.players = {}

def myround(x, base=30):
    return base * round(x/base)

def MilesMorales (image, attrib):
    print("Run Program")
    #for y in range(0, len(image)):
     #   for x in range(0, len(image[y])):
      #      for z in range(0, 3):
       #         image[y][x][z] =  myround(image[y][x][z])   
    for y in range(0, len(image)):
        for x in range(0, len(image[y])):
            if sum(image[y][x])/3 >= 240 or sum(image[y][x])/3 < 5:
                image[y][x] = list(ImageColor.getrgb("purple"))
            else:
                break
        for x in range(len(image[y])-1, -1, -1):
            if sum(image[y][x])/3 >= 240 or sum(image[y][x])/3 < 5:
                image[y][x] = list(ImageColor.getrgb("purple"))
            else:
                break
    for x in range(0, len(image[0])):
        for y in range(0, len(image)):
            if sum(image[y][x])/3 >= 240 or sum(image[y][x])/3 < 5:
                image[y][x] = list(ImageColor.getrgb("purple"))
            elif sum(image[y][x])/3 - 85.33333333333333:
                break
        for y in range(len(image)-1, -1, -1):
            if sum(image[y][x])/3 >= 240 or sum(image[y][x])/3 < 5:
                image[y][x] = list(ImageColor.getrgb("purple"))
            elif sum(image[y][x])/3 != 85.33333333333333:
                break
    colorDict = {}
    for i, a in enumerate(attrib):
        newa = a
        if a in colorDict.keys():
            newa += "N"
        colorDict[newa] = [ImageColor.getrgb(a)[2], ImageColor.getrgb(a)[1], ImageColor.getrgb(a)[0]] 
        #colorDict[newa] = ImageColor.getrgb(a)
    colorDict["white"] = ImageColor.getrgb("white")
    
    miles = image.copy()
    for y in range(0, len(miles)):
        for x in range(0, len(miles[y])):
            if abs(miles[y][x][0] - 128) <= 0.1 and miles[y][x][1] == 0 and abs(miles[y][x][0] - 128) <= 0.1:
                miles[y][x] = [255, 255, 255]
            accuracy = []
            for i in colorDict.keys():
                accuracy.append(1-sum([abs(miles[y][x][ind]-c) for ind, c in enumerate(colorDict[i])])/765)
            accuracy = [accuracy.index(max(accuracy)), max(accuracy)]
            if accuracy[1] >= 0:
                if accuracy[0] == 0:
                    miles[y][x] = [0, 0, 0]
                elif accuracy[0] == 1:
                    miles[y][x] = [20, 20, 20]
                elif accuracy[0] == 2:
                    miles[y][x] = [0, 0, 255]
                elif accuracy[0] == 3:
                    miles[y][x] = [255, 255, 255]
                    miles[y][x-1] = [255, 255, 255]
    miles = cv2.cvtColor(miles, cv2.COLOR_BGR2RGB)
    return miles
    #Image.fromarray(miles).save("Miles.jpg")

def decodeMorse(morse_code):
    # ToDo: Accept dots, dashes and spaces, return human-readable message
    morse_dict = {'.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9', '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'", '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')', '.-...': '&', '---...': ':', '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-..-.': '"', '...-..-': '$', '.--.-.': '@', '...---...': 'SOS', '': ' '}
    morse_code = morse_code.replace("/", " ")
    morse_code = morse_code.split(" ")
    print(morse_code)
    for i in range(0, len(morse_code)-1):
        if morse_code[i] == '' and morse_code[i+1] == '':
            morse_code[i+1] = "poop"
    for x in range(0, morse_code.count("poop")):
        morse_code.remove("poop")
    for i in morse_code:
        if i not in morse_dict.keys():
            return "Invalid Morse"
    return "".join([morse_dict[i] for i in morse_code]).strip()

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

    for ext in pic_ext:
        if len(image) > 0 and image[0].filename.endswith(ext) and len(content) > 0:
            await image[0].save(image[0].filename)
            images = cv2.imread(image[0].filename)
            attrib = content.split("/")
            images = MilesMorales(images, attrib)
            Image.fromarray(images).save("New.jpg")
            await channel.send(file=discord.File('New.jpg'))
            await channel.send("My name is Miles Morales and for the last 2 seconds, I've been the one and only Schpiderman.")
    #if "spiderman" in message.content.lower():
     #   await channel.send("Send image (with white or transparent background) with three words separated by a \"/\" that describes the following physical aspects of his suit:")
      #  await channel.send("1. What color is the face and chest?")
       # await channel.send("2. What color is the side and legs?")
        #await channel.send("3. What color is the spider insignia and suit lines?")
    for i in content:
        if i in '/.- ':
            morse = True
        else:
            morse = False
            break
    if content == "--------------":
        morse = False
    print("{}: {}".format(author, content))
    if "hello there" in content.lower():
        await channel.send("General Kenobi")
    if "pogwon" in content.lower() or "juwon" in content.lower():
        await channel.send(file=discord.File('Pogwon.png'))
    if morse:
        await channel.send(decodeMorse(content))
    await client.process_commands(message)

@client.event
async def on_reaction_add(rxn, user):
    message = rxn.message
    channel = message.channel
    
    LastMsg = await channel.history().get(author__name='Hello There')
    if rxn.emoji == "💩" and user.name != "Hello There" and message.author.name == "Hello There" and LastMsg == message:
        client.players[user.name] = 0
    
@client.event
async def on_message_delete(message):
    author = message.author
    content = message.content
    channel = message.channel
    await channel.send('{} just deleted a message at {}'.format(author, channel))

@client.command()
async def run(message, Id):
    channel = message.channel
    try:
        doc = client.quiz.find_one({"_id": Id})
        questions = doc["questions"]
        answer_dict = {'🇦': "A", '🇧': "B", '🇨': "C", '🇩': "D", 
                               '🇪': "E", '🇫': "F", '🇬': "G", '🇭': "F", 
                               '🇮': "I", '🇯': "J"}
        
        await channel.send(embed = discord.Embed(title = "You have 10 seconds to react to the reaction below and join the game.", color = discord.Colour.blue()))
        InvMsg = await channel.history().get(author__name='Hello There')
        await InvMsg.add_reaction("💩")       
        time.sleep(10)
        InvMsg = await channel.history().get(author__name='Hello There')
        if InvMsg.reactions[0].count <= 1:
            await channel.send(embed = discord.Embed(title = "No players joined.  Ending the game.", color = discord.Colour.red()))
            return
        await channel.send(embed = discord.Embed(title = "Press 🇦 to play by elimination (wrong answers get you kicked) or 🇧 for subtraction (wrong answers lead to a score deduction).", color = discord.Colour.blue()))
        OptMsg = await channel.history().get(author__name='Hello There')
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
        if client.elimination:
            await channel.send(embed = discord.Embed(title = "You are playing by elimination", color = discord.Colour.blue()))
        else:
            await channel.send(embed = discord.Embed(title = "You are playing with score deductions", color = discord.Colour.blue()))
        await channel.send(embed = discord.Embed(title = "Starting", color = discord.Colour.green()))
        for iteration, row in enumerate(questions):
            if len(list(client.players.keys())) == 1 and client.elimination:
                await channel.send(embed = discord.Embed(title = list(client.players.keys())[0] + " wins for being the last survivor!", color = discord.Colour.blue()))
                podium = discord.Embed(
                    title = "Final Podium",
                
                    color = discord.Colour.gold()
                )
                podium.add_field(name= "🥇", value= list(client.players.keys())[0], inline=False)
                await channel.send(embed = podium)
                break
            row = row.split("ȟ̵̢̨̤͕̔͊̓͒ͅ")  
            for i in range(0, len(row)):
                if row[i] == '':
                    row[i] = False
            for i in range(0, row.count(False)):
                row.remove(False)
            def check(rxn, user):
                message = rxn.message
                if len(message.embeds) == 0:
                    print("No embeds")
                    return False
                if user.name != "Hello There" and user.name in client.players.keys() and message.embeds[0].title == "Question " + str(row[0]):
                    return True
                else:
                    return False
            def equation(x):
                return 300-300*(x/(int(row[4])/1.5))**2
            embed = discord.Embed(
                title = "Question " + row[0],
                description = row[1],
                
                colour = discord.Colour.blue()
            )
            if row[2] != "None":
                await channel.send(row[2])
            emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯'] 
            await channel.send(embed = embed)
            msg = await channel.history().get(author__name='Hello There')
            for emoji in emojis[:len(row[5:])]:
                await msg.add_reaction(emoji)
            time.sleep(3)
            for i, e  in enumerate(emojis[:len(row[5:])]):
                if row[5+i] == "TRUE":
                    row[5+i] = "True"
                elif row[5+i] == "FALSE":
                    row[5+i] = "False"
                embed.add_field(name=e, value=row[5+i])                    
            embed.add_field(name='Time:', value=row[4]+" seconds",inline=False)
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
                    await channel.send("Correct!  " + answer[1].name + " will be awarded " + str(int(round(pts, 0))) + " points.")
                    client.players[answer[1].name] += int(round(pts, 0))
                else: 
                    await channel.send("WRONG! The correct answer is " + row[3])
                    if client.elimination:
                        client.players.pop(answer[1].name, None)
                        await channel.send(answer[1].name + " will be kicked!")
                    else:
                        client.players[answer[1].name] -= int(round(pts, 0))
                        await channel.send(answer[1].name + " will lose " + str(int(round(pts, 0))) + " points!")
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
            time.sleep(5)
            if iteration == len(questions)-1:
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
    except:
        await channel.send("Invalid Quiz Code Given or Invalid Quiz Set")

@client.command()
async def upload(ctx, filetype):

    validfiletypes = ["url", "csv", "excel", "xls"]
    author = ctx.author
    channel = ctx.channel
    
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

        def quizcodemaker(col):
            filename = ''.join(random.choice(string.ascii_uppercase) for i in range(4))
            doc = col.find_one({"_id": "Key"})
            codes = doc["Codes"]
            for row in codes:
                if filename in row:
                    quizcodemaker()
            return filename
        
        try:
            message = await client.wait_for('message', timeout=30.0, check=check)
            file = message.attachments
            unique_quizcode = quizcodemaker(client.quiz)
            unique_filename = unique_quizcode + ".csv"

            if len(file) > 0 and file[0].filename.endswith('.csv'):
                quiz = requests.get(file[0].url).content.decode("utf-8")
                quiz = quiz.split("\n")
                quiz = csv.reader(quiz)
                for question in quiz:
                    await channel.send(question)
                        
            await ctx.channel.send("--------------")
            await ctx.channel.send("Is this the quiz set you wish to create? (Y/N)")

            def checkanswer(message):
                return (message.content.lower() == "y" or message.content.lower() == "n") and message.channel == ctx.channel

            try:
                userAnswer = await client.wait_for('message', timeout=15.0, check=checkanswer)
                print(userAnswer.content)
                if userAnswer.content.lower() == "y":

                    #inserts the code into the quiz key documents
                    x = client.quiz.update_one({"_id": "Key"}, {'$addToSet': {"Codes": unique_quizcode}})

                    client.quiz.insert_one({"_id": unique_quizcode, "name": str(author), "quizName": str(file[0].filename)[:-4], "questions": []})

                    quiz = requests.get(file[0].url).content.decode("utf-8")
                    quiz = quiz.split("\n")
                    quiz = csv.reader(quiz)
                    for row in quiz:
                        y = 'ȟ̵̢̨̤͕̔͊̓͒ͅ'.join(row)
                        x = client.quiz.update_one({"_id": unique_quizcode}, {'$addToSet': {"questions": y}})

                    await ctx.channel.send("Success! Your quiz set ID is " + unique_quizcode)

                elif userAnswer.content.lower() == "n":
                    await ctx.channel.send("Got it.")

            except asyncio.TimeoutError:
                await ctx.channel.send("You timed out!")
                await ctx.channel.send("Please resend the command if you still wish to upload a quiz set.")

        except asyncio.TimeoutError:
            await ctx.channel.send("You timed out!")
            await ctx.channel.send("Please resend the command if you still wish to upload a quiz set.")
    
@client.command()
async def myQuiz(ctx):
    
    author = ctx.author
    channel = ctx.channel
    
    embed = discord.Embed(
        title = "Quizzes made by " + str(author),
        
        color = discord.Colour.purple()
        )
    docs = client.quiz.find({"name": str(author)})
    for doc in docs:
        code = doc["_id"]
        name = doc["quizName"]
        embed.add_field(name = code, value = name, inline = False)
    await channel.send(embed=embed)
        

client.run(token)