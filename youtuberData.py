from bs4 import BeautifulSoup
import pandas as pd
import requests
import sys
import re

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

def convertDuration(c):
    dur = c.strip('P').strip('T')
    
    D = re.findall(r"(\d+)DT",dur)+['0']
    H = re.findall(r"(\d+)H",dur)+['0']
    M = re.findall(r"(\d+)M",dur)+['0']
    S = re.findall(r"(\d+)S",dur)+['0']
    
    minutes = 60*(24*int(D[0])+int(H[0]))+int(M[0])
    
    return str(minutes).zfill(2)+':'+S[0].zfill(2)

def youtuberData(url):
    r = requests.get(url).text
    channelId = r.split('externalId\":\"')[1].split('\"')[0]

    link = 'https://www.youtube.com/channel/'+channelId+'/videos?view=0&sort=p&flow=grid'

    r2 = requests.get(link).text

    topIds = list(dict.fromkeys(re.findall(r'"videoId":"(.*?)","',r2)))

    video_list = []
    for x in progressbar(topIds[:25],'Getting Top Videos: ',len(topIds[:25])):
        videoLink = 'https://www.youtube.com/watch?v='+x

        sp = BeautifulSoup(requests.get(videoLink).text)

        duration = convertDuration(sp.find('meta',{'itemprop':'duration'})['content'])

        videoTitle = sp.find('meta',{'name':'title'})['content']

        video_list.append({'Video Link':videoLink,'Title':videoTitle,
                           'Duration':duration})

    return pd.DataFrame(video_list)
