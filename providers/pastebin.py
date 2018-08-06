import time
import random
import re

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger

class Pastebin(Downloader):

    @staticmethod
    def searchLists(param):
        url = "https://www.googleapis.com/customsearch/v1element?" \
              "key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY" \
              "&rsz=filtered_cse" \
              "&num=20" \
              "&hl=en" \
              "&prettyPrint=false" \
              "&source=gcsc" \
              "&gss=.com" \
              "&sig=8bdfc79787aa2b2b1ac464140255872c" \
              "&cx=013305635491195529773:0ufpuq-fpt0"
        url += "&q="+param+"&sort=date&googlehost=www.google.com&callback=google.search.Search.apiary846"

        results = Pastebin.getContentFromUrl(url)
        x = []
        jsonString = Decoder.extract(',"results":',']});',results)
        logger.debug(jsonString)
        for jsonResult in results.split('{"GsearchResultClass"'):
            element = {}
            link = Decoder.extract('"url":"','","',jsonResult)
            if "pastebin.com" in link and '/raw/' not in link:
                link = link[:link.rfind('/')]+"/raw/"+link[link.rfind('/')+1:]
            title = Decoder.extract('"title":"','","titleNoFormatting"',jsonResult)
            if "http" in link:
                logger.debug("appending result: "+title+", url: "+link)
                element["title"] = title
                element["link"] = link
                x.append(element)
        return x

