# -*- coding: utf-8 -*-
import urllib
import sys
import base64

from tvboxcore.xbmcutils import XBMCUtils
from tvboxcore.addonUtils import add_dir
from tvboxcore.addonUtils import open, play
from tvboxcore import logger
from tvboxcore.decoder import Decoder
from tvboxcore.downloader import Downloader

from tvboxcore.listsParsers import getListsUrls

from providers.filmoncom import Filmoncom
from providers.hdfulltv import HdfullTv
from providers.peliculasbiz import Peliculasbiz
from providers.cricfreetv import Cricfreetv
from providers.skylinewebcamscom import Skylinewebcamscom
from providers.mamahdcom import Mamahdcom
from providers.arenavisionin import Arenavisionin
from providers.acetvru import Acetvru
from providers.elitetorrent import Elitetorrent
from providers.youtube import Youtube
from providers.pastebin import Pastebin
from providers.redeneobuxcom import RedeneobuxCom
from providers.tunein import TuneIn
from providers.reuters import Reuters
from providers.ramalin import Ramalin
from providers.mobdro import Mobdro
from providers.antena3 import Antena3
from providers.lasexta import LaSexta
from providers.rtve import RTVE
from providers.pepecine import Pepecine
from providers.cnn import CNN
from providers.elmundo import ElMundo
from providers.elpaises import ElPais
from providers.clan import Clan
from providers.rtvealacarta import RTVEAlaCarta
from providers.mejortorrent import MejorTorrent
from providers.tumejortorrent import TuMejorTorrent
from providers.vigoalnet import Vigoal
from providers.tvporinternetnet import Tvporinternetnet
from providers.vercanalestv1com import Vercanalestv1com
from providers.elgolesme import Elgolesme
from providers.atresplayer import Atresplayer
from providers.rojadirecta import Rojadirecta

try:
	from providers.spliveappcom import Spliveappcom
except:
	logger.error("Crypto-problems detected, probably you need a better platform")
	pass

from window.DefaultWindow import DefaultWindow #papernews window library
try:
	from window.ImageWindow import windowImage #teletext window library
except:
	logger.info("No module named PIL was found in the system, hidding teletext library.")
	pass

icon = XBMCUtils.getAddonFilePath('icon.png')

def drawFilmon(page):
	jsonChannels = Filmoncom.getChannelsJSON()
	for itemFirst in jsonChannels:
		if page == "0":
			add_dir(itemFirst["title"],"http://www.filmon.com/tv/"+itemFirst["alias"],4,icon,"filmoncom",itemFirst["title"])
		elif (page == itemFirst["title"]) and itemFirst.has_key("channels") :
			for item in itemFirst["channels"]:
				add_dir(item["title"],"http://www.filmon.com/tv/"+item["alias"],5,item["logo"],"filmoncom",item["title"])
		else:
			logger.info("no channel: "+page)

def drawHdfulltv(page):
	mode = 4 #continue browsing
	jsonChannels = HdfullTv.getChannels(page)
	for itemFirst in jsonChannels:
		title = ""
		if itemFirst.has_key("permalink"):
			if itemFirst.has_key("show"): #serie
				link = "https://hdfull.me/serie/"+itemFirst["permalink"]+"/temporada-"+itemFirst["season"]+"/episodio-"+itemFirst["episode"]
				title = itemFirst["show"]["title"]
				if type(title) == type(dict()):
					if title.has_key("es"):
						title = title["es"]
					else:
						title = ""
					if len(title)==0 and itemFirst["title"].has_key("en"):
						title = itemFirst["title"]["en"]
				#put the season and the chapter
				chapter = int(itemFirst["episode"])
				if chapter<10:
					chapterString = "0"+str(chapter)
				else:
					chapterString = str(chapter)
				title = title+" "+itemFirst["season"]+"x"+chapterString
			else:
				if(itemFirst["permalink"].find("http://")>-1):
					link = itemFirst["permalink"]
				elif itemFirst["permalink"].find("http")>-1:
					link = itemFirst["permalink"]
				else:
					link = "https://hdfull.me/"+itemFirst["permalink"]
				title = itemFirst["title"]
				try:
					if type(title) == type(dict()):
						if title.has_key("es"):
							title = title["es"]
						else:
							title = ""
						if len(title)==0 and itemFirst["title"].has_key("en"):
							title = itemFirst["title"]["en"]
				except:
					logger.error("title is not dic, fails!!"+str(title))
					pass
			if itemFirst.has_key("thumbnail"):
				image = itemFirst["thumbnail"]
				if image.find("http://")<0:
					image = "https://hdfull.me/tthumb/130x190/"+image
			else:
				image = icon
		if itemFirst.has_key("finalLink"):
			mode = 100 #open link from provider
			title = itemFirst["title"]
			link = itemFirst["link"]
			image = ""
		add_dir(title,link,mode,image,"hdfulltv",link)

