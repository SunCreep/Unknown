from typing import Type
import discord
from discord import channel
from loguru import logger
import random
import os
import requests
import io
import sys
import asyncio
import datetime
import re
from pathlib import Path
from discord.ext import commands
import json
import collections
import pickle

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = Path('D:\\Sripts\\Unknown\\logs.log')
ERROR_LOG_FILE = Path('D:\\Sripts\\Unknown\\errors.log')
LOGURU_FORMAT = '<light-magenta>{time:x}</light-magenta> | <light-black>{time:DD.MM.YYYY at HH:mm:ss}</light-black> | <level>{level}</level> | <light-white>{message}</light-white>'
logger.remove()
logger.add(sys.stderr, format=LOGURU_FORMAT, level="DEBUG")
logger.add(LOG_FILE, format=LOGURU_FORMAT, level='DEBUG',  mode='w')
logger.add(ERROR_LOG_FILE, format=LOGURU_FORMAT, level='ERROR', mode='a')
logger.info('Imports initialized. Logging initialized.')

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '.', help_command=None, intents=intents)

@client.event
async def on_ready(): 
    print('Bot is ready.')


dir_list = ['D:\\Sripts\\Unknown\\', 'D:\\Sripts\\Unknown\\players\\', 'D:\\Sripts\\Unknown\\languages\\']


class Player:
    def __init__(self, id, lang, hero, channel, location, questid, quest, gold, party_id, party_channel):
        self.id = id #id игрока в игре - равен id usera
        self.lang = lang #язык который игрок использует
        # 0 - eng, 1 - rus
        self.hero = hero # обьект героя игрока
        self.channel = channel # канал, в котором играет игрок
        self.location = location # место где сейчас находится игрок
        self.questid = questid # номер квеста игрока
        self.quest = quest # обьект квеста который сейчас у игрока
        self.gold = gold # деньги игрока
        self.party_id = party_id # ID пати игрока
        self.party_channel = party_channel # канал пати игрока
    
            #hero = Hero(args,0,1,100,10,15,3,5,None,None,None,None,None,None)
class Hero:
    def __init__(self, name, exp, lvl, hp, mana, dmg, arm, eva, spells, har, slots, backpack, race, gender):
        self.name = name #имя героя
        self.exp = exp #уровень героя
        self.lvl = lvl #уровень героя
        self.hp = hp #здоровье героя + предмета
        self.mana = mana #мана героя + предмета
        self.dmg = dmg #урон героя + предмета
        self.arm = arm #защита героя + предмета
        self.eva = eva #уклонение героя + предмета
        self.spells = spells #абилки героя + предмета
        self.har = har #атрибуты героя + предмета
        self.slots = slots #активные слоты героя
        self.backpack = backpack #рюкзак героя с некактивными вещами
        self.race = race #расса героя 
        self.gender = gender #гендер героя

class Item:
    def __init__(self, name, dmg, arm, eva, hp, spells, har):
        self.name = name #имя предмета
        self.dmg = dmg #урон предмета
        self.arm = arm #защита предмета
        self.eva = eva #уклонение предмета
        self.hp = hp #здоровье предмета
        self.spells = spells #абилки предмета
        self.har = har #атрибуты предмета

#подсасывает из дб обьекты игроков и имен героев
all_heroes_names = []
players_data = {}
if len(os.listdir(dir_list[1]))>0:
    for player_file in os.listdir(dir_list[1]):
        with open(dir_list[1]+player_file, 'rb') as file:
            player = pickle.load(file)
            players_data[player.id] = player
    with open('D:\\Sripts\\Unknown\\hero_names', 'rb') as file:
        all_heroes_names = pickle.load(file)

#игрок=>герой=>характиристики+рюкзак+слоты+=>итемы=>атрибуты
#игрок имеет 1-3 героя
#герои имеет характиристики, слоты предметов, рюкзак
#слоты хранят активыне предметы
#рюкзак хранит неактивные предметы
#характиристики предмета переходят к герою
#а атрибуты героя характирузуют его в игре
#
{'id':{'id':'','lang':'',"hero_id":{"hero_id":'', "player_id":''}}}

#создает файлы языков для перевода
languges_help = []
languges_list = []
for language in os.listdir(dir_list[2]):
    languges_help.append(language.replace('.json',''))
    with open(dir_list[2]+language, encoding='utf8') as json_file:
        lang_dic = json.load(json_file)
        languges_list.append(lang_dic)



#функция, которая сейвит игрока в отдельный json файл
async def player_saver(player_id, player):
    with open(dir_list[1]+str(player_id), 'wb') as outfile:
        pickle.dump(player, outfile)
    players_data[player.id] = player


