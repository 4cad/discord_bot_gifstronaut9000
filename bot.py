import discord
from discord.ext import commands

from secret import giphy_key, discord_bot_name, discord_bot_token

import re
import json
import requests
import urllib.parse
import random

def print_debug_info(r) :    
    print('  url    = ',r.url)
    print('  status = ',r.status_code)
    print('  text   = ',r.text)

def get_random_gif(tag) :
    test_url = 'https://api.giphy.com/v1/gifs/random?api_key=%s&rating=pg-13&tag=%s'%(giphy_key, urllib.parse.quote(tag))
    r = requests.get(test_url)

    if r.status_code != 200 :
        print('Unable to fetch GIF for some reason.')
        print('  url    = ',r.url)
        print('  status = ',r.status_code)
        print('  text   = ',r.text)
        return None
    
    response =  json.loads(r.text)
    return response['data']['url']

def get_semirandom_gif(query) :
    offset = random.randint(0, 200)
    search_url = 'https://api.giphy.com/v1/gifs/search?api_key=%s&rating=pg-13&limit=1&q=%s&offset=%d'%(giphy_key, urllib.parse.quote(query), offset)
    r = requests.get(search_url)

    if r.status_code != 200 :
        print('Unable to fetch GIF for some reason.')
        print('  url    = ',r.url)
        print('  status = ',r.status_code)
        print('  text   = ',r.text)
        return None
    
    response =  json.loads(r.text)
    print(response)
    return response['data'][0]['url']

def canonical_name(name):
    cname = ""
    for char in name:
        if re.match("[A-Za-z0-9-+]", char):
            if len(cname) > 0 or char != "-":
                cname += char
    return cname

def permission_name(ctfname, challenge):
    ctfname = canonical_name(ctfname)
    challenge_name = canonical_name(challenge)
    permission = ctfname + "-" + challenge_name
    return permission

def find_role(roles, name):
    print("looking for", name)
    for role in roles:
        print(role.name)
        if role.name == name:
            return role

def random_select(x) :
    random.shuffle(x)
    return x[0]

async def make_role(guild, role_name):
    result = await guild.create_role(
        name=role_name, color=discord.Color(0xffff00))
    return result

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):

        print('Message from {0.author}: {0.content}'.format(message))
        if message.author.bot :
            print('   ignoring message from bot.')
            return

        if message.content.startswith("!gifme") :
            tag_m = re.findall("!gifme ([^ ]+)", message.content)
            if len(tag_m) < 1:
                return
            tag = tag_m[0]
            result = await message.channel.send(get_semirandom_gif(tag))
        elif (message.content.startswith('!solved') or message.content.startswith('!giftestsolve')) :
            tag = random_select(['win','celebrate','well done','awesome','excellent','woohoo'])
            print('Sending solved gif with tag "%s"'%tag)
            result = await message.channel.send(get_semirandom_gif(tag))
        elif 'coppersmith' in message.content.lower() :
            result = await message.channel.send(get_semirandom_gif('suspicious'))
        elif message.content.startswith("!help") :
            result = await message.channel.send("The lord helps those who help themselves.")
             
client = MyClient()
client.run(discord_bot_token)
