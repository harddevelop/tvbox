# -*- coding: utf-8 -*-

import urllib
import sys

import re
import platform

from core.xbmcutils import XBMCUtils
from core import logger
from core.listsParsers import * #xml parsers
from core.addonUtils import * #drawers
from core.providersUtils import * #renders

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
	add_dir(XBMCUtils.getString(10014), 'paidonline', 3, "", 'paidonline', 0)
	add_dir(XBMCUtils.getString(10015), 'programsonline', 3, "", 'programsonline', 0)
	try:
		if updater.isUpdatable():
			add_dir(XBMCUtils.getString(10011), '', 0, ICON, 0)
	except:
		logger.error("Couldn't add update option: probably server is down!")
		pass

def browse_channels(url,page): #BROWSES ALL PROVIDERS (it has been re-sorted)
	if str(url)=='browse_channels':
		add_dir(XBMCUtils.getString(10016), 'popularonline', 3, "", 'popularonline', 0)
		add_dir(XBMCUtils.getString(10017), 'tvseriesonline', 3, "", 'tvseriesonline', 0)
		add_dir(XBMCUtils.getString(10018), 'torrentwebsites', 3, "", 'torrentwebsites', 0)
		#add_dir(XBMCUtils.getString(10019), 'usersonlinewebsites', 3, "", 'usersonlinewebsites', 0)
		add_dir(XBMCUtils.getString(10020), 'sportsonline', 3, "", 'sportsonline', 0)
		add_dir(XBMCUtils.getString(10021), 'newsonlinewebsites', 3, "", 'newsonlinewebsites', 0)
		add_dir(XBMCUtils.getString(10022), 'worldstvonlinewebsites', 3, "", 'worldstvonlinewebsites', 0)
		add_dir(XBMCUtils.getString(10023), 'listsonlinewebsites', 3, "", 'listsonlinewebsites', 0)
		add_dir(XBMCUtils.getString(10024), 'webcamsonlinewebsites', 3, "", 'webcamsonlinewebsites', 0)
		add_dir(XBMCUtils.getString(10025), 'otherssonlinewebsites', 3, "", 'otherssonlinewebsites', 0)
	else:
		enableNews = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_news")
		enablePlexus = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_plexus")
		enableMobdro = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_mobdro")
		enableSplive = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_splive")
		patchedFfmpeg = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "ffmpeg_patch")
		enableDinamic = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_pastebin")

		if str(url)=='tvseriesonline':
			add_dir("HDFull.tv", 'hdfulltv', 4, "http://hdfull.tv/templates/hdfull/images/logo.png", 'hdfulltv', 0)
			add_dir("Peliculasid.cc", 'peliculasbiz', 4, "", 'peliculasbiz', 0)
			add_dir("Pepecine.com", 'pepecine', 4, "http://pepecine.net/assets/images/logo.png", 'pepecine', 0)
			if enablePlexus:
				#add_dir("[T] - Elitetorrent.net", 'elitetorrentnet', 4, "http://www.elitetorrent.net/images/logo_elite.png",'elitetorrentnet', 0)
				add_dir("[T] - TuMejorTorrent.net", 'tumejortorrent', 4,"http://tumejortorrent.com/pct1/library/content/template/images/tmt_logo.jpg", 'tumejortorrent', 0)
				add_dir("[T] - MejorTorrent.net", 'mejortorrent', 4,"http://www.mejortorrent.com/imagenes_web/cabecera.jpg", 'mejortorrent', 0)
		elif str(url)=='popularonline':
			add_dir("Youtube.com", 'youtube', 4,"https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/YouTube_logo_2015.svg/120px-YouTube_logo_2015.svg.png",'youtube', 0)
			add_dir("RTVE AlaCarta", 'rtvealacarta', 4,"https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Logo_RTVE.svg/150px-Logo_RTVE.svg.png",'rtvealacarta', 0)
			add_dir("CLAN (rtve)", 'clan', 4,"https://upload.wikimedia.org/wikipedia/en/thumb/4/47/TVEClan_logo.png/150px-TVEClan_logo.png",'clan', 0)
			add_dir("TuneIn.com", 'tunein', 4,"https://lh5.googleusercontent.com/-NsniPTwZFkc/AAAAAAAAAAI/AAAAAAAAOLE/qtdbWIxlF5M/s0-c-k-no-ns/photo.jpg",'tunein', 0)
		elif str(url)=='paidonline':
			enableYomvi = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "enable_yomvi")
			if enableYomvi == "true":
				add_dir("Yomvi.es", 'yomvies', 4, "http://ver.movistarplus.es/img/logo-web-player-YOMVI.png", 'yomvies', 0)
		elif str(url) == 'programsonline':
			if enableSplive == "true":
				add_dir("Spliveapp.com", 'splive', 4, "http://www.spliveapp.com/main/wp-content/uploads/footer_logo.png",'splive', 0)
			if enableMobdro == 'true':
				add_dir("Mobdro.com", 'mobdro', 4, "https://www.mobdro.com/favicon.ico", 'mobdro', 0)
		elif str(url)=='torrentwebsites'and enablePlexus == "true":
			add_dir("Arenavision.in", 'arenavisionin', 4, "http://www.arenavision.in/sites/default/files/logo_av2015.png",'arenavisionin', 0)
			add_dir("Acesoplisting.in", 'acesoplistingin', 4, "http://acesoplisting.in/images/acesop.gif", 'acesoplistingin', 0)
			add_dir("Ace-tv.ru", 'acetvru', 4, "http://ace-tv.eu/logo.png", 'acetvru', 0)
		#elif str(url)=='usersonlinewebsites':
			#add_dir("Tvshow.me", 'tvshowme', 4, "http://www.tvshow.me/wp-content/uploads/2016/09/Icon_.png", 'tvshowme', 0)
		elif str(url)=='sportsonline':
			add_dir("Live9.co", 'live9', 4, "", 'live9', 0)
			add_dir("Cricfree.tv", 'cricfree', 4, "http://cricfree.tv/images/logosimg.png", 'cricfree', 0)
			add_dir("Mamahd.com", 'mamahdcom', 4, "http://mamahd.com/images/logo.png", 'mamahdcom', 0)
			add_dir("Vipracing.net", 'vipracinginfo', 4, "", 'vipracinginfo', 0)
			add_dir("Zonasports.me", 'zonasportsme', 4, "http://i.imgur.com/yAuKRZw.png", 'zonasportsme', 0)
		elif str(url)=='newsonlinewebsites' and enableNews == "true":
			add_dir("Bbc.co.uk", 'bbccouk', 4, "", 'bbccouk', 'http://feeds.bbci.co.uk/news/rss.xml?edition=int')
			add_dir("Reuters.com", 'reuters', 4, "http://www.thewrap.com/wp-content/uploads/2013/10/Reuters-Logo.jpg",'reuters', 0)
			add_dir("CNN.com", 'editioncnn', 4, "http://i.cdn.cnn.com/cnn/.e1mo/img/4.0/logos/logo_cnn_badge_2up.png",'editioncnn', 0)
			add_dir("ElMundo.es", 'editionelmundo', 4, "http://estaticos.elmundo.es/imagen/canalima144.gif",'editionelmundo', 0)
			add_dir("ElPais.es", 'editionelpais', 4, "http://ep01.epimg.net/corporativos/img/elpais2.jpg",'editionelpais', 0)

		elif str(url)=='worldstvonlinewebsites':
			add_dir("Filmon.com", 'filmon', 4, "http://static.filmon.com/theme/img/filmon_small_logo.png", 'filmoncom', 0)
			add_dir("Streamgaroo.com", 'streamgaroo', 4, "http://www.streamgaroo.com/images/logo.png", 'streamgaroo', 0)
		elif str(url)=='listsonlinewebsites':
			add_dir("Ramalin.com", 'ramalin', 4, "http://websites-img.milonic.com/img-slide/420x257/r/ramalin.com.png",'ramalin', 0)
			if enableDinamic == "true":
				add_dir("Pastebin.com", 'pastebincom', 4, "", 'pastebincom', 0)
			add_dir("Redeneobux.com", 'redeneobuxcom', 4, "", 'redeneobuxcom', 0)
		elif str(url)=='webcamsonlinewebsites':
			add_dir("Skylinewebcams.com", 'skylinewebcams', 4, "http://www.skylinewebcams.com/website.jpg",'skylinewebcams', 0)
		elif str(url)=='otherssonlinewebsites':
			if patchedFfmpeg == "true":
				add_dir("Cinestrenostv.tv", 'cineestrenos', 4, "http://i.imgur.com/z3CINCU.jpg", 'cineestrenos',0)
				add_dir("Vipgoal.net", 'vigoal', 4, "http://vipgoal.net/VIPgoal/img/logo.png", 'vigoal', 0)

	#sports with event
	#add_dir("Sportstream365.com", 'sportstream365com', 4, "http://sportstream365.com/img/logo.png", 'sportstream365com' , 0)

	#world tv

	#add_dir("Youtvgratis.com", 'youtvgratis', 4, "http://youtvgratis.com/themes/tutvplayer/img/logo.gif", 'youtvgratis', 0)
	#add_dir("Zoptv.com", 'zoptv', 4, "http://www.zoptv.com/images/logo.png", 'zoptv' , 0)

	#add_dir("Sports4u.tv", 'sports4u', 4, "http://live.sports4u.tv/wp-content/uploads/logo3.png", 'sports4u' , 0)
	#add_dir("Showsport-tv.com", 'showsporttvcom', 4, "http://showsport-tv.com/images/logoh.png", 'showsporttvcom', 0)

	#add_dir("Zona-app.com", 'zonaappcom', 4, "", 'zonaappcom', 0)
	#static streaming lists
	#add_dir("Hdfullhd.eu", 'hdfullhdeu', 4, "", 'hdfullhdeu' , 0)

