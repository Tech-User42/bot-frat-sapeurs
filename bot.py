##############################################################
############# IMPORTATION DES MODULES DE DISCORD #############
##############################################################
import discord
from discord import Member
from discord.ext import commands
from discord.utils import get
from discord_webhook import DiscordWebhook, DiscordEmbed # MODULE POUR FAIRE DES WEBHOOK AVEC EMBED
##############################################################
############# IMPORTATION DES MODULES DE PYTHON ##############
##############################################################
import time
from datetime import datetime 
import os 
from random import randint
import requests
import json
from math import floor 
import sqlite3
##############################################################
############# IMPORTATION DES MODULES DE GOOGLE ##############
##############################################################
import gspread
from oauth2client.service_account import ServiceAccountCredentials
##############################################################
############# DEFINITION DES CONSTANTES DU BOT ###############
##############################################################


PREFIX = "!" # Prefix à mettre devant la commande Ex : !pds .

TOKEN =  "ODg4MTQ5NTE4Mzg4OTgxODEz.YUOfsg.JdKBiGl5vJy8LznlT5TEshPBx7s" # Token du bot NE JAMAIS PARTAGER VOTRE TOKEN DE BOT !




LISTE_STATUS=["s'occupe de l'administratif","gère le CSP"] # Liste des status apparaissant sur le bot. 

botstatus = LISTE_STATUS[randint(0,len(LISTE_STATUS)-1)] # Prend un status aléatoire dans LISTE_STATUS.

MOTS_BANNIS = ["nitro","everyone","here"] # Liste de mot que le bot detectera et supprimera automatiquement.

SERVEUR_ID = 850334186560421918 # ID du serveur

WEBHOOK_LOGS = "https://discord.com/api/webhooks/932353627861962872/psG8oPeJ_-x-YcqF5nOR10BffqIUwVDwMSopRJq2vnAzydac-KU83WJcjM_WbzJPZL7I" # Lien du webhook servant aux logs du bot.

CHANNEL_SERVICE = 850334230533767198 #ID Du channel d'annonce de Prise et fin de service.

ROLE_SAPEURS = 850700741773754419 #ID du rôle des sapeurs pompiers, rôles nécessaire pour executer les commandes.

EMOJI_SP = '❌' # Nom de l'emoji qui sera ajouté en dessous des messages du bot.

URL_AVATAR_WEBHOOK = "https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128" # Url de l'image de profile du webhook.

DELETE_TRIG_COMMAND = True # Défini si les messages contenant les commadnes doivent être éffacés.


bot = discord.Client()







def send_logs_private(content,title="Logs du serveur de FratLite",footer="Logs de M.A.R.I.O.N"):
    now = datetime.now()

    dt_string = now.strftime("%d/%m/%Y à %H:%M")

    webhook = DiscordWebhook(url="h")
    
    embed = DiscordEmbed(title=title, description=str(dt_string)+" "+str(content), color='FF0000')

    embed.set_footer(text=footer)

    webhook.add_embed(embed)
    try:
        response = webhook.execute()
        return log_event(str(dt_string)+" Envoie d'un message sur l'intra des Sapeurs Pompiers avec pour titre : "+str(title)+" pour contenu : \n"+str(content)+" et pour footer "+str(footer))

    except:
        return log_event(str(dt_string)+" Erreur lors de l'envoie d'un message sur l'intra des Sapeurs Pompiers avec pour titre : "+str(title)+" pour contenu : \n"+str(content)+" et pour footer "+str(footer))

