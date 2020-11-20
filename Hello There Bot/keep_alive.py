# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:25:27 2020

@author: derph
"""

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return "Your bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)
    
def keep_alive():
    server = Thread(target=run)
    server.start()