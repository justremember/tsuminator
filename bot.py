"""
TODO:
    customize help screen
    add option to schedule tsume
    segmentize tsume solution
"""
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import random
import csv
from github import Github
import itertools
import io
import re

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
QBANK_LINK = os.getenv("QBANK_LINK")
bot = commands.Bot(command_prefix='$', activity=discord.Game('$help | Please message Carl#7846 for support'))
bot.remove_command('help')

allTsumes = []
tsumeSorted = {'1': [], '3': [], '5': [], '7': []}

g = Github(GITHUB_TOKEN)
qbankRepo = g.get_repo(QBANK_LINK)

def download_file_from_github(pathToFile):
    print(pathToFile)
    return qbankRepo.get_contents(pathToFile).decoded_content

tsumeLengths = {
        'https://www.shogitown.com/beginner/1tetume/1tetume.html':'1',
        'https://www.shogitown.com/beginner/tume/tume.html':'3',
        'https://www.shogitown.com/beginner/5te_2004/5te_tume.html': '5'
        }

# load tsumes from shogitown txt
jsonList = json.loads('[' + ','.join(open('links_shogitown.txt', 'r').readlines()) + ']')
for jsonObj in jsonList:
    tsumeLength = tsumeLengths[jsonObj['source']]
    jsonObj['te'] = tsumeLength

# load tsumes from qbank
pathToCsv = 'tsuminaref/reference.csv'
response = download_file_from_github(pathToCsv)
qbankCsv = csv.DictReader(response.decode('utf-8').splitlines(), delimiter='\t')
qbankList = []
for row in qbankCsv:
    row['filename_new_q'] = row['filename_new_q'].replace('png', 'jpg')
    row['filename_new_a'] = row['filename_new_a'].replace('png', 'jpg')
    row['questionGithub'] = 'tsuminator/question_bank/' + row['filename_new_q']
    row['answerGithub'] = 'tsuminator/question_bank/' + row['filename_new_a']
    qbankList.append(row)

index = 0
for jsonObj in itertools.chain(jsonList, qbankList):
    allTsumes.append(jsonObj)
    jsonObj['index'] = index
    tsumeSorted[jsonObj['te']].append(jsonObj)
    index += 1


@bot.command()
async def tsume(ctx, *args):
    """"""
    if len(args) > 0:
        matcher = re.match(r'^(\d*)-(\d*)$', args[0])
        if matcher:
            lower = int(matcher[1])
            upper = int(matcher[2])
    if len(args) == 0 or args[0].replace('te', '') in tsumeSorted.keys() or (matcher and lower <= upper):
        if len(args):
            te = args[0].replace('te', '')
            if matcher:
                tsumeLists = []
                for i in tsumeSorted:
                    if lower <= int(i) and int(i) <= upper:
                        tsumeLists.append(tsumeSorted[i])
                randomTsume = random.choice(random.choices(tsumeLists, weights=map(len, tsumeLists))[0])
            else:
                randomTsumeNum = random.randint(0, len(tsumeSorted[te])-1)
                randomTsume = tsumeSorted[te][randomTsumeNum]
        else:
            randomTsumeNum = random.randint(0, len(allTsumes)-1)
            randomTsume = allTsumes[randomTsumeNum]
        embed = discord.Embed(
                title='Random Tsume #%s' % randomTsume['index'],
                description='%ste. To get the answer type `$answer %i`' % (randomTsume['te'], randomTsume['index']) ,
                color=0x00ff00)
        if randomTsume.get('question'):
            embed.set_image(url=randomTsume['question'])
            await ctx.send(embed=embed)
        else:
            imgBin = download_file_from_github(randomTsume['questionGithub'])
            imgObj = io.BytesIO(imgBin)
            imgFile = discord.File(imgObj, filename=randomTsume['filename_new_q'])
            embed.set_image(url='attachment://' + randomTsume['filename_new_q'])
            await ctx.send(file=imgFile, embed=embed)

@bot.command()
async def answer(ctx, arg:int):
    if arg >= 0 and arg < len(allTsumes):
        currTsume = allTsumes[arg]
        if currTsume.get('answer'):
            await ctx.send('Solution to tsume #%s: ||%s||' % (arg, currTsume['answer']))
        else:
            imgBin = download_file_from_github(currTsume['answerGithub'])
            imgObj = io.BytesIO(imgBin)
            imgFile = discord.File(imgObj, filename='SPOILER_' + currTsume['filename_new_a'])
            # embed.set_image(url='attachment://' + currTsume['answerGithub'])
            await ctx.send('Solution to tsume #%s (click to show spoiler)' % arg, file=imgFile)


@bot.command()
async def pat(ctx):
    embed = discord.Embed(
        title='Thanks.',
        color=0xFF7F7F)
    embed.set_image(url="https://cdn.discordapp.com/attachments/681810172876029974/792596784413278208/lklk.png")
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
            colour = discord.Colour.orange()
            )
    embed.set_author(name='Tsuminator Help')
    embed.add_field(name='$tsume', value='Get random tsume. Sample arguments: 3te, 1te, 5, 3-7, or no argument. Currently available tsumes are from 1te to 7te.', inline=False)
    embed.add_field(name='$answer', value='Get answer to a tsume. Takes a tsume # as argument.', inline=False)
    embed.add_field(name='$help', value='Shows this help message.', inline=False)
    embed.add_field(name='What is tsume?', value='Tsumeshogi are checkmate problems in shogi. More info: http://www.shogi.net/nexus/ladder/help.html', inline=False)


    await ctx.send(embed=embed)



# simple http server for pings

import threading

def serve():
    import http.server
    import socketserver
    from http import HTTPStatus

    PORT = int(os.getenv("PORT") or 8080)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(b'Tsuminator is up')
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

thr = threading.Thread(target=serve, name='Http')
thr.start()


bot.run(DISCORD_TOKEN)
