# -*- coding: utf-8 -*-

import urllib
import sys

import re
import platform

from tvboxcore.xbmcutils import XBMCUtils
from tvboxcore import logger
from tvboxcore.listsParsers import * #xml parsers
from tvboxcore.addonUtils import * #drawers
from tvboxcore.providersUtils import * #renders

def get_main_dirs():

	##CONSTANTS PARTS##
	MAIN_URL = XBMCUtils.getSettingFromContext(sys.argv[1], "remote_repository")
	BROWSE_CHANNELS = "browse_channels"
	ICON = XBMCUtils.getAddonFilePath('icon.png')

	#draw welcome menu
	add_dir(XBMCUtils.getString(10001), MAIN_URL, 1, ICON,'', 0)
	add_dir(XBMCUtils.getString(10010), BROWSE_CHANNELS, 3, '', ICON, 0)
	try:
		from window.ImageWindow import windowImage  # teletext window library
		add_dir(name=XBMCUtils.getString(10012), url='teletext', mode=4, provider='teletext', page=0,thumbnailImage="",iconimage=ICON)
	except:
		logger.info("No PIL module installed (needs Pillow 3.4.2 or less)")
		pass
	#add_dir(XBMCUtils.getString(10014), 'paidonline', 3, "", 'paidonline', 0)
	#add_dir(XBMCUtils.getString(10015), 'programsonline', 3, "", 'programsonline', 0)
	try:
		if updater.isUpdatable():
			add_dir(XBMCUtils.getString(10011), '', 0, ICON, 0)
	except:
		logger.error("Couldn't add update option: probably server is down!")
		pass

