import urllib2,os,sys
from tvboxcore.xbmcutils import XBMCUtils
from tvboxcore import logger
from tvboxcore import downloadtools
from tvboxcore import ziptools
import time
import CommonFunctions as common

REMOTE_FILE_XML = XBMCUtils.getSettingFromContext(sys.argv[1],"remote_updater")

ROOT_DIR = XBMCUtils.getAddonInfo('path')

def install(remote_file,id,folder):
    #first check if plexus exists, and where
    logger.info("installing "+id+"... ")

    addons_dir = XBMCUtils.getAddonsDir()
    logger.debug("Addons dir set to: "+addons_dir)

    localfile = ROOT_DIR+"/install.zip"

    downloadtools.downloadfile(remote_file, localfile, notStop=False)
    logger.debug("Download done, now it's time to unzip")
    unzipper = ziptools.ziptools()
    if folder == '':
        unzipper.extract(localfile,addons_dir) #github issues
    else:
        unzipper.extractReplacingMainFolder(localfile,addons_dir,folder)
    logger.debug("Unzip done! cleaning...")
    os.remove(localfile)
    logger.info("Additional addon clean done!")

def update():
    #download ZIP file
    start = time.clock()

    localfile = ROOT_DIR+"/update.zip"

    response = urllib2.urlopen(REMOTE_FILE_XML)
    html = response.read()
    remote_file = common.parseDOM(html,"file")[0].encode("utf-8") #remote version
    downloadtools.downloadfile(remote_file, localfile, notStop=False)

    end = time.clock()
    logger.info("org.harddevelop.kodi.tv Downloaded in %d seconds " % (end-start+1))

    separatorChar = XBMCUtils.getSeparatorChar()

    #unzip
    unzipper = ziptools.ziptools()
    logger.info("org.harddevelop.kodi.tv destpathname=%s" % ROOT_DIR)
    addons_dir = XBMCUtils.getAddonsDir()
    current_plugin_dir = XBMCUtils.getPathFixedFrom(XBMCUtils.getAddonInfo('path'))
    logger.debug("using dir: "+addons_dir+" to extract content")

    unzipper.extractReplacingMainFolder(localfile,addons_dir,current_plugin_dir) #github issues
    #unzipper.extract(localfile,ROOT_DIR)

    #clean downloaded zip file
    logger.info("org.harddevelop.kodi.tv clean zip file...")
    os.remove(localfile)
    logger.info("org.harddevelop.kodi.tv clean done!")

def isUpdatable():
    #remote file
    response = urllib2.urlopen(REMOTE_FILE_XML)
    html = response.read()
    remote_version = common.parseDOM(html,"version")[0].encode("utf-8") #remote version
    #local file
    fp = open(ROOT_DIR+"/version.xml", "r")
    content = fp.read()
    fp.close()
    local_version = common.parseDOM(content,"version")[0].encode("utf-8") #remote version
    logger.debug("Local version: "+local_version+", Remote version: "+remote_version)
    return bool(int(local_version)<int(remote_version))

def getUpdateInfo():
    response = urllib2.urlopen(REMOTE_FILE_XML)
    html = response.read()
    remote_changes = common.parseDOM(html,"changes")[0].encode("utf-8") #remote version
    return str(remote_changes)