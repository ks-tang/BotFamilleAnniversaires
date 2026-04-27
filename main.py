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

async def verifier_et_remercier(canal):
    # On remonte sur les dernières 24h
    hier = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    
    mots_souhaits = ["bon anniv", "joyeux anniversaire", "hb", "bravo", "félicitations", "merci"]
    noms_du_bot = ["bot", "robot", canal.client.user.name.lower()]
    utilisateurs_a_remercier = []

    print("🔍 Analyse des messages et ajout des réactions...")
    
    async for message in canal.history(after=hier):
        if message.author.bot:
            continue
        
        contenu = message.content.lower()
        
        # Détection : Contient un souhait/merci ET s'adresse au bot
        a_souhaite = any(mot in contenu for mot in mots_souhaits)
        parle_au_bot = (
            (canal.client.user in message.mentions) or 
            (message.reference and message.reference.resolved and message.reference.resolved.author == canal.client.user) or
            (any(nom in contenu for nom in noms_du_bot))
        )

        if a_souhaite and parle_au_bot:
            # 1. Ajouter la réaction coeur sur le message
            try:
                await message.add_reaction("❤️")
            except Exception as e:
                print(f"Erreur réaction : {e}")

            # 2. Ajouter l'utilisateur à la liste des remerciements groupés
            if message.author.mention not in utilisateurs_a_remercier:
                utilisateurs_a_remercier.append(message.author.mention)

    # 3. Message de remerciement groupé
    if utilisateurs_a_remercier:
        mentions = ", ".join(utilisateurs_a_remercier)
        await canal.send(f"Merci beaucoup {mentions} pour vos gentils messages ! Ça me fait chaud au circuit. ❤️🤖")

async def envoyer_rappel():
    # 1. On configure les permissions (intents)
    intents = discord.Intents.default()
    intents.message_content = True  # Indispensable pour lire les messages
    
    # 2. On crée le client avec ces permissions
    client = discord.Client(intents=intents)
    
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

        # Remerciements hier
        await verifier_et_remercier(canal)

        # Anniversaires du jour
        for personne in anniversaires:
            if personne["date"] == aujourd_hui:
                await canal.send(f"Aujourd'hui, c'est l'anniversaire de **{personne['prenom']}** ! Bon anniversaire **{personne['prenom']}** 🥳🎉🎊")
                print(f"Message envoyé pour {personne['prenom']}")
        
        await client.close() # Très important pour fermer le script proprement

    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(envoyer_rappel())
