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

class Rule:
    def __init__(self, raw_rule):
        self.regex = re.compile(raw_rule['match_value'])
        self.tags = raw_rule['tags']

    def process(self, msg):
        if self.regex.match(msg) :
            tag = random_select(self.tags)
            print('   responding with tag', tag)
            return get_semirandom_gif(tag)
            
rules = None
with open('config.json') as config_file :
    raw_rules = json.load(config_file)['rules']
    rules = [Rule(x) for x in raw_rules]

print('Rules: ',rules)
def process_message(text) :
    print('Processing message "%s"'%text)
    for rule in rules :
        response = rule.process(text)
        if response :
            return response
    print('   no match found in rules. Staying silent...')
    return None

#process_message('!solved')
#process_message('That looks like coppersmith')
#process_message('What?')

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):

        print('Message from {0.author}: {0.content}'.format(message))
        if message.author.bot :
            print('   ignoring message from bot.')
            return

        response = process_message(message.content)
        print('Responding with ',response)
        if response :
            result = await message.channel.send(response)
             
client = MyClient()
client.run(discord_bot_token)
