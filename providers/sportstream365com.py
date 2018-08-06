# -*- coding: utf-8 -*-
from datetime import datetime
from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from tvboxcore import logger
from tvboxcore.downloader import Downloader

try:
    import json
except:
    import simplejson as json


class Sportstream365com(Downloader):


    MAIN_URL = "http://sportstream365.com/"
    API_URL = "http://sportstream365.com/LiveFeed/GetLeftMenuShort"

    @staticmethod
    def getChannels(page):
        x = []
        if Sportstream365com.cookie=="":
            Sportstream365com.cookie = "lng=en" #default language is russian, so I prefer 'translated' English
        if str(page) == '0':
            page=Sportstream365com.API_URL
            params = "" #build params to get petition
            params += "_="+str(datetime.now().microsecond)
            params += "&lng="+"en"
            params += "&partner="+"24"
            params += "&sports="+"1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,87,88,89,90,91,92,93,94,95,96,97,98,99,100" #TODO, change with a for instead
            logger.debug(params)
            jsonData = Sportstream365com.getContentFromUrl(page+"?"+params,"",Sportstream365com.cookie,Sportstream365com.MAIN_URL)
            x = Sportstream365com.extractElements(json.loads(jsonData))
        return x

    @staticmethod
    def extractElements(jsonData):
        x = []
        i = 0
        logger.debug("json is "+str(len(jsonData)))
        for value in jsonData["Value"]:
            element = {}
            title = datetime.fromtimestamp(int(str(value["Start"])[:len(str(value["Start"]))-3])).strftime('%d/%m/%y - %H:%M')+" "+value["Sport"]+" - "+value["Opp1"]+" vs. "+value["Opp2"]
            link = "http://sportstream365.com/viewer?game="+str(value["FirstGameId"])
            element["title"] = title
            element["link"] = link
            logger.debug("append: "+title+", link: "+element["link"])
            x.append(element)
            i+=1
        return x