def log_event(logs):
    print(logs)
    f = open("/home/pi/bot-sapeurs/logs.txt","a")
    f.write(logs+"\n")
    f.close()
    #journal.write(logs)
    data = {
    "content" : "",
    "username" : "Secrétaire du CSP",
    "avatar_url": URL_AVATAR_WEBHOOK
    }

    #leave this out if you dont want an embed
    #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    data["embeds"] = [
        {
            "description" : logs,
            "title" : "Logs de l'intranet du CSP",
            "color": 16711680
        }
    ]
    result = requests.post(WEBHOOK_LOGS, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Logs envoyé avec succès , code {}.".format(result.status_code))
    #send_logs_private(logs)

def push_worktime(agent,h,m):
    try:
        found = False
        today = datetime.today().strftime("%A")
        print(today)
        days = {"Monday":5,"Tuesday":6,"Wednesday":7,"Thursday":8,"Friday":9,"Saturday":10,"Sunday":11}
        scope = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
            ]
        file_name = '/home/pi/bot-sapeurs/client_key.json'
        hours = None
        creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
        client = gspread.authorize(creds)
        sheet = client.open('Suivi Heures').get_worksheet_by_id(2036745914)
        python_sheet = sheet.get_all_records()
        values = sheet.col_values(21)
        index = 0
        for col  in values:
            index += 1
            if str(agent) in col:
                found = True
                value_stored = sheet.cell(index,days[today]).value.split(":")
                hours = value_stored[0]
                hours = int(hours)+int(h)
                minutes = value_stored[1]
                minutes = int(minutes)+int(m)
                if hours < 10 :
                    hours = "0"+str(hours)
                if minutes < 10 :
                    minutes = "0"+str(minutes)
                sheet.update_cell(index,days[today],str(hours)+":"+str(minutes))
                log_event("Mise à jour du Google Sheets pour l'agent <@"+str(agent)+">")
                try:
                    os.system("rm /home/pi/bot-sapeurs/pds/"+str(agent)+'.json')
                    log_event("Suppression du timestamp de l'agent <@"+str(agent)+">")
                except Exception as e:
                    log_event("Echec de la suppression du timestamp de l'agent <@"+str(agent)+"> avec le code d'erreur suivant "+str(e))
                    return e
        if not found:
            log_event("Echec de la mise à jour du Google Sheets pour l'agent <@"+str(agent)+"> Code d'erreur : Agent introuvable")
            return "Agent Introuvable sur la feuille d'heure, merci de vérifier son enregistrement."
        else:
            return None           
    except Exception as e:
        log_event("Echec de la mise à jour du Google Sheets pour l'agent <@"+str(agent)+"> Code d'erreur "+str(e))
        return e
    
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(status=discord.Status.online,name=botstatus))
    print('Bot connecté au compte : {0.user}'.format(bot))
  
@bot.event
async def on_message(message):
    log_event("Message de "+str(message.author.display_name)+" dans le channel "+str(message.channel.name)+" : "+str(message.content))
    if not message.content == "" and message.author.id != bot.user.id :
        ##############################################################
        ############# Gestion des suppresions de messages ############
        ##############################################################
        for mot in MOTS_BANNIS:
            if  mot in message.content.lower():
                await message.delete()
                channel = bot.get_channel(message.channel.id)
                await channel.send("<@"+str(message.author.id)+"> Ton message à été supprimé car il contenait un mot interdit par la direction du CSP !")
        ##############################################################
        ############# Gestion des commandes de service ###############
        ##############################################################
        if message.content.lower() == str(PREFIX)+"pds": # Trigger de la pds si on trouve la commande
            if DELETE_TRIG_COMMAND:
                await message.delete()
            await _pds(message)
        elif message.content.lower() == str(PREFIX)+"fds": # Trigger de la fds si on trouve la commande
            if DELETE_TRIG_COMMAND:
                await message.delete()
            await _fds(message)
        ##############################################################
        ############# Gestion du service en automatique ##############
        ##############################################################
        if message.channel.id == 779715261665771546: 
            if "a commencer son service" in message.content :
                name = message.content.split("Le joueur ")[1]
                name = name.split(" a commencer son service")[0]
                log_event(f"Prise de service automatique détectée pour le joueur {name}, le module de prise en charge automatique des prises de service et en développement :wink:")
        if message.channel.id == 779715261665771546:
            if "a finit son service" in message.content :
                name = message.content.split("Le joueur ")[1]
                name = name.split(" a finit son service")[0]
                log_event(f"Fin de service automatique détectée pour le joueur {name}, le module de prise en charge automatique des fins de service est en développement :wink:")
        