def drawVipgoal(page):
	jsonChannels = Vigoal.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Display by event':
			title = XBMCUtils.getString(10006)
		link = item["link"]
		if link != '1':
			mode = 101 #next step returns a final link
		else:
			mode = 4 #continue browsing
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
		else:
			image = icon
		add_dir(title,link,mode,image,"vigoal",link)


def drawCricfree(page):
	jsonChannels = Cricfreetv.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Display by event':
			title = XBMCUtils.getString(10006)
		link = item["link"]
		if link=='1':
			mode = 4
		else:
			mode = 103 #next step returns a final link
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
		else:
			image = icon
		add_dir(title,link,mode,image,"cricfree",link)

def drawSkylinewebcams(page):
	jsonChannels = Skylinewebcamscom.getChannels(page)
	mode = 4
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		if item.has_key("permaLink"):
			mode = 108
		add_dir(title,link,mode,image,"skylinewebcams",link)

def drawSplive(page):
	mode = 4
	jsonChannels = Spliveappcom.getChannels(page)
	image = icon
	for item in jsonChannels:
		try:
			logger.debug("trying splive item...")
			#title = urllib.unquote_plus(item["title"].decode('iso-8859-1', 'ignore'))
			title = item["title"]
			link = item["link"]
			referer = "splive"
			if item.has_key("permaLink"):
				mode = 111
				if item.has_key("referer"):
					referer = item["referer"]
					logger.info("referer is: "+referer)
			if item.has_key("thumbnail"):
				image = item["thumbnail"]
				logger.info("detected img: "+image)
			else:
				image = icon
			add_dir(title,link,mode,image,referer,link)
		except:
			logger.error("Something goes wrong with SPLIVEAPP drawer")
			pass

def drawMamahdcom(page):
	mode = 4
	jsonChannels = Mamahdcom.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("permaLink"):
			mode = 112
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		add_dir(title,link,mode,image,"mamahdcom",link)

def drawElgolesme(page):
	jsonChannels = Elgolesme.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		mode = 130
		if "acestream" in link:
			mode = 2
		add_dir(title,link,mode,icon,"elgolesme",link)

def drawTvporinternetnet(page):
	mode=4
	jsonChannels = Tvporinternetnet.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("permaLink"):
			mode = 128
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: " + image)
		else:
			image = icon
		add_dir(title, link, mode, image, "tvporinternetnet", link)

def drawVercanalestv(page):
	mode=4
	jsonChannels = Vercanalestv1com.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("permaLink"):
			mode = 129
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: " + image)
		else:
			image = icon
		add_dir(title, link, mode, image, "vercanalestv", link)

def drawArenavisionin(page):
	mode = 2
	jsonChannels = Arenavisionin.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		add_dir(title,link,mode,icon,"arenavisionin",link)

def drawAcetvru(page):
	mode = 2
	jsonChannels = Acetvru.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Display by event':
			title = XBMCUtils.getString(10006)
		link = item["link"]
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		add_dir(title,link,mode,image,"acetvru",link)

