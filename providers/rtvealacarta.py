from tvboxcore.downloader import Downloader
from tvboxcore import logger
from tvboxcore.decoder import Decoder

try:
    import json
except:
    import simplejson as json

class RTVEAlaCarta(Downloader):

	SEARCH = 'http://www.rtve.es/alacarta/interno/buscador'
	MAIN_URL = 'http://www.rtve.es'
	A_LA_CARTA = 'http://www.rtve.es/alacarta/'

	@staticmethod
	def getChannels(page):
		x = []
		if page == '0':
			x = RTVEAlaCarta.getSections()
			pass
		elif RTVEAlaCarta.A_LA_CARTA in page:
			elementPage = page[len(RTVEAlaCarta.A_LA_CARTA):]
			logger.debug("subPage is: " + elementPage)
			x = RTVEAlaCarta.getSection(page)
			if '/' in elementPage:
				logger.debug("analysing... ")
				# channel part
			else:
				logger.debug("analysing 2...")
				pass
			#chapter or video part part
		return x

	@staticmethod
	def search():
		x = []
		referer = RTVEAlaCarta.MAIN_URL+"/alacarta/tve/la1/"
		bruteJson = RTVEAlaCarta.getContentFromUrl(url=RTVEAlaCarta.SEARCH,referer=referer)
		items = json.loads(bruteJson)
		for item in items["items"]:
			title = item["text"]
			url = item["url"]
			logger.debug("item is: "+title+", url: "+url)
			element = {}
			element["title"] = title
			element["link"] = url
			x.append(element)
		return x
		
	@staticmethod
	def getSections():
		x = []
		html = RTVEAlaCarta.getContentFromUrl(url=RTVEAlaCarta.A_LA_CARTA)
		content = Decoder.extract('<div class="wrapper-canales mark">','<div class="mark">',html)
		for line in content.split('<a '):
			if 'href=' in line:
				link = Decoder.extract('href="','"',line)
				if '/alacarta' in link:
					link = RTVEAlaCarta.MAIN_URL+link
					title = Decoder.extract('href="','</a',line)
					title = title.replace('<strong>','')
					title = title.replace('</strong>','')
					title = title[title.rfind(">")+1:]
					logger.debug("Appending '"+title+"', '"+link+"'")
					element = {}
					element["title"] = title
					sublink = ''
					if RTVEAlaCarta.A_LA_CARTA in link:
						sublink = link[len(RTVEAlaCarta.A_LA_CARTA):]
						logger.debug("sublink 1 is: "+sublink)
						sublink = Decoder.extract('/',"/",sublink)
						logger.debug("sublink 2 is: " + sublink)
						link=RTVEAlaCarta.A_LA_CARTA+"programas/"+sublink+"/todos/1/"
						logger.debug("new link is: "+link+", from: "+sublink)
					element["link"] = link
					if len(sublink)>0:
						x.append(element)
		return x
		
	@staticmethod
	def getSection(url):
		x = []
		url = url.replace("&amp;","&")
		html = RTVEAlaCarta.getContentFromUrl(url=url,referer=RTVEAlaCarta.A_LA_CARTA)
		content = Decoder.rExtract('</ul><div class="ContentTabla">','<div class="pagbox mark">',html)
		if ' class="anterior">' in html:
			logger.debug("'anterior' FOUND!")
			if '" class="anterior">' not in html:
				html2 = Decoder.extract(' class="anterior">', "</li>", html)
			else:
				html2 = Decoder.extract('" class="anterior">', "</li>", html)
			link = Decoder.extract('href="', '"', html2)
			if "<span>" in html2:
				title = Decoder.extract('<span>', '</span>', html2)
			else: #title is in other part, so it's needed more html
				html2 = Decoder.rExtract("<li",'" class="anterior">', html)
				title = Decoder.extract('title="','"',html2)
			element = {}
			if RTVEAlaCarta.MAIN_URL not in link:
				link = RTVEAlaCarta.MAIN_URL + link
			element["link"] = link
			element["title"] = title
			x.append(element)
		if '<!--EMPIEZA TOOL-TIP-->' in content:
			for line in content.split('<!--EMPIEZA TOOL-TIP-->'):
				logger.debug("html line1 is: "+line)
				title = Decoder.extract(' title="Ver programa seleccionado">','<',line)
				link = Decoder.rExtract('<a href=',title+'</a>',line)
				link = Decoder.extract('"','"',link)
				logger.debug("new link is: "+link)
				element = {}
				element["title"] = title
				if RTVEAlaCarta.MAIN_URL not in link:
					link = RTVEAlaCarta.MAIN_URL+link
				logger.debug("title: "+title+", url: "+link)
				element["link"] = link
				x.append(element)
		elif '</li><li class="' in content:
			for line in content.split('</li><li class="'):
				logger.debug("html line2 is: " + line)
				link = Decoder.extract('<a href="', '"', line)
				title = Decoder.extract('/">', '</a>', line).replace("&nbsp;"," ").replace("<em>","").replace("</em>","")
				element = {}
				element["title"] = title
				if RTVEAlaCarta.MAIN_URL not in link:
					link = RTVEAlaCarta.MAIN_URL + link
				logger.debug("title: " + title + ", url: " + link)
				element["link"] = link
				element["finalLink"] = True
				if "</span>" not in title:
                                        logger.debug("title: %s, url: %s"%(title,link))
					x.append(element)
		elif '</li><li class="' in html:
			for line in html.split('</li><li class="'):
				logger.debug("html line3 is: " + line)
				link = Decoder.extract('<a href="', '"', line)
				title = Decoder.extract('/">', '</a>', line).replace("&nbsp;", " ").replace("<em>", "").replace("</em>",
																												"")
				element = {}
				element["title"] = title
				if RTVEAlaCarta.MAIN_URL not in link:
					link = RTVEAlaCarta.MAIN_URL + link
				logger.debug("title: " + title + ", url: " + link)
				element["link"] = link
				element["finalLink"] = True
				if "</span>" not in title:
					x.append(element)


		if ' class="siguiente">' in html:
			logger.debug("'siguiente' FOUND!")
			if '" class="siguiente">' not in html:
				html2 = Decoder.extract(' class="siguiente">', "</li>", html)
			else:
				html2 = Decoder.extract('" class="siguiente">', "</li>", html)
			link = Decoder.extract('href="', '"', html2)
			if "<span>" in html2:
				title = Decoder.extract('<span>', '</span>', html2)
			else: #title is in other part, so it's needed more html
				html2 = Decoder.rExtract("<li", '" class="siguiente">', html)
				title = Decoder.extract('title="','"',html2)
			element = {}
			if RTVEAlaCarta.MAIN_URL not in link:
				link = RTVEAlaCarta.MAIN_URL + link
			element["link"] = link
			element["title"] = title
			x.append(element)

		if len(x) == 0:
			#json api
			pageCode = Decoder.extract('/alacarta/interno/contenttable.shtml?ctx=','&',html)
			jsonPage = "http://www.rtve.es/api/programas/%s/videos.json?page=1&size=60" % pageCode
			jsonContent = RTVEAlaCarta.getContentFromUrl(url=jsonPage)
			try:
				jsonObject = json.loads(jsonContent)
				logger.debug("loaded json")
				for item in jsonObject["page"]["items"]:
					logger.debug("item looping...")
					url = item["htmlUrl"]
					title = item["longTitle"]
					element = {}
					element["link"] = url
					element["title"] = title
					try:
						element["thumbnail"] = item["imageSEO"]
					except:
						logger.error("No imageSEO found!")
						pass
					element["finalLink"] = True
					logger.debug("%s %s" % (title,link))
					x.append(element)
			except:
				logger.error("Could not parse JSON from ALACARTA alternative way: "+jsonPage)
		return x
