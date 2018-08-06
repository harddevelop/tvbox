import sys, os.path
import re
import urllib,urllib2
import time
import socket
import logger
import traceback # for download problems
import StringIO
import gzip
from tvboxcore.xbmcutils import XBMCUtils

def sec_to_hms(seconds):
    m,s = divmod(int(seconds), 60)
    h,m = divmod(m, 60)
    return ("%02d:%02d:%02d" % ( h , m ,s ))

def buildMusicDownloadHeaders(host,cookie='',referer=''):
    headers = {"Accept":"audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
        "Connection":"keep-alive",
        "DNT":"1",
        "Host":host,
        "Range":"bytes=0-",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0"
    }
    if cookie!='':
        headers["Cookie"] = cookie
    if referer!='':
        headers["Referer"] = referer
    return headers

def downloadfile(url,fileName,headers=[],silent=False,notStop=False):
    logger.debug("downloadfile: url="+url)
    logger.debug("downloadfile: fileName="+fileName)

    try:

        try:
            fileName = XBMCUtils.getRightString(fileName)
        except:
            pass
        logger.debug("downloadfile with fileName="+fileName)

        if os.path.exists(fileName) and notStop:
            f = open(fileName, 'r+b')
            existSize = os.path.getsize(fileName)
            
            logger.info("downloadfile: file exists, size=%d" % existSize)
            recordedSize = existSize
            f.seek(existSize)

        elif os.path.exists(fileName) and not notStop:
            logger.info("downloadfile: file exists, dont re-download")
            return

        else:
            existSize = 0
            logger.info("downloadfile: file doesn't exists")

            f = open(fileName, 'wb')
            recordedSize = 0

        if not silent:
            progressDialog = XBMCUtils.getDialogProgress() # Open dialog
            progressDialog.create("plugin",XBMCUtils.getString(10002) ,url,fileName)
        else:
            progressDialog = ""

        socket.setdefaulttimeout(30) #Timeout
    
        h=urllib2.HTTPHandler(debuglevel=0)
        remoteFile = url
        params = None

        request = urllib2.Request(url)

        logger.debug("checking headers... type: "+str(type(headers)))
        if len(headers)>0:
            logger.debug("adding headers...")
            for key in headers.keys():
                logger.debug("Header="+key+": "+headers.get(key))
                request.add_header(key,headers.get(key))
        else:
            logger.debug("headers figure are 0")

        logger.debug("checking resume status...")
        if existSize > 0: #restart
            logger.info("resume is launched!")
            request.add_header('Range', 'bytes=%d-' % (existSize, ))
    
        opener = urllib2.build_opener(h)
        urllib2.install_opener(opener)
        try:
            logger.debug("opening request...")
            connection = opener.open(request)
        except: # End
            logger.error("ERROR: "+traceback.format_exc())
            f.close()
            if not silent:
                progressDialog.close()
        logger.debug("detecting download size...")
    
        try:
            totalFileSize = int(connection.headers["Content-Length"])
        except:
            totalFileSize = 1

        logger.debug("total file size: "+str(totalFileSize))
                
        if existSize > 0:
            totalFileSize = totalFileSize + existSize
    
        logger.debug("Content-Length=%s" % totalFileSize)
    
        blockSize = 100*1024 #Buffer size
    
        bufferReadedSize = connection.read(blockSize)
        logger.info("Starting download, readed=%s" % len(bufferReadedSize))
    
        maxRetries = 5
        
        while len(bufferReadedSize)>0:
            try:
                f.write(bufferReadedSize)
                recordedSize = recordedSize + len(bufferReadedSize)
                percent = int(float(recordedSize)*100/float(totalFileSize))
                totalMB = float(float(totalFileSize)/(1024*1024))
                downloadedMB = float(float(recordedSize)/(1024*1024))

                retries = 0
                while retries <= maxRetries:
                    try:
                        before = time.time()
                        bufferReadedSize = connection.read(blockSize)
                        after = time.time()
                        if (after - before) > 0:
                            speed=len(bufferReadedSize)/((after - before))
                            remainingSize=totalFileSize-recordedSize
                            if speed>0:
                                remainingTime=remainingSize/speed
                            else:
                                remainingTime=0 #infinite

                            if not silent:
                                progressDialog.update( percent , XBMCUtils.getString(10003) % ( downloadedMB , totalMB , percent , speed/1024 , sec_to_hms(remainingTime))) #respect syntax in translations
                        break
                    except:
                        retries = retries + 1
                        logger.info("ERROR downloading buffer, retry %d" % retries)
                        logger.error( traceback.print_exc() )
                
                # if the user stops download proccess...
                try:
                    if progressDialog.iscanceled():
                        logger.info("Download was canceled by user action")
                        f.close()
                        progressDialog.close()
                        return -1
                except:
                    pass
    
                # Something wrong happened
                if retries > maxRetries:
                    logger.error("ERROR, something happened in download proccess")
                    f.close()
                    if not silent:
                        progressDialog.close()
    
                    return -2
    
            except:
                logger.error( traceback.print_exc() )

                f.close()
                if not silent:
                    progressDialog.close()

                return -2

    except:
        pass

    try:
        f.close()
    except:
        pass

    if not silent:
        try:
            progressDialog.close()
        except:
            pass

    logger.info("Finished download proccess")