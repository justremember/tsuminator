import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import random

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix='$')

allTsumes = []
tsumeSorted = {'1te': [], '3te': [], '5te': []}

tsumeLengths = {
        'https://www.shogitown.com/beginner/1tetume/1tetume.html':'1te',
        'https://www.shogitown.com/beginner/tume/tume.html':'3te',
        'https://www.shogitown.com/beginner/5te_2004/5te_tume.html': '5te'
        }

# load tsumes from shogitown txt
jsonList = json.loads('[' + ','.join(open('links_shogitown.txt', 'r').readlines()) + ']')
for jsonObj in jsonList:
    tsumeLength = tsumeLengths[jsonObj['source']]
    jsonObj['tsumeLength'] = tsumeLength
    tsumeSorted[tsumeLength].append(jsonObj)

index = 0
for jsonObj in jsonList:
    allTsumes.append(jsonObj)
    jsonObj['index'] = index
    index += 1

    

@bot.command()
async def tsume(ctx, *args):
    """Get random tsume."""
    if len(args) == 0 or arg[0] in tsumeSorted.keys():
        if len(args):
            randomTsumeNum = random.randint(0, len(tsumeSorted[arg[0]])-1)
            randomTsume = tsumeSorted[arg[0]][randomTsumeNum]
        else:
            randomTsumeNum = random.randint(0, len(allTsumes)-1)
            randomTsume = allTsumes[randomTsumeNum]
        embed = discord.Embed(
                title='Random Tsume #%s' % randomTsume['index'],
                description='%s. To get the answer type `$answer %i`' % (randomTsume['tsumeLength'], randomTsume['index']) ,
                color=0x00ff00)
        embed.set_image(url=randomTsume['question'])
        await ctx.send(embed=embed)

@bot.command()
async def answer(ctx, arg:int):
    """Get answer to a tsume."""
    await ctx.send('Solution to tsume #%s: ||%s||' % (arg, allTsumes[arg]['answer']))
    await ctx.send(embed=embed)


bot.run(DISCORD_TOKEN)