def drawElitetorrentnet(page):
	jsonChannels = Elitetorrent.getChannels(page)
	for item in jsonChannels:
		mode = 4
		title = item["title"]
		link = item["link"]
		if '/torrent/' in link or "finalLink" in item:
			mode = 124
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: " + image)
		else:
			image = icon
		add_dir(title, link, mode, image, "elitetorrentnet", link)

def drawYoutube(url='0'): #BROWSES ALL PROVIDERS (it has been re-sorted)
	#static content
	channels = Youtube.getChannels(url)
	logger.debug("items obtained: "+str(len(channels)))
	for channel in channels:
		image = ''
		level = 4
		if channel.has_key('finalLink'):
			level = 115
		if channel.has_key('thumbnail'):
			image = channel["thumbnail"]
		add_dir(channel["title"], channel["page"], level, image, "youtube", channel["page"])

def drawPastebinCom():
	param = urllib.quote_plus(str(XBMCUtils.getSettingFromContext(sys.argv[1],'pastebin_param')))
	logger.debug("extracted param to be searched: "+param)
	channels = Pastebin.searchLists(param=param)
	logger.debug("items obtained: " + str(len(channels)))
	level = 1
	for channel in channels:
		add_dir(channel["title"], channel["link"], level, '', "pastebincom", channel["link"])

def drawRedeneobuxCom(url):
	channels = RedeneobuxCom.getChannels(url)
	logger.debug("items obtained: " + str(len(channels)))
	for channel in channels:
		level = 4
		if channel.has_key("finalLink"):
			level = 2 #m3u8 list
		img = ''
		if channel.has_key("thumbnail"):
			img = channel["thumbnail"]
		add_dir(channel["title"], channel["link"], level, img, "redeneobuxcom", channel["link"])

def drawTuneIn(url):
	channels = TuneIn.getChannels(url)
	logger.debug("items obtained: " + str(len(channels)))
	for channel in channels:
		level = 4
		if channel.has_key("finalLink"):
			level = 118  # stream
		img = ''
		if channel.has_key("thumbnail"):
			img = channel["thumbnail"]
		add_dir(channel["title"], channel["link"], level, img, "tunein", channel["link"])

def drawAresplayer(url):
	channels = Atresplayer.getChannels(url)
	logger.debug("items obtained: " + str(len(channels)))
	for channel in channels:
		level = 4
		if channel.has_key("finalLink"):
			level = 131  # stream
		img = ''
		if channel.has_key("thumbnail"):
			img = channel["thumbnail"]
		add_dir(channel["title"], channel["link"], level, img, "atresplayer", channel["link"])

def drawRojadirecta(url):
	channels = Rojadirecta.getChannels(url)
	logger.debug("items obtained: " + str(len(channels)))
	for channel in channels:
		level = 132  # stream
		add_dir(channel["title"], channel["link"], level, icon, "rojadirecta", channel["link"])

def drawRamalin(page):
	jsonChannels = Ramalin.getChannels(page)
	for item in jsonChannels:
		mode = 4
		title = item["title"]
		link = item["link"]
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: " + image)
		else:
			image = icon
		if item.has_key("finalLink"):
			mode = 2
		add_dir(title, link, mode, image, "ramalin", link)

def drawMobdro(page):
	jsonChannels = Mobdro.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: " + image)
		else:
			image = icon
		if item.has_key("finalLink"):
			link = base64.encodestring(link)
			mode = 122 #base64 link, so needs to be decoded
		else:
			mode = 4
		add_dir(title, link, mode, image, "mobdro", link)

def drawNews(url,provider='',targetAction=1): #from rss page
	if targetAction==4 and provider=="bbccouk" and ".xml" not in url:
		drawBbcCoUkNew(url)
	else:
		getListsUrls(url,provider=provider,finalTarget=targetAction)

