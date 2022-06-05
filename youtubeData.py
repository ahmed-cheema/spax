# Script to collect metadata and transcript information from YouTube videos
# Both metadata and transcript data can be retrieved for a YouTube video in less than two seconds
# Script made by Ahmed Cheema

from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
from pyyoutube import Api
import pandas as pd
import requests
import math
import time
import re

# accesses the youtube API with a key
api = Api(api_key=INSERT-KEY-HERE)
    
# converts number of seconds to a MM:SS timestamp
def timestamp(sec):
    minutes = math.floor(sec/60)
    r = round(sec%60)
    return str(minutes)+':'+str(r).zfill(2)

class Duration:
    def __init__(self, days, hours, minutes, seconds):
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

# converts youtube duration string
def convertDuration(c):
    dur = c.strip('P').strip('T')
    
    D = re.findall(r"(\d+)DT",dur)+['0']
    H = re.findall(r"(\d+)H",dur)+['0']
    M = re.findall(r"(\d+)M",dur)+['0']
    S = re.findall(r"(\d+)S",dur)+['0']
    
    return Duration(D[0].zfill(2),
                    H[0].zfill(2),
                    M[0].zfill(2),
                    S[0].zfill(2))

# convert two letter language codes into words
# if statement can be expanded
def convertLanguage(lang):
    if lang == 'en':
        return 'english'
    if lang == 'en-US':
        return 'english'
    elif lang == 'ar':
        return 'arabic'

# collects the metadata for a youtube video
# example usage: 
#   metaData('https://www.youtube.com/watch?v=5JaG0W3dzzs','saud',0)
def metaData(videoUrl,channel,ID):
    videoId = videoUrl.split('?v=')[1]

    r = requests.get(videoUrl)

    sp = BeautifulSoup(r.text,'lxml')
    
    channelUrl = sp.find_all('link',{'itemprop':'url'})[1]['href']
    
    videoInfo = api.get_video_by_id(video_id=videoId).items[0]
    
    video_id = str(ID+1).zfill(5)
    
    title = videoInfo.snippet.title
    
    duration = convertDuration(videoInfo.contentDetails.duration)
    durationMin = 60*(24*int(duration.days)+int(duration.hours))+int(duration.minutes)
    durationString = str(durationMin)+':'+duration.seconds

    language = convertLanguage(videoInfo.snippet.defaultAudioLanguage)
    
    keys = ['creator','video_id','video_url','creator_url','video title','duration','original_language']
    values = [channel,video_id,videoUrl,channelUrl,title,durationString,language]
    
    return pd.DataFrame({'key':keys,'value':values})

# collects transcripts for a youtube video
# returns dataframe stating "No Transcript Found" if video has no transcript
def transcripts(videoUrl):
    videoId = videoUrl.split('?v=')[1]
    
    try:
        trans_list = []
        for x in YouTubeTranscriptApi.list_transcripts(videoId):
            tf = pd.DataFrame(x.fetch())
            tf['start_time'] = tf.start.apply(timestamp)
            tf['end_time'] = tf.start_time.shift(-1)
            tf[x.language.split(' ')[0]] = tf.text
            tf = tf[['start_time','end_time',x.language.split(' ')[0]]]
            trans_list.append(tf)

        return pd.concat(trans_list,axis=1)
    except:
        return pd.DataFrame({},columns=['No Transcript Found'])
