
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcgui
import os
import urllib
from tvboxcore import logger

class XBMCUtils():

    @staticmethod
    def getAddonInfo(property,idAddon='org.harddevelop.kodi.tv'):
        return xbmcaddon.Addon(id=idAddon).getAddonInfo(property)

    @staticmethod
    def getSettingFromContext(context,setting):
        return xbmcplugin.getSetting(int(context), setting)

    @staticmethod
    def getSetting(property,idAddon="org.harddevelop.kodi.tv"):
        xbmcaddon.Addon(id=idAddon).getSetting(property)

    @staticmethod
    def isWindowsPlatform():
        return xbmc.getCondVisibility("system.platform.windows")

    @staticmethod
    def isAndroidPlatform():
        return xbmc.getCondVisibility("System.Platform.Android")

    @staticmethod
    def isRaspberryPlatform():
        return xbmc.getCondVisibility("System.Platform.Linux.RaspberryPi")

    @staticmethod
    def isLinuxPlatform():
        return xbmc.getCondVisibility("System.Platform.Linux")

    @staticmethod
    def getAddonsDir():
        separatorChar = '/'
        if XBMCUtils.isWindowsPlatform():
            logger.debug("Detected Windows system...")
            separatorChar = "\\"
        addons_dir = xbmc.translatePath("special://home"+separatorChar+"addons"+separatorChar)
        return addons_dir

    @staticmethod
    def getSeparatorChar():
        separatorChar = "/"
        if XBMCUtils.isWindowsPlatform():
            separatorChar = "\\"
        return separatorChar

    @staticmethod
    def getPathFixedFrom(path):
        separatorChar = XBMCUtils.getSeparatorChar()
        return xbmc.translatePath(path[path.rfind(separatorChar)+1:])

    @staticmethod
    def executeScript(path):
        xbmc.executebuiltin('RunScript('+path+')')

    @staticmethod
    def getAddon(idAddon="org.harddevelop.kodi.tv"):
        return xbmcaddon.Addon(id=idAddon)

    @staticmethod
    def getString(id):
        return XBMCUtils.getAddon().getLocalizedString(id)

    @staticmethod
    def getDialog():
        return xbmcgui.Dialog()

    @staticmethod
    def getDialogProgress():
        return xbmcgui.DialogProgress()

    @staticmethod
    def getRightString(string):
        return xbmc.makeLegalFilename(string)

    @staticmethod
    def log(text):
        return xbmc.log(text)

    @staticmethod
    def getAddonFilePath(file='icon.png'):
        return xbmc.translatePath(os.path.join( XBMCUtils.getAddonInfo('path'), file ))

    @staticmethod
    def getList(name, iconImage, thumbnailImage):
        return xbmcgui.ListItem(name, iconImage=iconImage, thumbnailImage=thumbnailImage)

    @staticmethod
    def getSimpleList(name):
        return xbmcgui.ListItem(name)

    @staticmethod
    def addPlayableDirectory(handle,url,listitem):
        return xbmcplugin.addDirectoryItem(handle=int(handle),url=url,listitem=listitem,isFolder=False) #Playable

    @staticmethod
    def addDirectory(handle,url,listitem):
        return xbmcplugin.addDirectoryItem(handle=int(handle),url=url,listitem=listitem,isFolder=True) #Folder

    @staticmethod
    def getPlayer():
        return xbmc.Player(xbmc.PLAYER_CORE_AUTO)

    @staticmethod
    def play(url, listitem):
        player = XBMCUtils.getPlayer()
        if player.isPlaying() :
            player.stop()
        #xbmc.sleep(1000)
        player.showSubtitles(False)
        urlPlayer = urllib.unquote_plus(url.replace("+","@#@")).replace("@#@","+")
        urlPlayer = urllib.unquote_plus(url) ##THIS METHOD FAILS IN SOME CASES SHOWING A POPUP (server petition and ffmpeg internal problem)
        player.play(urlPlayer,listitem) ##THIS METHOD FAILS IN SOME CASES SHOWING A POPUP (server petition and ffmpeg internal problem)

    @staticmethod
    def resolveListItem(context,listitem):
        xbmcplugin.setResolvedUrl(int(context), True, listitem)

    @staticmethod
    def getDialogYesNo(title,text):
        return xbmcgui.Dialog().yesno(title,text, "", "", XBMCUtils.getString(11013), XBMCUtils.getString(11014) )

    @staticmethod
    def getOkDialog(title,text):
        return xbmcgui.Dialog().ok(title,text)

    @staticmethod
    def getNotification(title,text):
        xbmcgui.Dialog().notification(title,text)

    @staticmethod
    def setEndOfDirectory(context):
        xbmcplugin.endOfDirectory(int(context))

    @staticmethod
    def getKeyboard(text=''):
        return xbmc.Keyboard(text)