def drawReutersNews(url): #from rss page
	x = Reuters.getChannels(url)
	if str(url)=='0':
		level = 4
		for new in x:
			img = icon
			if new.has_key("thumbnail"):
				img = new["thumbnail"]
			add_dir(new["title"], new["link"], level, img, "reuters", 1)
	else:
		body = x[0]["title"]
		drawNew(textContent=(body))

def drawElPaisNews(url):
	x = ElPais.getChannels(url)
	if str(url) == '0':
		level = 4
		for new in x:
			img = icon
			if new.has_key("thumbnail"):
				img = new["thumbnail"]
			add_dir(new["title"], new["link"], level, img, "editionelpais", new["link"])
	else:
		body = x[0]["title"]
		logger.debug("body is: " + body)
		# clean bad html

		body = body.replace(". ", ". \n")
		logger.debug("drawing new...")
		drawNew(textContent=(body))
def drawElMundoNews(url):
	x = ElMundo.getChannels(url)
	if str(url) == '0':
		level = 4
		for new in x:
			img = icon
			if new.has_key("thumbnail"):
				img = new["thumbnail"]
			add_dir(new["title"], new["link"], level, img, "editionelmundo", new["link"])
	else:
		body = x[0]["title"]
		logger.debug("body is: "+body)
		#clean bad html

		body = body.replace(". ",". \n")
		logger.debug("drawing new...")
		drawNew(textContent=(body))

def drawCNNNews(url):
	x = CNN.getChannels(url)
	if str(url) == '0':
		level = 4
		for new in x:
			img = icon
			if new.has_key("thumbnail"):
				img = new["thumbnail"]
			add_dir(new["title"], new["link"], level, img, "editioncnn", new["link"])
	else:
		body = x[0]["title"]
		logger.debug("body is: "+body)
		#clean bad html
		body = body.replace('<h4 class="video__end-slate__tertiary-title">MUST WATCH</h4>',"")
		body = body.replace('<div class="video__end-slate__engage__more"><a href="/videos" class="video__end-slate__replay-text">More Videos ...</a></div>', "")
		body = body.replace('<h4 class="video__end-slate__tertiary-title">MUST WATCH</h4>',"")
		body = body.replace('<h3 class="cd__headline-title">JUST WATCHED</h3>', "")
		body = body.replace(".",". \n")
		logger.debug("drawing new...")
		drawNew(textContent=(body))

def drawBbcCoUkNew(url):
	htmlContent = Downloader.getContentFromUrl(url=url)
	title = Decoder.extract('<p class="story-body__introduction">','</p><div',htmlContent)
	if 'property="articleBody"' in htmlContent:
		body = Decoder.extract('property="articleBody"','                                                                                                </div>',htmlContent)
		body = body.replace('<span class="off-screen">Image copyright</span>','')
		body = body.replace('<span class="story-image-copyright">AFP</span>', '')
		body = body.replace('<span class="story-image-copyright">Reuters</span>', '')
		body = body.replace('<span class="off-screen">Image caption</span>', '')
		body = body.replace('<span class="off-screen">Media caption</span>','')
		while '<span class="media-caption__text">' in body:
			line = Decoder.extractWithRegex('<span class="media-caption__text">',"</span>",body)
			body = body.replace(line,"")
	elif 'class="text-wrapper"' in htmlContent:
		#special content
		body = Decoder.extract('class="text-wrapper"','</p>\n',htmlContent)
		dates = Decoder.extractWithRegex('<div class="date',"</div>",body)
		lastUpdate = Decoder.extractWithRegex('<p class="date ', "</p>", body)
		body = body.replace(dates,"")
		body = body.replace(lastUpdate, "")
	elif '<figcaption class="sp-media-asset' in htmlContent:
		body = Decoder.extract('<figcaption class="sp-media-asset', '</p><div ', htmlContent)
		if '>' in body:
			body = body[body.find(">") + 1:]
	body = Decoder.removeHTML(body).replace(".", ".\n").replace(">", "")
	logger.debug("body is: " + body)
	drawNew(textContent=(body))

