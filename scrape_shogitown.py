#Scrapes all tsumes from sites including shogitown and dumps it to links.txt.
#Meant to be run in local machine and not in deployment.
import asyncio
from pyppeteer import launch
from io import BytesIO
import json
import re

urls = [
        'https://www.shogitown.com/beginner/1tetume/1tetume.html',
        'https://www.shogitown.com/beginner/tume/tume.html',
        'https://www.shogitown.com/beginner/5te_2004/5te_tume.html'
        ]

blacklist = [
        'https://www.shogitown.com/index.html',
        'https://www.shogitown.com/beginner/top-b.html',
        'https://www.shogitown.com/beginner/1tetume/1tetume01.html',
        'https://www.shogitown.com/beginner/1tetume/1tetume.html',
        'https://www.shogitown.com/beginner/tume/tume.html',
        'https://www.shogitown.com/beginner/5te_2004/5te_tume.html'
        ]

# if program freezes or stops for any reason, copy the last printed url and put it here, & run the program again.
last = ''

async def scrape_shogitown():
    willSkip = True

    if not last:
        willSkip = False
    jsonList = []
    browser = await launch()
    fo = open('links_shogitown.txt', 'a')
    for url in urls:
        page = await browser.newPage()
        await page.goto(url)
        links = await page.querySelectorAllEval('a', 'elems => elems.map(elem => elem.getAttribute("href")).map(elem => new URL(elem, document.baseURI).href)')
        await page.close()
        tsumeLinks = [link for link in links if link not in blacklist]
        print(tsumeLinks)
        for x, tsumeLink in enumerate(tsumeLinks):
            if last == tsumeLink:
                willSkip = False
                continue
            if willSkip:
                continue
            #print('kek1')
            page = await browser.newPage()
            await page.goto(tsumeLink)
            #print('kek2')
            tsumeImageLinks = await page.querySelectorAllEval('img', 'elems => elems.map(elem => elem.getAttribute("src")).map(elem => new URL(elem, document.baseURI).href).filter(elem => elem.endsWith("gif"))')
            #print('kek3')
            answerPageLink = await page.querySelectorAllEval('a', 'elems => Array.from(elems).filter(elem => elem.innerHTML == "解答を見る").map(elem => elem.getAttribute("href")).map(elem => new URL(elem, document.baseURI).href)')
            await page.close()
            page = await browser.newPage()
            await page.goto(answerPageLink[0])
            #print('kek4')
            htmlContent = await page.content()
            #print('kek5')
            await page.close()
            answersRe = re.findall(r'第.*?問(?:<br>\n.*?)?<br>(\n.*?)((まで(１|３|５)手詰)?。|まで)<br>', htmlContent)
            answers = [answer[0] for answer in answersRe]
            if len(tsumeImageLinks) != len(answers):
                raise ValueError #probably not the right error but w/e
            for tsumeImageLink, answer in zip(tsumeImageLinks, answers):
                jsonObj = {'question': tsumeImageLink, 'answer': answer.strip(), 'source': url}
                fo.write(json.dumps(jsonObj) + '\n')
                #print(jsonObj)
            print(tsumeLink)
            print(x+1,'/',len(tsumeLinks))

    await browser.close()
    print('Done')

async def main():
    await scrape_shogitown()


asyncio.get_event_loop().run_until_complete(main())