list_of_welcomes=[884286622059864114,884298098321535046]
#Инициализация нового игрока, создает обьект игрока и канал в котором он играет. 
#При выходе с сервера обьект игрока не страдает, т.к. в нем хранятся данные об обьекте героя.
#Игроки с долгим перерывом будут удаляться, т.к. доступно только порядка 450 игроков одновременно. 
#Но их герои и прогресс будут сохраняться навсегда.
@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if (str(payload.emoji) == '☑️') and (message.id in list_of_welcomes):
        if message.id == 884298098321535046:
            lang = 1
        elif message.id == 884286622059864114:
            lang = 0
        user = await client.fetch_user(payload.user_id)
        guild = client.get_guild(882580817983963197)
        role = guild.default_role
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        channel = await guild.create_text_channel('My Adventure', overwrites=overwrites)
        new=True
        if user.id not in players_data.keys():
            hero = []
            player = Player(user.id, lang, hero, channel.id, None, None, None, None, None, None)
        else:
            new=False
            player = players_data[user.id]
            player.channel = channel.id
            loc_channel = discord.utils.get(guild.channels, name=locsChannels[player.location])
            await loc_channel.set_permissions(user, view_channel=True, read_messages=True, send_messages=True)
            loc_voice_channel = discord.utils.get(guild.channels, name=locsVoiceChannels[player.location])
            await loc_voice_channel.set_permissions(user, view_channel=True, read_messages=True, send_messages=True)
        players_data[user.id] = player
        await player_saver(user.id, player)
        language = languges_list[player.lang]
        await channel.edit(name=language["3"])
        await channel.set_permissions(role, view_channel=False)
        await channel.set_permissions(user, view_channel=True, read_messages=True, send_messages=True)
        category = discord.utils.get(guild.channels, name="Adventures")
        await channel.edit(category=category)
        language = languges_list[player.lang]
        if new == True:
            await channel.send(language["1"])
            await channel.send(language["7"])
        elif new == False:
            await channel.send(language["29"])
            tmp=languges_list[player.lang]["23"][player.location]
            await channel.send(languges_list[player.lang]["28"]+"**"+tmp+"**")

#Тут происходит удаление канала при покидании игроком сервера, 
#Не зависимо был он удален админом, инактивом или вышел сам.
@client.event
async def on_member_remove(member):
    player = players_data[member.id]
    channel = client.get_channel(player.channel)
    await channel.delete()
    player.channel = None  #замена переменной канала игрока
    await player_saver(member.id, player)

#Команда показывающая и меняющая доступные языки перевода
@client.command(aliases=['lang'])
async def language(ctx, args=None):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    if args==None:
        em = discord.Embed(title = language["2"], description = '\n'.join(languges_help), color=ctx.author.color)
        await ctx.send(embed = em)
    else:
        if (args in languges_help) and (player.lang != languges_help.index(args)):
            player.lang = languges_help.index(args) #Замена переменной языка игрока
            await player_saver(player.id, player)
            language = languges_list[player.lang]
            await channel.send(language["6"])
            await channel.edit(name=language["3"])
        elif args not in languges_help:
            await channel.send(language["17"])
            em = discord.Embed(title = language["2"], description = '\n'.join(languges_help), color=ctx.author.color)
            await ctx.send(embed = em)
        else:
            await channel.send(language["18"])

#команда показывающая доступные не игровые команды
@client.command()
async def help(ctx):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    em = discord.Embed(title = language["4"], description = language["5"], color=ctx.author.color)
    await channel.send(embed = em)

forbidden_hero_names = ['.','@',"#","/"]
#создает героя, в аргс принимает имя нового героя
#максимум 3 героя на игрока, именя не повторяются и не содержат плохих симвалов 
@client.command()
async def create_hero(ctx, args):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    for name in forbidden_hero_names:
        if (name in args) or (args in name):
            return await channel.send(language["21"])
    if args in all_heroes_names:
        return await channel.send(language["22"])
    if len(player.hero) < 3:
        all_heroes_names.append(args)
        with open(dir_list[0]+'hero_names', 'wb') as outfile:
            pickle.dump(all_heroes_names, outfile)
        await channel.send(language["8"]+args+'!')
        hero = Hero(args,0,1,100,10,15,3,5,None,None,None,None,None,None)
        player.hero.append(hero)
        await player_saver(player.id, player)
        await channel.send(language["10"])
        await channel.send(language["9"])
    elif len(player.hero) >= 3:
        await channel.send(language["20"])

#команда смерти/удаление героя
@client.command()
async def kick_hero(ctx, args):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    if len(player.hero)>=1:
        for heroObj in player.hero:
            if heroObj.name == args:
                player.hero.remove(heroObj)
                all_heroes_names.remove(args)
                await player_saver(player.id, player)
                with open(dir_list[0]+'hero_names', 'wb') as outfile:
                    pickle.dump(all_heroes_names, outfile)
                await channel.send(language["24"])
    else:
        await channel.send(language["25"])

#выводит мини статы всех героев
@client.command()
async def stats(ctx):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    if len(player.hero) > 0:
        stat = ''
        itemlist = ["name",'hp','dmg','mana']
        for heroes in player.hero:
            for k,v in heroes.__dict__.items():
                if k in itemlist:
                    stat = stat+'**'+str(k)+'**: '+str(v)+'\n'
            stat = stat+'======================================'+'\n'
        for k,v in language["13"].items():
            stat = stat.replace(k, v)
        stat = stat.replace('None', language["12"])
        em = discord.Embed(title = language["11"], description = stat, color=ctx.author.color)
        await channel.send(embed = em)
    elif len(player.hero) == 0:
        await channel.send(language["19"])