def browse_channels(url,page): #BROWSES ALL PROVIDERS (it has been re-sorted)
	if str(url)=='browse_channels':
		add_dir(XBMCUtils.getString(10016), 'popularonline', 3, "", 'popularonline', 0)
		#add_dir(XBMCUtils.getString(10017), 'tvseriesonline', 3, "", 'tvseriesonline', 0)
		#add_dir(XBMCUtils.getString(10018), 'torrentwebsites', 3, "", 'torrentwebsites', 0)
		#add_dir(XBMCUtils.getString(10019), 'usersonlinewebsites', 3, "", 'usersonlinewebsites', 0)
		add_dir(XBMCUtils.getString(10020), 'sportsonline', 3, "", 'sportsonline', 0)
		#add_dir(XBMCUtils.getString(10021), 'newsonlinewebsites', 3, "", 'newsonlinewebsites', 0)
		add_dir(XBMCUtils.getString(10022), 'worldstvonlinewebsites', 3, "", 'worldstvonlinewebsites', 0)
		#add_dir(XBMCUtils.getString(10023), 'listsonlinewebsites', 3, "", 'listsonlinewebsites', 0)
		#add_dir(XBMCUtils.getString(10024), 'webcamsonlinewebsites', 3, "", 'webcamsonlinewebsites', 0)
		#add_dir(XBMCUtils.getString(10025), 'otherssonlinewebsites', 3, "", 'otherssonlinewebsites', 0)
	else:
		enableNews = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_news")
		enablePlexus = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_plexus")
		enableMobdro = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_mobdro")
		enableSplive = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_splive")
		patchedFfmpeg = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "ffmpeg_patch")
		enableDinamic = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_pastebin")

		#if str(url)=='tvseriesonline':
		#	add_dir("HDFull.tv", 'hdfulltv', 4, "http://hdfull.tv/templates/hdfull/images/logo.png", 'hdfulltv', 0)
		#	add_dir("Peliculasid.cc", 'peliculasbiz', 4, "", 'peliculasbiz', 0)
		#	add_dir("Pepecine.com", 'pepecine', 4, "http://pepecine.net/assets/images/logo.png", 'pepecine', 0)
		#	if enablePlexus:
		#		add_dir("[T] - Elitetorrent.biz", 'elitetorrentnet', 4, "https://www.elitetorrent.biz/wp-content/themes/EliteTorrent/css/images/logo.png",'elitetorrentnet', 0)
		#		add_dir("[T] - TuMejorTorrent.net", 'tumejortorrent', 4,"http://tumejortorrent.com/pct1/library/content/template/images/tmt_logo.jpg", 'tumejortorrent', 0)
		#		add_dir("[T] - MejorTorrent.org", 'mejortorrent', 4,"http://www.mejortorrent.org/imagenes_web/cabecera.jpg", 'mejortorrent', 0)
		if str(url)=='popularonline':
			#add_dir("Youtube.com", 'youtube', 4,"https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/YouTube_logo_2015.svg/120px-YouTube_logo_2015.svg.png",'youtube', 0)
			add_dir("RTVE AlaCarta", 'rtvealacarta', 4,"https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Logo_RTVE.svg/150px-Logo_RTVE.svg.png",'rtvealacarta', 0)
			add_dir("CLAN (rtve)", 'clan', 4,"https://upload.wikimedia.org/wikipedia/en/thumb/4/47/TVEClan_logo.png/150px-TVEClan_logo.png",'clan', 0)
			add_dir("TuneIn.com", 'tunein', 4,"https://lh5.googleusercontent.com/-NsniPTwZFkc/AAAAAAAAAAI/AAAAAAAAOLE/qtdbWIxlF5M/s0-c-k-no-ns/photo.jpg",'tunein', 0)
			add_dir("Atresplayer.com", 'atresplayer', 4,"https://statics.atresmedia.com/atresplayer/assets/web/icon-192x192.png",'atresplayer', 0)
		#elif str(url) == 'programsonline':
		#	if enableSplive == "true":
		#		add_dir("Spliveapp.com", 'splive', 4, "http://www.spliveapp.com/main/wp-content/uploads/footer_logo.png",'splive', 0)
		#	if enableMobdro == 'true':
		#		add_dir("Mobdro.com", 'mobdro', 4, "https://www.mobdro.com/favicon.ico", 'mobdro', 0)
		#elif str(url)=='torrentwebsites'and enablePlexus == "true":
		#	add_dir("Arenavision.in", 'arenavisionin', 4, "http://www.arenavision.in/sites/default/files/logo_av2015.png",'arenavisionin', 0)
		#	add_dir("Ace-tv.ru", 'acetvru', 4, "http://ace-tv.eu/logo.png", 'acetvru', 0)
		elif str(url)=='sportsonline':
			add_dir("Dailysport.pw", 'dailysport', 4, "", 'dailysport', 0)
			#add_dir("Cricfree.tv", 'cricfree', 4, "http://cricfree.tv/images/logosimg.png", 'cricfree', 0)
			#add_dir("Mamahd.com", 'mamahdcom', 4, "http://mamahd.com/images/logo.png", 'mamahdcom', 0)
			#add_dir("Elgoles.me", 'elgolesme', 4, "http://elgoles.me/elgoles3.png", 'elgolesme', 0)
			add_dir("rojadirecta.(unblocker.cc)", 'rojadirecta', 4, "http://rojadirecta.unblocker.cc/static/roja.jpg", 'rojadirecta', 0)
		#elif str(url)=='newsonlinewebsites' and enableNews == "true":
		#	add_dir("Bbc.co.uk", 'bbccouk', 4, "", 'bbccouk', 'http://feeds.bbci.co.uk/news/rss.xml?edition=int')
		#	add_dir("Reuters.com", 'reuters', 4, "http://www.thewrap.com/wp-content/uploads/2013/10/Reuters-Logo.jpg",'reuters', 0)
		#	add_dir("CNN.com", 'editioncnn', 4, "http://i.cdn.cnn.com/cnn/.e1mo/img/4.0/logos/logo_cnn_badge_2up.png",'editioncnn', 0)
		#	add_dir("ElMundo.es", 'editionelmundo', 4, "http://estaticos.elmundo.es/imagen/canalima144.gif",'editionelmundo', 0)
		#	add_dir("ElPais.es", 'editionelpais', 4, "http://ep01.epimg.net/corporativos/img/elpais2.jpg",'editionelpais', 0)
		elif str(url)=='worldstvonlinewebsites':
			add_dir("Filmon.com", 'filmon', 4, "http://static.filmon.com/theme/img/filmon_small_logo.png", 'filmoncom', 0)
			add_dir("Vercanalestv1.com", 'vercanalestv', 4, "https://vercanalestv1.com/wp-content/uploads/2014/01/vercanalestv4.png", 'vercanalestv', 0)
			#add_dir("Tvpor-internet.net", 'tvporinternetnet', 4, "http://tvpor-internet.net/theme/img/woot.png", 'tvporinternetnet', 0)
		#elif str(url)=='listsonlinewebsites':
		#	add_dir("Ramalin.com", 'ramalin', 4, "http://websites-img.milonic.com/img-slide/420x257/r/ramalin.com.png",'ramalin', 0)
		#	if enableDinamic == "true":
		#		add_dir("Pastebin.com", 'pastebincom', 4, "", 'pastebincom', 0)
		#	add_dir("Redeneobux.com", 'redeneobuxcom', 4, "", 'redeneobuxcom', 0)
		#elif str(url)=='webcamsonlinewebsites':
		#	add_dir("Skylinewebcams.com", 'skylinewebcams', 4, "http://www.skylinewebcams.com/website.jpg",'skylinewebcams', 0)
		#elif str(url)=='otherssonlinewebsites':
		#	if patchedFfmpeg == "true":
		#		add_dir("Vipgoal.me", 'vigoal', 4, "https://2.bp.blogspot.com/-I8bndGrJcio/W8EFr_igJtI/AAAAAAAADzc/jeO495i1CaMbsK7YTH8jwvc1VR-UJsfxgCLcBGAs/s1600/vipgoal4.png", 'vigoal', 0)


