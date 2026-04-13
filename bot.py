import discord
from discord.ext import tasks, commands
import datetime
import json
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
import pytz
import requests
import re

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

MERCI_REGEX = re.compile(
    r"\b(merci+|mercy|thx|thanks?)\b",
    re.IGNORECASE
)

def charger_anniversaires():
    with open("anniversaires.json", "r") as f:
        return json.load(f)

@tasks.loop(time=datetime.time(hour=8, minute=5))  # +1h Paris si heure d'hiver +2h si heure d'été
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


async def analyser_messages_du_jour():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ Channel introuvable")
        return

    # Début de la journée (00:00)
    aujourd_hui = datetime.datetime.now(datetime.timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    print("🔍 Analyse des messages de la journée...")

    async for message in channel.history(after=aujourd_hui, limit=500):
        if message.author.bot:
            continue

        contenu = message.content.lower()

        # 1️⃣ détecter merci
        if not MERCI_REGEX.search(contenu):
            continue

        # 2️⃣ détecter que ça vise le bot
        mots_bot = [
            "bot",
            "le bot",
            bot.user.name.lower()
        ]

        parle_du_bot = any(mot in contenu for mot in mots_bot)
        bot_mentionne = bot.user in message.mentions
        reponse_au_bot = (
            message.reference
            and message.reference.resolved
            and message.reference.resolved.author == bot.user
        )

        if parle_du_bot or bot_mentionne or reponse_au_bot:
            try:
                await message.add_reaction("👍")
                print(f"👍 Réaction ajoutée à un message de {message.author}")
            except Exception as e:
                print(f"❌ Erreur réaction : {e}")

    print("✅ Analyse terminée")



@bot.event
async def on_ready():
    print(f"{bot.user} est connecté.")
    verifier_anniversaires.start()
    verifier_anniversaire_console.start()

    await analyser_messages_du_jour()

    #channel = bot.get_channel(CHANNEL_ID)
    #message = await channel.fetch_message(1450444653781450754)
    #await message.add_reaction("👍")



keep_alive()
bot.run(TOKEN)
