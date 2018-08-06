import xbmc
import xbmcplugin
import xbmcaddon
import sys

enabled = bool(xbmcplugin.getSetting(int(sys.argv[1]), "debug")=="true")
IDADDON='org.harddevelop.kodi.tv'
ROOT_DIR = xbmcaddon.Addon(id=IDADDON).getAddonInfo('path')

def info(text):
    if enabled:
        try:
            f = open(ROOT_DIR+'/log_file.txt', 'a+')
            f.write(text+"\n")
            f.close()
            xbmc.log(text)
        except:
            validChars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in text if c in validChars)
            xbmc.log("(stripped) "+stripped)

def debug(text):
    if enabled:
        try:
            f = open(ROOT_DIR+'/log_file.txt', 'a+')
            f.write(text + "\n")
            f.close()
            xbmc.log(text)
        except:
            validChars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in text if c in validChars)
            xbmc.log("(stripped) "+stripped)

def error(text):
    if enabled:
        try:
            f = open(ROOT_DIR+'/log_file.txt', 'a+')
            f.write(text + "\n")
            f.close()
            xbmc.log(text)
        except:
            validChars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in text if c in validChars)
            xbmc.log("(stripped) "+stripped)