def browse_channel(url,page,provider): #MAIN TREE BROWSER IS HERE!
	if provider == "filmoncom":
		drawFilmon(page)
	elif provider == 'vercanalestv':
		drawVercanalestv(page)
	elif provider== "hdfulltv":
		drawHdfulltv(page)
	elif provider == "peliculasbiz":
		drawPeliculasBiz(url,page)
	elif provider == 'pepecine':
		drawPepecine(url, page)
	elif provider == "vigoal":
		drawVipgoal(page)
	elif provider == "cricfree":
		drawCricfree(page)
	elif provider == 'skylinewebcams':
		drawSkylinewebcams(page)
	elif provider == 'splive':
		drawSplive(page)
	elif provider == 'mamahdcom':
		drawMamahdcom(page)
	elif provider == 'elgolesme':
		drawElgolesme(page)
	elif provider == 'tvporinternetnet':
		drawTvporinternetnet(page)
	elif provider == 'arenavisionin':
		drawArenavisionin(page)
	elif provider == 'acetvru':
		drawAcetvru(page)
	elif provider == 'elitetorrentnet':
		drawElitetorrentnet(page)
	elif provider == 'tumejortorrent':
		drawTuMejorTorrent(page)
	elif provider == 'mejortorrent':
		drawMejorTorrent(page)
	elif provider == 'youtube':
		drawYoutube(page)
	elif provider == 'pastebincom':
		drawPastebinCom()
	elif provider == 'redeneobuxcom':
		drawRedeneobuxCom(page)
	elif provider == 'bbccouk':
		if str(page)=='0':
			page = url
		drawNews(url=page,provider=provider,targetAction=4)
	elif provider == "reuters":
		logger.debug("page: "+page+", url: "+url)
		if str(page) == '1':
			page = url
		drawReutersNews(url=page)
	elif provider =='editioncnn':
		drawCNNNews(url=page)
	elif provider =='editionelmundo':
		drawElMundoNews(url=page)
	elif provider =='editionelpais':
		drawElPaisNews(url=page)
	elif provider == "tunein":
		drawTuneIn(page)
	elif provider == 'atresplayer':
		drawAtresplayer(page)
	elif provider == 'rojadirecta':
		drawRojadirecta(page)
	elif provider == 'ramalin':
		drawRamalin(page)
	elif provider == 'mobdro':
		drawMobdro(page)
	elif provider == 'teletext':
		displayTeletext(url, page)
	elif provider == 'clan':
		displayClan(url, page)
	elif provider == 'rtvealacarta':
		displayRTVE(url, page)
	elif provider == 'dailysport':
		displayDailySport(url, page)

	logger.info(provider)

