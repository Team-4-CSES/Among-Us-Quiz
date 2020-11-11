# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:07:08 2020

@author: derph
"""

import discord
from discord.ext import commands
import nest_asyncio
import asyncio
import cv2
from PIL import Image
from PIL import ImageColor
from scipy import signal as sg
import numpy as np
import csv
import time
nest_asyncio.apply()

tokenIn = open("Token Key.txt", "r+").readline()
token = tokenIn

client = commands.Bot(command_prefix = '.')

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
    morse = True
    pic_ext = ['.jpg','.png','.jpeg']
    if len(image)>0 and image[0].filename.endswith('.csv'):
        print("reading csv")
        await image[0].save('quiz.csv')
        with open('quiz.csv', newline='') as q:
            reader = csv.reader(q, delimiter='~')
            i = 1
            answer_dict = {'🇦': "A", '🇧': "B", '🇨': "C", '🇩': "D", 
                           '🇪': "E", '🇫': "F", '🇬': "G", '🇭': "F", 
                           '🇮': "I", '🇯': "J"}
            for row in reader:
                def check(rxn, user):
                    if user.name != "Hello There":
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
                msg = await channel.history().get(author__name='Hello There')
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
                    else: 
                        await channel.send("WRONG! The correct answer is " + row[2])
                        await channel.send(answer[1].name + " will be kicked!")

    for ext in pic_ext:
        if len(image) > 0 and image[0].filename.endswith(ext) and len(content) > 0:
            await image[0].save(image[0].filename)
            images = cv2.imread(image[0].filename)
            attrib = content.split("/")
            images = MilesMorales(images, attrib)
            Image.fromarray(images).save("New.jpg")
            await channel.send(file=discord.File('New.jpg'))
            await channel.send("My name is Miles Morales and for the last 2 seconds, I've been the one and only Schpiderman.")
    if "spiderman" in message.content.lower():
        await channel.send("Send image (with white or transparent background) with three words separated by a \"/\" that describes the following physical aspects of his suit:")
        await channel.send("1. What color is the face and chest?")
        await channel.send("2. What color is the side and legs?")
        await channel.send("3. What color is the spider insignia and suit lines?")
    for i in content:
        if i not in '/.- ':
            morse = False
    print("{}: {}".format(author, content))
    if "hello there" in content.lower():
        await channel.send("General Kenobi")
    if "pogwon" in content.lower() or "juwon" in content.lower():
        await channel.send(file=discord.File('Pogwon.png'))
    if morse:
        await channel.send(decodeMorse(content))        

@client.event
async def on_reaction_add(rxn, user):
    message = rxn.message
    reactions = message.reactions
    #print(reactions)
    #print(user)

@client.event
async def on_message_delete(message):
    author = message.author
    content = message.content
    channel = message.channel
    await channel.send('{} just deleted a message at {}'.format(author, channel))
    
client.run(token)
    