def drawNew(textContent,img=''):
	TypeOfMessage = "t" #text
	NewMessage = textContent
	TempWindow = DefaultWindow(noteType=TypeOfMessage, noteMessage=NewMessage, logo=img)
	TempWindow.doModal()
	del TempWindow

def drawFilmonLinks(url, page, provider=""):
	finalUrls = Filmoncom.getChannelUrl(url)
	for finalUrl in finalUrls:
		add_dir(page+", "+finalUrl["name"],finalUrl["url"],2,provider,page)
		#print("page: "+page+", url: "+finalUrl["url"])


def drawPeliculasBiz(url,page):
	finalUrls = Peliculasbiz.getChannels(page)
	for element in finalUrls:
		code = 4
		if element.has_key("finalLink"):
			code = 123
		image = icon
		if element.has_key("thumbnail"):
			image = element["thumbnail"]
		add_dir(element["title"], element["link"], code, image, "peliculasbiz", element["link"])

def drawPepecine(url, page):
	finalUrls = Pepecine.getChannels(page)
	for element in finalUrls:
		code = 4
		if element.has_key("finalLink"):
			code = 2
		image = icon
		if element.has_key("thumbnail"):
			image = element["thumbnail"]
		add_dir(element["title"], element["link"], code, image, "pepecine", element["link"])

def displayTeletext(url,page):
	if "antena3.com" in url:
		displayAntena3Teletext(url, page)
	elif "lasexta.com" in url:
		displayLaSextaTeletext(url, page)
	elif "rtve.es" in url:
		displayRTVETeletext(url, page)
	elif "bbc1" in url:
		displayBBCTeletext(url=url, page=page, version='1')
	elif "bbc2" in url:
		displayBBCTeletext(url=url, page=page, version='2')
	else:
		add_dir("Rtve.es", "rtve.es", 4, "rtve.es", "teletext", 0)
		add_dir("Antena3.com", "antena3.com", 4, "antena3.com", "teletext", 0)
		add_dir("LaSexta.com", "lasexta.com", 4, "lasexta.com", "teletext", 0)
		#add_dir("BBC1 - ceefax.tv", "bbc1", 4, "bbc1", "teletext", 0)
		#add_dir("BBC2 - ceefax.tv", "bbc2", 4, "bbc2", "teletext", 0)

def displayClan(url,page):
	finalUrls = Clan.getChannels(page)
	for element in finalUrls:
		code = 4
		if element.has_key("finalLink"):
			code = 125
		image = icon
		if element.has_key("thumbnail"):
			image = element["thumbnail"]
		add_dir(element["title"], element["link"], code, image, "clan", element["link"])

def displayRTVE(url,page):
	finalUrls = RTVEAlaCarta.getChannels(page)
	for element in finalUrls:
		code = 4
		if element.has_key("finalLink"):
			code = 125
		image = icon
		if element.has_key("thumbnail"):
			image = element["thumbnail"]
		add_dir(element["title"], element["link"], code, image, "rtvealacarta", element["link"])

def drawTuMejorTorrent(page):
	jsonChannels = TuMejorTorrent.getChannels(page)
	for item in jsonChannels:
		mode = 4
		title = item["title"]
		link = item["link"]
		if item.has_key("finalLink"):
			mode = 126
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: " + image)
		else:
			image = icon
		add_dir(title, link, mode, image, "tumejortorrent", link)

def drawMejorTorrent(page):
	jsonChannels = MejorTorrent.getChannels(page)
	for item in jsonChannels:
		mode = 4
		title = item["title"]
		link = item["link"]
		if 'secciones.php' in link and '&p=' not in link:
			mode = 127
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: " + image)
		else:
			image = icon
		add_dir(title, link, mode, image, "mejortorrent", link)

