'''
TODO

Current instructions:
Structure of project
main folder
  |- /image_data
    |- 1.png
    |- ... 
    |- XX.png
  |- game_data.csv

Run project file to generate game_data.csv and re-run to update periodically
Delete game_data.csv to refresh with all images in image_data
  
'''

import tesserocr
import PIL.ImageOps
import PIL.ImageEnhance
import re
import os
import imghdr
import csv
import pandas as pd
import platform
from PIL import Image
from pathlib import Path
from datetime import datetime, timedelta

class Game:
    def __init__(self, datetime):
        self.screenshot_datetime = datetime

    def setGameData(self, datalist):
        '''iterate through datalist, find relevant fields and populate data in Game'''
        self.setFeat('nothing')
        for i in datalist:
            if i.startswith('Won Match') or i.startswith('Top 5'):
                self.setFeat(i)
            if i.startswith('Time Survived'):
                self.setSurvivalTime(i)
            elif i.startswith('Kills'):
                self.setKills(i)
            elif i.startswith('Damage Done'):
                self.setDamage(i)
            elif i.startswith('Revive'):
                self.setRevives(i)
            elif i.startswith('Respawn'):
                self.setRespawns(i)
            elif i.startswith('Playing with Friends'):
                self.setPremade(i)
            else:
                pass
    
    def setSurvivalTime(self, time):
        #store game time as timedelta for calculating game time
        x = re.search(r"\((.+)\)", time)
        t = datetime.strptime(x.group(1),"%M:%S")
        delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        self.start_time = self.screenshot_datetime - delta #update game_datetime to be game start time
        self.survival_time = delta
    
    def setKills(self, kills):
        x = re.search(r"\(x(\d+)\)", kills)
        self.kills = x.group(1)

    def setRevives(self, revives):
        x = re.search(r"\(x(\d+)\)", revives)
        self.revives = x.group(1)

    def setRespawns(self, respawns):
        x = re.search(r"\(x(\d+)\)", respawns)
        self.respawns = x.group(1)

    def setDamage(self, damage):
        try:
            x = re.search(r"\((.+)\)", damage)
            self.damage = x.group(1)
        except:
            self.damage = 'OCR error'

    def setPremade(self, friends):
        x = re.search(r"\(x(\d+)\)", friends)
        if (int(x.group(1)) > 0):
            self.premade = True
        else: 
            self.premade = False

    def setFeat(self, feat):
        if feat.startswith('Won Match'):
            self.feat = 'Champion'
        elif feat.startswith('Top 5'):
            self.feat = 'Top 5'
        else:
            self.feat = 'No feat'
        

def cropAndInvertImage(raw_img):
    w, h = raw_img.size #1920 * 1080
    (left, upper, right, lower) = ((0.103*w), (0.13*h), (0.526*w), (0.45*h))
    img_crop = raw_img.crop((left, upper, right, lower)) 

    inverted_image = img_crop.convert('L')
    inverted_image = PIL.ImageOps.invert(inverted_image)
    return inverted_image

def readTextFromImage(inverted_image):
    api = tesserocr.PyTessBaseAPI()
    api.SetImage(inverted_image)
    text = api.GetUTF8Text()
    text = text.split('\n')
    return text

def metadata(txt):
    x = re.search(r"(\d{4}\.\d{2}\.\d{2})(?:\s\-\s)(\d{2}\.\d{2}.\d{2})", txt)
    game_datetime = x.group(0)
    game_datetime = datetime.strptime(game_datetime, '%Y.%m.%d - %H.%M.%S')
    return game_datetime

def outputCSV(game_list):
    csv_columns = ['screenshot_datetime', 'start_time','feat', 'survival_time', 'kills', 'damage', 'revives', 'respawns', 'premade']
    filepath = Path(os.path.join(os.path.dirname(__file__), 'game_data.csv'))
    outputfile = open(filepath, 'a', newline = '')
    with outputfile as csvfile:
        writer = csv.writer(csvfile)
        if os.stat(filepath).st_size == 0:
            writer.writerow(csv_columns)
        for item in game_list:
                writer.writerow([
                    item.screenshot_datetime,
                    item.start_time,
                    item.feat,
                    item.survival_time,
                    item.kills,
                    item.damage,
                    item.revives,
                    item.respawns,
                    item.premade
                    ])

def getLatestUpdate():
    try:
        filepath = Path(os.path.join(os.path.dirname(__file__), 'game_data.csv'))
        #df = pd.read_csv(r'/Users/mus/Personal/ocr_project/game_data.csv')
        df = pd.read_csv(filepath)
        df['screenshot_datetime'] = df['screenshot_datetime'].astype('datetime64[ns]')
        return df.screenshot_datetime.max()
    except:
        return datetime.strptime('2019-02-19 00:00:00', '%Y-%m-%d %H:%M:%S')
                
def main():
    #iterate through target directory and do all preproc and ocr
    cwd = os.path.dirname(os.path.realpath(__file__))
    print(cwd)
    game_list = []
    basepath = Path(os.path.join(os.path.dirname(__file__), './image_data'))
    files_in_basepath = basepath.iterdir()
    last_updated = getLatestUpdate()
    print('Last Updated:',last_updated)
    print('Working...')
    for item in files_in_basepath:
        if platform.system() == 'Windows':
            timestamp_dt = datetime.fromtimestamp(item.stat().st_ctime)
            pass
        else:
            timestamp_dt = datetime.fromtimestamp(item.stat().st_birthtime)
        if (item.is_file() and item.suffix==".png" and (timestamp_dt > last_updated)):
            pil_image = Image.open(os.path.join(basepath, item.name))
            text_in_image = readTextFromImage(cropAndInvertImage(pil_image))

            #set game data
            newMatch = Game(timestamp_dt)
            newMatch.setGameData(text_in_image)

            #add to list of games
            game_list.append(newMatch)

    outputCSV(game_list)
    print('Done')
        
if __name__ == "__main__":
    main()