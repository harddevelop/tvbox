import urllib
import sys,os
import platform

from tvboxcore.xbmcutils import XBMCUtils
from tvboxcore import logger
from tvboxcore import updater

from tvboxcore.decoder import Decoder
from tvboxcore.downloader import Downloader

from providers.mamahdcom import Mamahdcom

MAX = 131

def open(url,page,decode=True):
	if decode:
		if "rtmp://" not in url:
			try:
				if url.find(", referer: ")>-1:
					page = url[url.find(", referer: ")+len(", referer: "):]
					url = url[:url.find(", referer: ")]
					logger.debug("changing page to referer: "+page)
				logger.debug("trying decoder part for url: "+url)
				url = Decoder.decodeLink(url,page)
			except:
				logger.info("decoder url launched an exception, probably could not be decoded")
				pass
		#launch redirects to his better addons
		if "youtube.com/" in url:
			id = ""
			if url.find("v=") > -1:
				id = url[url.find("v=") + len("v="):]
			elif url.find("/embed/") > -1:
				id = url[url.find("/embed/") + len("/embed/"):]
			url = "plugin://plugin.video.youtube/play/?video_id=" + id + ""
		elif "vimeo.com/" in url:
			url = "plugin://plugin.video.vimeo/play/?video_id=" + urllib.quote_plus(url)
		elif url.find("sop://")>-1 or url.find("acestream://")>-1 or url.find(".acelive")>-1: #required plexus or something similar installed, this dependency is external from this addon so needs to be installed
			logger.info("trying to send link to plexus: "+url)
			mode = "1"
			if url.find("sop://")>-1:
				mode = "2"
			url = "plugin://program.plexus/?mode="+mode+"&url="+url+"&name=RemoteLink"
		elif ".torrent" in url or url.find("magnet:")>-1:
			logger.info("trying to send link to quasar: "+url)
			url = urllib.quote_plus(url)
			url = "plugin://plugin.video.quasar/play?uri="+url
		else:
			logger.info("nothing done!")
	logger.debug("launching playable url: "+url)
	play(url,page)

def play(url,page):
	listitem = XBMCUtils.getSimpleList(page)
	listitem.setProperty('IsPlayable','true')
	listitem.setPath(url)
	listitem.setInfo("video",page)
	try:
		#XBMCUtils.play(url,listitem)
		XBMCUtils.resolveListItem(sys.argv[1],listitem) ##FIX FOR PREVIEWS LINE##
		#xbmc.executebuiltin('Dialog.Close(all, true)') ## could be returned an empty element in a list, so player open the next and shows a invalid popup
	except:
		pass
		#print(traceback.format_exc())