def displayRTVETeletext(url,page):
	logger.debug("displaying teletext for LaSextaText provider")
	imgPath = 'http://www.rtve.com/television/teletexto/100/100_0001.png' #first
	x = RTVE.getChannels(page)
	for element in x:
		if element.has_key("thumbnail"): #displayed thumbnail
			imgPath = element["thumbnail"]
		else:#continue
			add_dir(element["title"],element["link"], 4, element["link"], "teletext", element["link"])
	#finally show img (before render, xbmc will wait until some event happens)
	displayImg(imgPath)

def displayLaSextaTeletext(url,page):
	logger.debug("displaying teletext for LaSextaText provider")
	imgPath = 'http://www.lasexta.com/teletexto/datos/100/100_0001.png' #first
	x = LaSexta.getChannels(page)
	for element in x:
		if element.has_key("thumbnail"): #displayed thumbnail
			imgPath = element["thumbnail"]
		else:#continue
			add_dir(element["title"],element["link"], 4, element["link"], "teletext", element["link"])
	#finally show img (before render, xbmc will wait until some event happens)
	displayImg(imgPath)

def displayAntena3Teletext(url,page):
	logger.debug("displaying teletext for Antena3Text provider")
	imgPath = 'http://www.antena3.com/teletexto/100/100_0001.png' #first
	x = Antena3.getChannels(page)
	for element in x:
		if element.has_key("thumbnail"): #displayed thumbnail
			imgPath = element["thumbnail"]
		else: #continue
			add_dir(element["title"],element["link"], 4, element["link"], "teletext", element["link"])
	#finally show img (before render, xbmc will wait until some event happens)
	displayImg(imgPath)

def displayBBCTeletext(url,page,version):
	logger.debug("displaying teletext for BBC1 provider")
	imgPath = 'http://www.ceefax.tv/cgi-bin/gfx.cgi?font=big&channel=bbc'+version+'&page=100_0'  # first
	if '.search' in url:
		keyboard = XBMCUtils.getKeyboard()
		keyboard.doModal()
		text = ""
		if (keyboard.isConfirmed()):
			text = keyboard.getText()
			imgPath = imgPath[:imgPath.rfind('100_')]+text+'_0'
	imgPath = 'http://anonymous-images-proxy.com/proxy.php?url='+urllib.quote(imgPath)
	add_dir('bbc'+version+'.search','bbc'+version+'.search', 4, 'bbc'+version+'teletext.search', 'teletext', 'bbc'+version+'teletext.search')
	# finally show img (before render, xbmc will wait until some event happens)
	displayImg(imgPath)

def displayImg(imgPath):
	import xbmcgui
	window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
	window.setProperty('imagePath', imgPath)
	display = windowImage()
	display.doModal()
	del display

def decodeAndOpenLink(url,page):
    logger.info("decoding: " + url)
    link = Decoder.decodeLink(url)
    logger.info("decoded: " + link)
    open(link, page)

def openVipgoalLink(url,page):
    jsonChannels = Vigoal.getChannels(page)
    url = jsonChannels[0]["link"]
    logger.info("found link: " + url + ", launching...")
    play(url, page)  # same that 2, but reserved for rtmp

def openCricFreeLink(url,page):
    channel = Cricfreetv.getChannels(page)
    logger.info("found link: " + channel[0]["link"] + ", launching...")
    play(channel[0]["link"], page)

def openSkylineLink(url,page):
	channel = Skylinewebcamscom.getChannels(page, True)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	play(channel[0]["link"], page)

def openSpliveLink(url,page,provider):
	if url.find(".m3u8") == -1 and url.find("rtmp://") == -1:
		channel = Spliveappcom.decodeUrl(url, provider)
		link = channel[0]["link"]
		if link.find(", referer:") > -1:
			link = link[0:link.find(", referer:")]
		url = link
	else:
		logger.debug("nothing decoded for splive encrypted channels, continue...")

	logger.debug("splive BRUTE logic for url: " + url)

	link = url

	logger.info("found link: " + link + ", launching...")
	play(link, page)

