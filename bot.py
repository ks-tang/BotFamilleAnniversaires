import discord
from discord.ext import tasks, commands
import datetime
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def charger_anniversaires():
    with open("anniversaires.json", "r") as f:
        return json.load(f)

@tasks.loop(time=datetime.time(hour=9, minute=0))  # Tous les jours à 9h
async def verifier_anniversaires():
    aujourd_hui = datetime.datetime.now().strftime("%m-%d")
    anniversaires = charger_anniversaires()
    canal = bot.get_channel(CHANNEL_ID)

    for personne in anniversaires:
        if personne["date"] == aujourd_hui:
            await canal.send(f"Aujourd'hui, c'est l'anniversaire de **{personne['prenom']}** ! Bon anniversaire **{personne['prenom']}** 🎉 ")

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté.")
    verifier_anniversaires.start()

bot.run(TOKEN)