def add_dir(name,url,mode,iconimage,provider,page="", thumbnailImage=''):
	type = "Video"
	u=sys.argv[0]+"?url="+urllib.quote_plus(url.decode('utf-8', 'replace').encode('iso-8859-1', 'replace'))
	u+="&mode="+str(mode)+"&page="
	try:
		u+=urllib.quote_plus(str(page))
	except:
		u+=page
		pass
	provider = str(provider)
	u+="&provider="+urllib.quote_plus(provider.decode('utf-8', 'replace').encode('iso-8859-1', 'replace'))
	ok=True
	liz=XBMCUtils.getList(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo(type='Video', infoLabels={'Title': name})
	if mode == 2 or (mode >=100 and mode<=MAX): #playable, not browser call, needs decoded to be playable or rtmp to be obtained
		liz.setProperty("IsPlayable", "true")
		liz.setPath(url)
		ok=XBMCUtils.addPlayableDirectory(handle=int(sys.argv[1]),url=u,listitem=liz) #Playable)
	else:
		liz.setProperty('Fanart_Image', thumbnailImage)
		ok=XBMCUtils.addDirectory(sys.argv[1],url=u,listitem=liz) #Folder

	return ok


def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		try:
			#now extract expected params, it has been changed because some params could be links
			#with other params and the previews method (split with '?' expr. doesn't work in some cases)
			logger.debug("filling params array with brute params...")
			mode = params[params.find("mode=")+len("mode="):]
			logger.debug("brute mode: "+mode)
			if mode.find("&")>-1:
				mode = mode[:mode.find("&")]
			url = params[params.find("url=")+len("url="):]
			logger.debug("brute url: "+url)
			if url.find("&mode")>-1:
				url = url[:url.find("&mode")]
			elif url.find("&page")>-1:
				url = url[:url.find("&page")]
			elif url.find("&")>-1:
				url = url[:url.find("&")]
			page = params[params.find("page=")+len("page="):]
			logger.debug("brute page: "+page)
			if page.find("&provider")>-1:
				page = page[:page.find("&provider")]
			elif page.find("&")>-1:
				page = page[:page.find("&")]
			provider = params[params.find("provider=")+len("provider="):]
			logger.debug("brute provider: "+provider)
			if provider.find("&")>-1:
				provider = provider[:provider.find("&")]
			#finally put in param array
			logger.debug("done, filling params dic...")
			param={}
			param["mode"] = mode
			param["url"] = url
			param["page"] = page
			param["provider"] = provider
			logger.debug("done params built: "+str(len(param)))
		except Exception as e:
			logger.error("ERROR: using old method to extract params..."+str(e))
			#old method
			cleanedparams=params.replace('?','')
			if (params[len(params)-1]=='/'):
				params=params[0:len(params)-2]
			pairsofparams=cleanedparams.split('&')
			param={}
			for i in range(len(pairsofparams)):
				splitparams={}
				splitparams=pairsofparams[i].split('=')
				if (len(splitparams))==2:
					param[splitparams[0]]=splitparams[1]
					logger.info("param: "+splitparams[0]+" with value: "+splitparams[1])

	return param

def quasarUpdater():
    if XBMCUtils.getDialogYesNo(XBMCUtils.getString(30052), XBMCUtils.getString(30052)):
        quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/archive/master.zip"
        if XBMCUtils.isWindowsPlatform():
            logger.debug("Detected Windows system...")
            if "x64" in platform.machine():
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.windows_x64.zip"
            else:
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.windows_x86.zip"
        elif XBMCUtils.isAndroidPlatform():
            logger.debug("Detected Android system...")
            if os.uname()[4].startswith("arm"):
                logger.debug("android system...")
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.android_arm.zip"
            else:
                logger.debug("Androidx86 system...")
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.android_x86.zip"
        elif XBMCUtils.isRaspberryPlatform():
            logger.debug("raspberry system...")
            if "armv7" in platform.machine():
                logger.debug("raspberry pi 2!")
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_armv7.zip"
            elif "armv6" in platform.machine():
                logger.debug("raspberry pi 1!")
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_arm.zip"
            else:
                logger.debug("raspberry pi 3!")
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_arm64.zip"
        elif XBMCUtils.isLinuxPlatform():
            if "x64" in platform.machine():
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_x64.zip"
            else:
                quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_x86.zip"
        else:
            logger.info("no detected platform, using default (could be a osx?)")
        try:
            updater.install(quasarUrl, "plugin.video.quasar", "plugin.video.quasar")
            logger.debug("addon installed!")
        except:
            logger.error("Addon not installed, something wrong happened!")
            pass
        XBMCUtils.getOkDialog(XBMCUtils.getString(30051), XBMCUtils.getString(30051))
        logger.debug("launch done!")

def plexusUpdater():
    if XBMCUtils.getDialogYesNo(XBMCUtils.getString(30050), XBMCUtils.getString(30050)):
        try:
            url = "https://github.com/AlexMorales85/program.plexus/archive/1.2.2.zip"  # better and updated with an acestream fixed client for raspberry platforms
            updater.install(url, "program.plexus", "program.plexus")
            logger.debug("addon installed!")
            # try with request dependency
            updater.install("https://github.com/beenje/script.module.requests/archive/gotham.zip",
                            "script.module.requests", "script.module.requests")
            logger.debug("dependency installed, finished!")
        except:
            logger.error("Addon not installed, something wrong happened!")
            pass
        XBMCUtils.getOkDialog(XBMCUtils.getString(30051), XBMCUtils.getString(30051))
        logger.debug("launch done!")

def addonUpdater():
	if XBMCUtils.getDialogYesNo(XBMCUtils.getString(10011), updater.getUpdateInfo()):
		updater.update()

def httpProxyUpdater():
	masterPatchUrl = "https://github.com/harddevelop/httpproxy-service/archive/master.zip"
	try:
		updater.install(masterPatchUrl, "org.harddevelop.kodi.proxy", "org.harddevelop.kodi.proxy")
		XBMCUtils.getOkDialog(XBMCUtils.getString(30060), XBMCUtils.getString(30060))
		logger.debug("patch installed!")
	except:
		logger.error("Patch not installed, something wrong happened!")
		pass