#выводит статы всех героев
@client.command()
async def full_stats(ctx):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    if len(player.hero) > 0:
        stat = ''
        for heroes in player.hero:
            for k,v in heroes.__dict__.items():
                stat = stat+'**'+str(k)+'**: '+str(v)+'\n'
            stat = stat+'======================================'+'\n'
        for k,v in language["13"].items():
            stat = stat.replace(k, v)
        stat = stat.replace('None', language["12"])
        em = discord.Embed(title = language["11"], description = stat, color=ctx.author.color)
        await channel.send(embed = em)
    elif len(player.hero) == 0:
        await channel.send(language["19"])

#список всех цветов в формате меншена
colors_mentions = [
'<@&884490761188573184>',
'<@&884477545507078195>',
'<@&884484307731775559>',
'<@&884484631842394133>',
'<@&884488750506332242>',
'<@&884490418060926978>',
'<@&884485089688424448>',
'<@&884487789612257321>',
'<@&884490168688594946>',
'<@&884490317091463188>',
'<@&884488243456933899>',
'<@&884488302382678016>',
'<@&884489474116038677>',
'<@&884489408403877899>',
'<@&884488845700251690>']

#функция вывода и смены цветов, показывает какие они есть на сервере
@client.command()
async def color(ctx, args=None):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    guild = client.get_guild(882580817983963197)
    if args == None:
        desc = '\n'.join(colors_mentions)
        em = discord.Embed(title = language["16"], description = desc, color=ctx.author.color)
        await channel.send(embed = em)
    else:
        if (ctx.channel == channel) and (args in colors_mentions):
            role_id = args.replace('<@&','')
            role_id = role_id.replace('>','')
            role = discord.utils.get(guild.roles, id=int(role_id))
            roles = ''.join(str(ctx.author.roles))
            if role_id not in roles:
                for x in ctx.author.roles:
                    if ('<@&'+str(x.id)+'>') in colors_mentions:
                        await ctx.message.author.remove_roles(x)
                await ctx.message.author.add_roles(role)
                await channel.send(language["14"]+args)
            else:
                await channel.send(language["15"]+args)
        elif args not in colors_mentions:
            await channel.send(language["17"])

locsVoiceChannels = {
    "1":"City Streets",
    "2":"Sabertusk Tavern"
}
locsChannels = {
    "1":"city-streets",
    "2":"sabertusk-tavern"
}

#функция перехода в другое место, выше список локаций-каналов 
@client.command()
async def go_to(ctx, arg=None):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    locs = language["23"]
    if arg==None:
        locsString = ''
        for k,v in locs.items():
            locsString = locsString+'**'+str(k)+'**: '+str(v)+'\n'
        em = discord.Embed(title = language["26"], description = locsString, color=ctx.author.color)
        await channel.send(embed = em)
    else:
        if arg in locs.keys():
            if player.location != arg:
                player.location = arg
                await player_saver(player.id, player)
                user = await client.fetch_user(player.id)
                loc_channel = discord.utils.get(ctx.guild.channels, name=locsChannels[arg])
                loc_voice_channel = discord.utils.get(ctx.guild.channels, name=locsVoiceChannels[arg])
                for channels in locsChannels.values():
                    tmpChannel = discord.utils.get(ctx.guild.channels, name=channels)
                    await tmpChannel.set_permissions(user, view_channel=False, read_messages=False, send_messages=False)
                for channels in locsVoiceChannels.values():
                    tmpChannel = discord.utils.get(ctx.guild.channels, name=channels)
                    await tmpChannel.set_permissions(user, view_channel=False, read_messages=False, send_messages=False)
                await loc_channel.set_permissions(user, view_channel=True, read_messages=True, send_messages=True)
                await loc_voice_channel.set_permissions(user, view_channel=True, read_messages=True, send_messages=True)
                await channel.send(language["27"]+"**"+locs[player.location]+"**")
            elif player.location == arg:
                await channel.send(language["30"])

#подсказывает юзеру где тот сейчас находится
@client.command()
async def whereami(ctx):
    player = players_data[ctx.author.id]
    language = languges_list[player.lang]
    channel = client.get_channel(player.channel)
    tmp=language["23"][player.location]
    await channel.send(language["28"]+"**"+tmp+"**")


#разрешить ввод и вывод всех команд только в своем или пати чате 

#добавить систему сбора пати и пати чатов
#добавить установку характеристик, выбор старотового инвентаря, рассы, пола для героев

#Нужно добавить адекватный логгинг всех действий!
#использовать для сценария известные днд сессии


with open('D:\\Sripts\\Unknown\\Unknown.property.json', encoding='utf8') as json_file:
    property = json.load(json_file)
    client.run(property['api-key'])