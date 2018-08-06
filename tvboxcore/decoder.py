#-*- coding: utf-8 -*-

import re

try:
    import json
except:
    import simplejson as json

import urllib
import shutil
import zipfile
import os

from tvboxcore.xbmcutils import XBMCUtils
from tvboxcore import downloadtools
from tvboxcore import ziptools
from tvboxcore import logger

class Decoder():

    #START STRING UTILS

    @staticmethod
    def extract(fromString, toString, data):
        newData = data[data.find(fromString) + len(fromString):]
        newData = newData[0:newData.find(toString)]
        return newData

    @staticmethod
    def rExtract(fromString, toString, data):
        newData = data[0:data.rfind(toString)]
        newData = newData[newData.rfind(fromString) + len(fromString):]
        return newData

    @staticmethod
    def extractWithRegex(fromString, toString, data):
        newData = data[data.find(fromString):]
        newData = newData[0:newData.find(toString) + len(toString)]
        return newData

    @staticmethod
    def rExtractWithRegex(fromString, toString, data):
        newData = data[0:data.rfind(toString) + len(toString)]
        newData = newData[newData.rfind(fromString):]
        return newData

    #END STRING UTILS

    @staticmethod
    def decodeLink(link,referer=''):
        try:
            logger.debug("first try...")
            link = Decoder.decodeWithImportedEngine(targetUrl=link)
            logger.debug("done, url at this moment is %s " % link)
        except Exception as e:
            logger.info("Something goes wrong, probably there are not engines available, retrying... %s " % str(e))
            Decoder.importEngine(engine="alfaengine",url="https://github.com/alfa-addon/addon/archive/master.zip",targetPath="/addon-master/plugin.video.alfa/",deletePath="addon-master")
            logger.debug("retry in course...")
            try:
                link = Decoder.decodeWithImportedEngine(link)
            except Exception as e2:
                logger.error("Something goes wrong: %s" % str(e2))
            pass
        return link

    @staticmethod
    def decodeWithImportedEngine(targetUrl):

        finalLink = ""
        from alfaengine.core.servertools import get_servers_list, get_server_parameters
        from alfaengine.platformcode import config

        if str(len(targetUrl)) > 0:
            for serverid in get_servers_list().keys():
                server_parameters = get_server_parameters(serverid)
                for pattern in server_parameters.get("find_videos", {}).get("patterns", []):
                    for match in re.compile(pattern["pattern"], re.DOTALL).finditer(targetUrl):
                        url = pattern["url"]
                        for x in range(len(match.groups())):
                            url = url.replace("\\%s" % (x + 1), match.groups()[x])
                            scriptToInvoke = __import__("alfaengine.servers." + serverid, globals(), locals(),
                                                        ["get_video_url"], 0)
                            links = scriptToInvoke.get_video_url(page_url=url)
        try:
            for link in links:
                if (str(type(link) == list)):
                    for linkC in link:
                        if "http" in linkC:
                            logger.debug("found link %s" % linkC)
                            finalLink = linkC
        except:
            if len(finalLink) == 0:
                finalLink = targetUrl
            logger.debug("link will be %s" % finalLink)
            pass
        return finalLink


    @staticmethod
    def importEngine(engine,url,targetPath,deletePath):

        try:
            shutil.rmtree(engine)
        except:
            logger.debug("doesn't exists... continue")
            pass

        logger.debug("downloading...")

        ROOT_DIR = XBMCUtils.getAddonInfo('path')

        localfile = ROOT_DIR + "/master.zip"

        downloadtools.downloadfile(url, localfile, notStop=False)

        logger.debug("done, unzipping...")
        logger.debug("Download done, now it's time to unzip")
        unzipper = ziptools.ziptools()
        unzipper.extract(localfile, ROOT_DIR)
        shutil.move(ROOT_DIR+targetPath, ROOT_DIR+"/"+engine)
        logger.debug("done, delete all unused files...")
        shutil.rmtree(ROOT_DIR+"/"+deletePath)
        logger.debug("Unzip done! cleaning...")
        os.unlink(localfile)
        logger.info("Additional addon clean done!")