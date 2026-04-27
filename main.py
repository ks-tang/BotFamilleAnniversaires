import discord
import datetime
import json
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

def charger_anniversaires():
    with open("anniversaires.json", "r") as f:
        return json.load(f)

async def envoyer_rappel():
    client = discord.Client(intents=discord.Intents.default())
    
    @client.event
    async def on_ready():
        print(f"Connecté en tant que {client.user}")
        aujourd_hui = datetime.datetime.now().strftime("%m-%d")
        anniversaires = charger_anniversaires()
        canal = client.get_channel(CHANNEL_ID)

        if canal is None:
            print("Erreur : Canal introuvable")
            await client.close()
            return

        for personne in anniversaires:
            if personne["date"] == aujourd_hui:
                await canal.send(f"Aujourd'hui, c'est l'anniversaire de **{personne['prenom']}** ! Bon anniversaire **{personne['prenom']}** 🥳🎉🎊")
                print(f"Message envoyé pour {personne['prenom']}")
        
        await client.close() # Très important pour fermer le script proprement

    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(envoyer_rappel())
