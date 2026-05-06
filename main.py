import sys
print("🚀 DÉMARRAGE DU SCRIPT PYTHON", flush=True)
import discord
import datetime
import json
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
#TOKEN = os.environ.get("TOKEN")
#CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

def charger_anniversaires():
    print("Chargement de la liste des anniversaires...", flush=True)
    with open("anniversaires.json", "r") as f:
        return json.load(f)

async def verifier_et_remercier(canal):
    print("Vérification des messages de la veille...", flush=True)
    # On remonte sur les dernières 24h
    hier = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)

    moi = canal.guild.me
    mots_felicitations = ["anniv", "anniversaire", "hb", "bravo", "félicitations"]
    mots_merci = ["merci", "thx", "thanks", "mrc"]
    noms_du_bot = ["bot", "robot", "test", "TEST"]
    utilisateurs_a_remercier = []

    print("🔍 Analyse des messages et ajout des réactions...", flush=True)

    try:
        async for message in canal.history(limit=30, oldest_first=False):

            print(f"📥 Message trouvé : '{message.content}' de {message.author}", flush=True)
                  
            if message.created_at < hier:
                print(f"↳ Trop vieux ({message.created_at}), j'arrête.", flush=True)
                break
            if message.author.bot:
                print(message.author.bot, flush=True)
                print("bot", flush=True)
                continue
            
            contenu = message.content.lower()
            print(contenu, flush=True)
            
            # Détection : Contient un souhait/merci ET s'adresse au bot
            parle_au_bot = (
                (moi in message.mentions) or 
                (message.reference and message.reference.resolved and message.reference.resolved.author == moi) or
                (any(nom in contenu for nom in noms_du_bot))
            )
    
            if parle_au_bot:
                # CAS 1 : On lui souhaite son anniversaire / On le félicite
                if any(mot in contenu for mot in mots_felicitations):
                    try:
                        await message.add_reaction("❤️")
                    except: pass
                    
                    if message.author.mention not in utilisateurs_a_remercier:
                        utilisateurs_a_remercier.append(message.author.mention)
                
                # CAS 2 : On lui dit juste merci
                elif any(mot in contenu for mot in mots_merci):
                    try:
                        await message.add_reaction("👍") 
                    except: pass
    
        print("Messages de la veille vérifiés ✅", flush=True)
    
        # 3. Message de remerciement groupé
        if utilisateurs_a_remercier:
            mentions = ", ".join(utilisateurs_a_remercier)
            await canal.send(f"Merci beaucoup {mentions} pour vos gentils messages ! Ça me fait chaud au circuit. ❤️🤖")

    except Exception as e:
        print(f"⚠️ Erreur lors de la lecture de l'historique : {e}", flush=True)

    print("✅ Vérification terminée.", flush=True)

async def run_bot():
    print("Configuration des permissions...", flush=True)
    # 1. On configure les permissions (intents)
    # intents = discord.Intents.default()
    intents = discord.Intents.all()
    intents.message_content = True  # Indispensable pour lire les messages
    
    # 2. On crée le client avec ces permissions
    client = discord.Client(intents=intents)

    print("Configuration terminée ✅", flush=True)
    
    @client.event
    async def on_ready():
        print("✅ Le bot est réveillé et tente de travailler...", flush=True)
        print(f"Connecté en tant que {client.user}", flush=True)
        aujourd_hui = datetime.datetime.now().strftime("%m-%d")
        canal = client.get_channel(CHANNEL_ID)
        
        if canal is None:
            print("Erreur : Canal introuvable", flush=True)
            await client.close()
            return

        # Fonction vérification et remerciement
        await verifier_et_remercier(canal)

        # Chargement des anniversaires
        anniversaires = charger_anniversaires()

        for personne in anniversaires:
            if personne["date"] == aujourd_hui:
                await canal.send(f"Aujourd'hui, c'est l'anniversaire de **{personne['prenom']}** ! Bon anniversaire **{personne['prenom']}** 🥳🎉🎊")
                print(f"✅ Message envoyé pour {personne['prenom']}", flush=True)

        print("FIN SCRIPT", flush=True)
        await client.close() # Très important pour fermer le script proprement

    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(run_bot())