def browse_channel(url,page,provider): #MAIN TREE BROWSER IS HERE!
	if provider == "filmoncom":
		drawFilmon(page)
	elif provider== "hdfulltv":
		drawHdfulltv(page)
	elif provider == "peliculasbiz":
		drawPeliculasBiz(url,page)
	elif provider == 'pepecine':
		drawPepecine(url, page)
	elif provider == "vigoal":
		drawVipgoal(page)
	elif provider == "cineestrenos":
		drawCinestrenostv(page)
	elif provider == "cricfree":
		drawCricfree(page)
	elif provider == 'zoptv':
		drawZoptv(page)
	elif provider == 'live9':
		drawLive9(page)
	elif provider == 'sports4u':
		drawSports4u(page)
	elif provider == 'vipracinginfo':
		drawVipracinginfo(page)
	elif provider == 'hdfullhdeu':
		drawHdfullhdeu(page)
	elif provider == 'skylinewebcams':
		drawSkylinewebcams(page)
	elif provider == 'zonasportsme':
		drawZonasportsme(page)
	elif provider == 'sportstream365com':
		drawSportstream365(page)
	elif provider == 'splive':
		drawSplive(page)
	elif provider == 'mamahdcom':
		drawMamahdcom(page)
	elif provider == 'showsporttvcom':
		drawShowsporttvcom(page)
	elif provider == 'arenavisionin':
		drawArenavisionin(page)
	elif provider == 'acesoplistingin':
		drawAcesoplistingin(page)
	elif provider == 'acetvru':
		drawAcetvru(page)
	elif provider == 'streamingsport365':
		drawStreamingsport365()
	#elif provider == 'elitetorrentnet':
	#	drawElitetorrentnet(page)
	elif provider == 'tumejortorrent':
		drawTuMejorTorrent(page)
	elif provider == 'mejortorrent':
		drawMejorTorrent(page)
	elif provider == 'youtube':
		drawYoutube(page)
	elif provider == 'zonaappcom':
		drawZonaAppCom()
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
	elif provider == 'youtvgratis':
		drawYoutvgratis(page)
	elif provider == "yomvies":
		drawYomviEs(page)
	elif provider == 'streamgaroo': #<ul class="nav navbar-nav">
		drawStreamgaroo(page)
	elif provider == 'tvshowme':
		drawTvshowme(page)
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
			open(url,page)
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
		elif mode == 102:
			openCineestrenosLink(url,page)
		elif mode == 103:
			openCricFreeLink(url,page)
		elif mode == 104:
			openZopTvLink(url,page)
		elif mode == 105:
			openLive9Link(url,page)
		elif mode == 106:
			openSports4uLink(url,page)
		elif mode == 107:
			openVipracingLink(url,page)
		elif mode == 108:
			openSkylineLink(url,page)
		elif mode == 109:
			openZonasportsLink(url,page)
		elif mode == 110:
			openSports365Link(url,page)
		elif mode == 111:
			openSpliveLink(url,page,provider)
		elif mode == 112:
			openMamahdLink(url,page)
		elif mode == 113:
			openShowsportsLink(url,page)
		elif mode == 114:
			openArenavisionLink(url,page)
		elif mode == 115:
			openYoutubeLink(url,page)
		elif mode == 116:
			openZonaappLink(url,page)
		elif mode == 117:
			drawFilmonLinks(url,page)
		elif mode == 118:
			openTuneInLink(url,page)
		elif mode == 119:
			openYoutvgratisLink(url, page)
		elif mode == 120:
			openYomvies(url,page)
		elif mode == 121:
			openStreamgaroo(url, page)
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


	except Exception as e:
		logger.error(XBMCUtils.getString(10009)+", "+str(e))
		XBMCUtils.getNotification("Error",XBMCUtils.getString(10009))
		pass
	if not isAnException(url,page,provider,mode):
		logger.debug("End of main menu to be displayed. Params -> page: "+page+", url: "+url+", provider: "+provider+", mode: "+str(mode))
		XBMCUtils.setEndOfDirectory(int(sys.argv[1]))

init()