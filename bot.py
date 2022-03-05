import discord
from discord import Member
from discord import FFmpegPCMAudio
from discord_slash import SlashCommand 
import time 
from discord.ext import commands
from datetime import datetime
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord.utils import get
from discord_slash.utils.manage_components import wait_for_component
from systemd import journal
from random import randint
import requests
import json
from math import floor 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from datetime import datetime as date
import os 
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType
from discord_webhook import DiscordWebhook, DiscordEmbed
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
import sqlite3
TOKEN =  ""
list_status=["s'occupe de l'administratif"]

botstatus = list_status[randint(0,len(list_status)-1)]

bot = discord.Client( intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

SERVEUR_ID = 779715258545078282 # ID du serveur
WEBHOOK_LOGS = ""
CHANNEL_SERVICE = 925232806941048882
ROLE_SAPEURS = 791275596830867457
EMOJI_PROMOTION = 'spfrat'
EMOJI_DECES = 'spfrat'

MOTS_BANNIS = ["nitro","everyone","here"]
def send_logs_private(content,title="Logs du serveur de FratLite",footer="Logs de M.A.R.I.O.N"):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y à %H:%M")
    webhook = DiscordWebhook(url="h")
    
    embed = DiscordEmbed(title=title, description=str(dt_string)+" "+str(content), color='FF0000')

    embed.set_footer(text=footer)

    webhook.add_embed(embed)
    try:
        response = webhook.execute()
        #return log_event(str(dt_string)+" Envoie d'un message sur l'intra des Sapeurs Pompiers avec pour titre : "+str(title)+" pour contenu : \n"+str(content)+" et pour footer "+str(footer))

    except:
        pass
        #return log_event(str(dt_string)+" Erreur lors de l'envoie d'un message sur l'intra des Sapeurs Pompiers avec pour titre : "+str(title)+" pour contenu : \n"+str(content)+" et pour footer "+str(footer))

def log_event(logs):
    f = open("/home/pi/bot-sapeurs/logs.txt","a")
    f.write(logs+"\n")
    f.close()
    journal.write(logs)
    data = {
    "content" : "",
    "username" : "Secrétaire du CSP",
    "avatar_url": "https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128"
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
    send_logs_private(logs)

def push_worktime(agent,h,m):
    try:
        found = False
        today = date.today().strftime("%A")
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
                except:
                    log_event("Echec de la suppression du timestamp de l'agent <@"+str(agent)+">")
        if not found:
            print("Echec de la mise à jour du Google Sheets pour l'agent <@"+str(agent)+"> Code d'erreur : Agent introuvable")
            log_event("Echec de la mise à jour du Google Sheets pour l'agent <@"+str(agent)+"> Code d'erreur : Agent introuvable")           
    except Exception as e:
        print("Echec de la mise à jour du Google Sheets pour l'agent <@"+str(agent)+"> Code d'erreur "+str(e))
        log_event("Echec de la mise à jour du Google Sheets pour l'agent <@"+str(agent)+"> Code d'erreur "+str(e))
    
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(status=discord.Status.offline,name=botstatus))
    print('Bot connecté au compte : {0.user}'.format(bot))
    journal.write('Bot connecté au compte : {0.user}'.format(bot))
    text_channel_list = []
    for guild in bot.guilds:
        for channel in guild.text_channels:
            text_channel_list.append(channel)
            print(str(channel.name)+str(channel.id))
    message = "Bonsoir à toutes et tous, je suis au regret de vous annoncer la désactivation du secrétaire de gestion des temps de service du CSP\n\nEn effet à partir de ce soir vous perdrez l'accès aux commandes suivantes\n```/pds``` ```/fds```\n\nCe bot est fait de mes mains et autohéberger sur mon serveur personnel des suites d'evenement liés aux staffs du serveur j'arrête donc de m'investir.\n\n L'intégralité du code source sera remis au commandant, libre à lui de s'en servir ou de le jeter.\n\n je vous souhaites à toutes et tous un bon RP et une bonne santé\n\nUn codeur parmi tant d'autres."
    embed = discord.Embed(
    title='Arrêt du secrétaire de gestion des temps de service',
    description=message,
    color=discord.Color.red())
    embed.set_author(name="Secrétaire du CSP de FratLite",
    icon_url="https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128")
    try:
        channel = bot.get_channel(925232806941048882)
        #await channel.send(embed=embed)
        #print("MESSAGE DE DESACTIVATION ENVOYE !")
    except Exception as Error:
        print("Une erreur s'est produite : "+str(Error))
    
@bot.event
async def on_message(message):
    print("Message de "+str(message.author.display_name)+" dans le channel "+str(message.channel.name)+" : "+str(message.content))
    if not message.content  == "":
        print("Message de "+str(message.author.display_name)+" dans le channel "+str(message.channel.name)+" : "+str(message.content))
        send_logs_private("Message de "+str(message.author.display_name)+" dans le channel "+str(message.channel.name)+" : "+str(message.content))
        for mot in MOTS_BANNIS:
            if  mot in message.content.lower():
                await message.delete()
                channel = bot.get_channel(message.channel.id)
                await channel.send("<@"+str(message.author.id)+"> Ton message à été supprimé car il contenait un mot interdit par la direction du CSP !")
        if message.channel.id == 779715261665771546: 
            if "a commencer son service" in message.content :
                name = message.content.split("Le joueur ")[1]
                name = name.split(" a commencer son service")[0]
                print(f"Prise de service automatique détectée pour le joueur {name}, le module de prise en charge automatique des prises de service et en développement :wink:")
                log_event(f"Prise de service automatique détectée pour le joueur {name}, le module de prise en charge automatique des prises de service et en développement :wink:")
        if message.channel.id == 779715261665771546:
            if "a finit son service" in message.content :
                name = message.content.split("Le joueur ")[1]
                name = name.split(" a finit son service")[0]
                print(f"Prise de service automatique détectée pour le joueur {name}, le module de prise en charge automatique des fins de service est en développement :wink:")
                log_event(f"Fin de service automatique détectée pour le joueur {name}, le module de prise en charge automatique des fins de service est en développement :wink:")

@slash.slash(name="pds", description="Prendre son service")
async def _pds(ctx):
    await ctx.defer(hidden=False)
    message = "Bonsoir à toutes et tous, je suis au regret de vous annoncer la désactivation du secrétaire de gestion des temps de service du CSP\n\nEn effet à partir de ce soir vous perdrez l'accès aux commandes suivantes\n```/pds``` ```/fds```\n\nCe bot est fait de mes mains et autohéberger sur mon serveur personnel des suites d'evenement liés aux staffs du serveur j'arrête donc de m'investir.\n\n L'intégralité du code source sera remis au commandant, libre à lui de s'en servir ou de le jeter.\n\n je vous souhaites à toutes et tous un bon RP et une bonne santé\n\nUn codeur parmi tant d'autres."
    embed = discord.Embed(
    title='Arrêt du secrétaire de gestion des temps de service',
    description=message,
    color=discord.Color.red())
    embed.set_author(name="Secrétaire du CSP de FratLite",
    icon_url="https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128")
    await ctx.send(ctx.author.mention,embed=embed)
    # if not ctx.guild or not ctx.guild.id == SERVEUR_ID:
    #     await ctx.send("Cette commande est réservée au serveur de FratLite !")
    # else:
    #     role = get(ctx.guild.roles, id = ROLE_SAPEURS)
    #     if False:
    #         await ctx.send("Vous n'êtes pas un membre du SAMU, vous ne pouvez utiliser cette commande !")
    #     else:
    #         now = datetime.now()
    #         dt_string = now.strftime("%d/%m/%Y à %H:%M")
    #         timestamp = time.time()
    #         emoji = get(ctx.guild.emojis, name="SamuFRaternity")
    #         data = {}
    #         data[ctx.author.id] =[]
    #         data[ctx.author.id].append({
    #             'timestamp' : str(timestamp),
    #             'date' : str(dt_string),
    #         })
    #         with open("/home/pi/bot-sapeurs/pds/"+str(ctx.author.id)+'.json', 'w') as outfile:
    #             json.dump(data, outfile)
    #         message = "Prise de service d'"+str(ctx.author.mention)+"\nHeure de prise de service : "+str(dt_string)
    #         embed = discord.Embed(
    #         title='Prise de service',
    #         description=message,
    #         color=discord.Color.red())
    #         embed.set_author(name="Secrétaire du CSP de FratLite",
    #         icon_url="https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128")
    #         await ctx.send("PDS enregistrée !",hidden=True)
    #         channel = bot.get_channel(CHANNEL_SERVICE)
    #         embed_send = await channel.send(embed=embed)
    #         emoji = get(ctx.guild.emojis, name=EMOJI_PROMOTION)
    #         await embed_send.add_reaction(emoji)
    #         log_event(str(dt_string)+" Prise de service de <@"+str(ctx.author.id)+">")
            
@slash.slash(name="fds", description="Prendre sa fin service")
async def _fds(ctx):
    await ctx.defer(hidden=False)
    message = "Bonsoir à toutes et tous, je suis au regret de vous annoncer la désactivation du secrétaire de gestion des temps de service du CSP\n\nEn effet à partir de ce soir vous perdrez l'accès aux commandes suivantes\n```/pds``` ```/fds```\n\nCe bot est fait de mes mains et autohéberger sur mon serveur personnel des suites d'evenement liés aux staffs du serveur j'arrête donc de m'investir.\n\n L'intégralité du code source sera remis au commandant, libre à lui de s'en servir ou de le jeter.\n\n je vous souhaites à toutes et tous un bon RP et une bonne santé\n\nUn codeur parmi tant d'autres."
    embed = discord.Embed(
    title='Arrêt du secrétaire de gestion des temps de service',
    description=message,
    color=discord.Color.red())
    embed.set_author(name="Secrétaire du CSP de FratLite",
    icon_url="https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128")
    await ctx.send(ctx.author.mention,embed=embed)
    # if not ctx.guild or not ctx.guild.id == SERVEUR_ID:
    #     await ctx.send("Cette commande est réservée au serveur de FratLite !")
    # else:
    #     role = get(ctx.guild.roles, id = ROLE_SAPEURS)
    #     if False:
    #         await ctx.send("Vous n'êtes pas un membre du SAMU, vous ne pouvez utiliser cette commande !")
    #     else:
    #         now = datetime.now()
    #         dt_string = now.strftime("%d/%m/%Y à %H:%M")
    #         timestamp = time.time()
    #         emoji = get(ctx.guild.emojis, name="SamuFRaternity")
    #         with open ("/home/pi/bot-sapeurs/pds/"+str(ctx.author.id)+".json") as js_file:
    #             data =  json.load(js_file)
    #             for p in data:
    #                 i = data[p]
    #                 for x in i:
    #                     T = x['timestamp']
    #                     D = x['date']
    #             heures = ((timestamp - float(T)) / 60.0 )/60.0
    #             minutes = floor((heures % 1) * 60)
    #             heures = floor(heures)
    #             h2 = heures
    #             m2 = minutes
    #             if heures < 10:
    #                 heures = "0"+str(heures)
    #             if minutes < 10:
    #                 minutes = "0"+str(minutes)
    #             message = "Fin de service d'<@"+str(ctx.author.id)+"> \nPrise de service : "+str(D)+"\nFin de service :"+str(dt_string)+"\n\nTemps total de service : "+str(heures)+":"+str(minutes)
    #         embed = discord.Embed(
    #         title='Fin de service',
    #         description=message,
    #         color=discord.Color.red())
    #         embed.set_author(name="Secrétaire du CSP de FratLite",
    #         icon_url="https://cdn.discordapp.com/avatars/929423911232372756/2c489781c793afd9545f18d9ccf40b94.webp?size=128")
    #         await ctx.send("FDS enregistrée !",hidden=True)
    #         channel = bot.get_channel(CHANNEL_SERVICE)
    #         embed_send = await channel.send(embed=embed)
    #         emoji = get(ctx.guild.emojis, name=EMOJI_PROMOTION)
    #         await embed_send.add_reaction(emoji)
    #         log_event(str(dt_string)+" Fin de service de <@"+str(ctx.author.id)+">")
    #         push_worktime(ctx.author.id,h2,m2)
    #         await channel.send("Google Sheets mis à jour !")

 
bot.run(TOKEN)