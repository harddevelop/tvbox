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
    def applyFix(fileFix,removeFix,replaced=''):
        logger.debug("Applying fix...")
        ROOT_DIR = XBMCUtils.getAddonInfo('path')
        # Read in the file
        pythonScript = ROOT_DIR + fileFix
        with open(pythonScript, 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(removeFix, replaced)

        # Write the file out again
        with open(pythonScript, 'w') as file:
            file.write(filedata)

    @staticmethod
    def decodeLink(link,referer=''):
        originalLink = link
        patternList = ['.torrent', 'acestream:', 'magnet:', 'sop:', 'mondo.me']
        if not any(regex in link for regex in patternList):

            logger.debug("trying alfa engine...")
            try:
                logger.debug("first try...")
                link = Decoder.decodeWithImportedEngine(targetUrl=link)
                logger.debug("done, url at this moment is %s " % link)
            except Exception as e:
                logger.info("Something goes wrong, probably there are not engines available, retrying... %s " % str(e))
                try:
                    Decoder.importEngine(engine="alfaengine",
                                         url="https://github.com/alfa-addon/addon/archive/master.zip",
                                         targetPath="/addon-master/plugin.video.alfa/", deletePath="addon-master")
                    logger.debug("retry in course...")
                    link = Decoder.decodeWithImportedEngine(link)
                except Exception as e2:
                    logger.error("FATAL: Something goes wrong: %s" % str(e2))
                    pass
                pass

            if originalLink == link or len(link)==0:
                #use second one
                logger.debug("trying youtube-dl library...")
                try:
                    link = Decoder.decodeWithYoutubeEngine(url=link)
                except Exception as e:
                    logger.info(
                        "Something goes wrong, probably there are not engines available, retrying... %s " % str(e))
                    Decoder.importEngine(engine="youtubedl", url="https://github.com/rg3/youtube-dl/archive/master.zip",
                                         targetPath="/youtube-dl-master/youtube_dl/", deletePath="youtube-dl-master")

                    Decoder.applyFix(fileFix="/youtubedl/extractor/common.py", removeFix='and sys.stderr.isatty()')
                    Decoder.applyFix(fileFix="/youtubedl/YoutubeDL.py", removeFix='and self._err_file.isatty()')
                    Decoder.applyFix(fileFix="/youtubedl/downloader/common.py", removeFix='sys.stderr.isatty()',
                                     replaced='False')

                    logger.debug("retry in course...")
                    try:
                        link = Decoder.decodeWithYoutubeEngine(url=link)
                    except Exception as e2:
                        logger.error("Something goes wrong: %s" % str(e2))
                        pass
                    pass
        return link

    @staticmethod
    def decodeWithYoutubeEngine(url):
        finalLink = ""
        from youtubedl.YoutubeDL import YoutubeDL
        downloader = YoutubeDL()
        response = downloader.extract_info(url=url, download=False)
        try:
            for links in response:
                finalLink = links["url"]
                logger.debug("found link %s" % finalLink)
        except:
            finalLink = response["url"]
            logger.debug("using final link %s " % finalLink)
            pass
        return finalLink

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

        ROOT_DIR = XBMCUtils.getAddonInfo('path')

        try:
            shutil.rmtree(ROOT_DIR+"/"+engine)
        except:
            logger.debug("local folder %s doesn't exists... continue" % str(ROOT_DIR+"/"+engine))
            pass

        logger.debug("downloading...")

        localfile = ROOT_DIR + "/master.zip"

        try:
            os.delete(localfile)
        except:
            logger.debug("local file doesn't exists... continue")
            pass

        downloadtools.downloadfile(url, localfile, notStop=True)

        logger.debug("done, unzipping...")
        logger.debug("Download done, now it's time to unzip")
        unzipper = ziptools.ziptools()
        unzipper.extract(localfile, ROOT_DIR)
        shutil.move(ROOT_DIR+targetPath, ROOT_DIR+"/"+engine)
        logger.debug("done, delete all unused files...")
        shutil.rmtree(ROOT_DIR+"/"+deletePath)
        logger.debug("Unzip done! cleaning...")
        try:
            os.unlink(localfile)
        except:
            logger.debug("couldn't remove %s" % localfile)
            pass
        logger.info("Additional addon clean done!")