async def _pds(ctx):
    if not ctx.guild or not ctx.guild.id == SERVEUR_ID:
        channel = bot.get_channel(message.channel.id)
        await channel.send("Cette commande est réservée au serveur de FratLite !")
    else:
        role = get(ctx.guild.roles, id = ROLE_SAPEURS)
        if False:
            await ctx.send("Vous n'êtes pas un membre du SAMU, vous ne pouvez utiliser cette commande !")
        else:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y à %H:%M")
            timestamp = time.time()
            emoji = get(ctx.guild.emojis, name="SamuFRaternity")
            data = {}
            data[ctx.author.id] =[]
            data[ctx.author.id].append({
                'timestamp' : str(timestamp),
                'date' : str(dt_string),
            })
            with open("/home/pi/bot-sapeurs/pds/"+str(ctx.author.id)+'.json', 'w') as outfile:
                json.dump(data, outfile)
            message = "Prise de service d'"+str(ctx.author.mention)+"\nHeure de prise de service : "+str(dt_string)
            embed = discord.Embed(
            title='Prise de service',
            description=message,
            color=discord.Color.red())
            embed.set_author(name="Secrétaire du CSP de FratLite",
            icon_url="https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128")
            channel = bot.get_channel(ctx.channel.id)
            await channel.send("<@"+str(ctx.author.id)+"> PDS enregistrée !")
            channel = bot.get_channel(CHANNEL_SERVICE)
            embed_send = await channel.send(embed=embed)
            await embed_send.add_reaction(EMOJI_SP)
            log_event(str(dt_string)+" Prise de service de <@"+str(ctx.author.id)+">")
            
async def _fds(ctx):
    if not ctx.guild or not ctx.guild.id == SERVEUR_ID:
        channel = bot.get_channel(message.channel.id)
        await channel.send("Cette commande est réservée au serveur de FratLite !")
    else:
        role = get(ctx.guild.roles, id = ROLE_SAPEURS)
        if False:
            await ctx.send("Vous n'êtes pas un membre du SAMU, vous ne pouvez utiliser cette commande !")
        else:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y à %H:%M")
            timestamp = time.time()
            emoji = get(ctx.guild.emojis, name="SamuFRaternity")
            with open ("/home/pi/bot-sapeurs/pds/"+str(ctx.author.id)+".json") as js_file:
                data =  json.load(js_file)
                for p in data:
                    i = data[p]
                    for x in i:
                        T = x['timestamp']
                        D = x['date']
                heures = ((timestamp - float(T)) / 60.0 )/60.0
                minutes = floor((heures % 1) * 60)
                heures = floor(heures)
                h2 = heures
                m2 = minutes
                if heures < 10:
                    heures = "0"+str(heures)
                if minutes < 10:
                    minutes = "0"+str(minutes)
                message = "Fin de service d'<@"+str(ctx.author.id)+"> \nPrise de service : "+str(D)+"\nFin de service :"+str(dt_string)+"\n\nTemps total de service : "+str(heures)+":"+str(minutes)
            embed = discord.Embed(
            title='Fin de service',
            description=message,
            color=discord.Color.red())
            embed.set_author(name="Secrétaire du CSP de FratLite",
            icon_url="https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128")
            channel = bot.get_channel(ctx.channel.id)
            await channel.send("<@"+str(ctx.author.id)+"> FDS enregistrée !")
            channel = bot.get_channel(CHANNEL_SERVICE)
            embed_send = await channel.send(embed=embed)
            await embed_send.add_reaction(EMOJI_SP)
            log_event(str(dt_string)+" Fin de service de <@"+str(ctx.author.id)+">")
            raise_work = push_worktime(ctx.author.id,h2,m2)
            if raise_work == None:
                await channel.send("Google Sheets mis à jour !")
            else:
                await channel.send("Le Google Sheet n'as pas été mis à jour à cause de l'erreur suivante "+str(raise_work))
bot.run(TOKEN)