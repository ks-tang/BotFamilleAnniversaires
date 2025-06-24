import discord
from discord.ext import tasks, commands
import datetime
import json
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
import pytz
import requests


# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def charger_anniversaires():
    with open("anniversaires.json", "r") as f:
        return json.load(f)

@tasks.loop(time=datetime.time(hour=7, minute=0))  # 9h Paris
async def verifier_anniversaires():
    aujourd_hui = datetime.datetime.now().strftime("%m-%d")
    anniversaires = charger_anniversaires()
    canal = bot.get_channel(CHANNEL_ID)

    for personne in anniversaires:
        if personne["date"] == aujourd_hui:
            await canal.send(f"Aujourd'hui, c'est l'anniversaire de **{personne['prenom']}** ! Bon anniversaire **{personne['prenom']}** 🥳🎉🎊 ")
            print(f"Message envoyé pour l'anniversaire de {personne['prenom']}")

@tasks.loop(minutes=2)
async def verifier_anniversaire_console():
    print("⏰ Boucle de vérification lancée...")
    response = requests.get("parallel-dianne-pro-tang-kevin-f1cda2ca.koyeb.app/")
    aujourd_hui = datetime.datetime.now().strftime("%m-%d")
    anniversaires = charger_anniversaires()
    trouve = False
    if not trouve:
        print("Pas d'anniversaire aujourd'hui...")
    for personne in anniversaires:
        if personne["date"] == aujourd_hui:
            print(f"🎉 Il y a un anniversaire aujourd'hui : {personne['prenom']}")
            trouve = True
            break


@bot.event
async def on_ready():
    print(f"{bot.user} est connecté.")
    verifier_anniversaires.start()
    verifier_anniversaire_console.start()


keep_alive()
bot.run(TOKEN)