def init():
	params=get_params()

	url=""
	mode=None
	page=""
	provider = ""

	try:
		page=urllib.unquote_plus(params["page"])
	except:
		pass
	try:
		url=urllib.unquote_plus(params["url"])
	except:
		pass
	try:
		mode=int(params["mode"])
	except:
		pass
	try:
		provider=urllib.unquote_plus(params["provider"])
	except:
		pass
	logger.debug("Mode: "+str(mode))
	logger.debug("URL: "+str(url))
	logger.debug("page: "+str(page))
	logger.debug("provider: "+str(provider))
	try:
		if mode==None: #init
			get_main_dirs()
		elif mode==1: #get channels
			getListsUrls(url)
		elif mode == 2: #open video in player
			play(url,page)
		elif mode == 3:
			browse_channels(url,page)
		elif mode == 4:
			browse_channel(url,page,provider)
		elif mode == 5:
			drawFilmonLinks(url, page)
		elif mode == 0: #update
			addonUpdater()
			get_main_dirs()
		elif mode == 97:
			httpProxyUpdater()
		elif mode == 98:
			quasarUpdater()
		elif mode == 99:
			plexusUpdater()
		elif mode == 100: #decode provider link
			decodeAndOpenLink(url,page)
		elif mode == 101:
			openVipgoalLink(url,page)
		elif mode == 103:
			openCricFreeLink(url,page)
		elif mode == 108:
			openSkylineLink(url,page)
		elif mode == 111:
			openSpliveLink(url,page,provider)
		elif mode == 112:
			openMamahdLink(url,page)
		elif mode == 114:
			#openArenavisionLink(url,page) #clean
			pass
		elif mode == 115:
			openYoutubeLink(url,page)
		elif mode == 117:
			drawFilmonLinks(url,page)
		elif mode == 118:
			openTuneInLink(url,page)
		elif mode == 122:
			openMobdro(url,page)
		elif mode == 123:
			openPeliculasbiz(url,page)
		elif mode == 124:
			openElitetorrentnet(url,page)
		elif mode == 125:
			openClan(url,page)
		elif mode == 126:
			openTuMejorTorrent(url,page)
		elif mode == 127:
			openMejorTorrent(url,page)
		elif mode == 128:
			openTvporinternetnet(url,page)
		elif mode == 129:
			openVercanalestv(url,page)
		elif mode == 130:
			openElgolesme(url,page)
		elif mode == 131:
			openAtresplayer(url,page)
		elif mode == 132:
			openRojadirecta(url,page)
		elif mode == 133:
			openDailySport(url,page)

	except Exception as e:
		logger.error(XBMCUtils.getString(10009)+", "+str(e))
		XBMCUtils.getNotification("Error",XBMCUtils.getString(10009))
		pass
	if not isAnException(url,page,provider,mode):
		logger.debug("End of main menu to be displayed. Params -> page: "+page+", url: "+url+", provider: "+provider+", mode: "+str(mode))
		XBMCUtils.setEndOfDirectory(int(sys.argv[1]))

init()