def openMamahdLink(url,page):
	channel = Mamahdcom.getChannels(url)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	play(channel[0]["link"], page)

def openTvporinternetnet(url,page):
	channel = Tvporinternetnet.getChannels(url)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	play(channel[0]["link"], page)

def openVercanalestv(url,page):
	channel = Vercanalestv1com.getChannels(url)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	play(channel[0]["link"], page)

def openYoutubeLink(url,page): #could be replaced by decodeAndOpenLink, traces are the unique difference
	logger.info("decoding youtube link... " + url)
	link = Decoder.decodeLink(url)
	logger.info("decoded youtube link: " + link)
	play(link, page)

def openTuneInLink(url,page):
	logger.info("decoding tunein link... " + url)
	link = TuneIn.getChannels(url)[0]["link"].strip()
	logger.info("decoded tunein link: " + link)
	play(link, page)

def openAtresplayer(url,page):
	logger.info("decoding atresplayer link... " + url)
	link = Atresplayer.getChannels(url)[0]["link"].strip()
	logger.info("decoded atresplayer link: " + link)
	play(link, page)

def openRojadirecta(url,page):
	logger.info("decoding rojadirecta link... %s" % url)
	link = Rojadirecta.getChannels(url)[0]["link"].strip()
	logger.info("decoded rojadirecta link: %s" % link)
	play(link, page)

def openPeliculasbiz(url,page):
	logger.info("decoding peliculasbiz link... " + url)
	link = Peliculasbiz.getChannels(url)[0]["link"]
	logger.info("decoded peliculasbiz link: " + link)
	play(link, page)

def openElitetorrentnet(url,page):
	logger.info("decoding eliteetorrentnet link... " + url)
	link = Elitetorrent.getChannels(url,decode=True)[0]["link"]
	logger.info("decoded eliteetorrentnet link: " + link)
	play(link, page)

def openTuMejorTorrent(url,page):
	logger.info("decoding tumejortorrent link... " + url)
	link = url
	if ".torrent" not in url:
		link = TuMejorTorrent.getChannels(url)[0]["link"]
		logger.debug("provisional link is: "+link)
		if ".torrent" not in link:
			link = TuMejorTorrent.getChannels(link)[0]["link"]
			logger.info("decoded two times tumejortorrent link: " + link)
		logger.info("decoded tumejortorrent link: " + link)
	play(link, page)

def openMejorTorrent(url,page):
	logger.info("decoding mejortorrent link... " + url)
	link = MejorTorrent.getChannels(url)[0]["link"]
	logger.info("decoded mejortorrent link: " + link)
	play(link, page)

def openClan(url,page):
	logger.info("decoding Clan link... " + url)
	link = Clan.getChannels(url)[0]["link"]
	logger.info("decoded Clan link: " + link)
	play(link, page)

def openMobdro(url,page):
	try:
		link = base64.decodestring(url)
	except:
		logger.debug("not a valid base64 content...")
		pass
	logger.info("decoded streamgaroo link: " + link)
	play(link, page)

def openElgolesme(url,page):
	logger.info("decoding Elgolesme link... " + url)
	link = Elgolesme.getChannels(url)[0]["link"]
	logger.info("decoded Elgolesme link: " + link)
	play(link, page)

def isAnException(url,page,provider,mode):
	state = False
	if mode == 4 and (provider=="bbccouk" and str(page) == '0' and ".xml" not in url) \
			or (str(page)=='1' and provider=='reuters')\
			or (str(page)!='0' and provider=='editioncnn') \
			or (str(page) != '0' and provider == 'editionelpais') \
			or (str(page)!='0' and provider=='editionelmundo'):
		logger.debug("Order don't reload page -> provider: "+provider)
		state = True
	if state:
		logger.debug("Dont reload view. Params -> page: "+page+", url: "+url+", provider: "+provider+", mode: "+str(mode))
	return state
