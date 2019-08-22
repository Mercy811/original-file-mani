from bs4 import BeautifulSoup
import requests
import os
import re

linkFilePath = os.environ['HOME']+"/documents/originalLink/"
textFilePath = os.environ['HOME']+"/documents/englishOriginalFile/"
badFile = []

def myBeautiful(link, fileName):
	print("Scraping from: "+link)
	page = requests.get(link)

	soup = BeautifulSoup(page.content, 'html.parser')

	for script in soup("script"):
		script.decompose()

	title_soup = soup.find("h1", class_="heading")
	english_soup = soup.find("div", class_="article__data")

	try: 
		relatedGroup = soup.find("div", class_="related__group")
		relatedGroup.decompose()
	except AttributeError:
		pass

	try: 
		title = title_soup.get_text()
		english = english_soup.get_text()
		return english,title
	except AttributeError:
		badFile.append(fileName)
		print("[ArributeError] BAD_URL-- "+link)


def readOriginalLink(fileName):
	with open(linkFilePath+fileName,'r') as f:
		return f.read()

def writeEnglishOriginalFile(fileName, content):
	with open(textFilePath+fileName,'w') as f:
		f.write(content)


# http://www.infoq.com/news/2008/06/eventmachine

# 10658 total
if __name__ == '__main__':
	for i in range(3462,10658):
		fileName = "chinese"+str(i)
		englishUrl = readOriginalLink(fileName)
		
		# get rid of links not from infoq
		if re.search('infoq',englishUrl) == None:
			print("[NOT INFOQ ARTICLE]: "+fileName)
			continue

		try: 
			# scrape enlgish content from all infoq website
			english, title = myBeautiful(englishUrl,fileName)

			finalEnglishContent = "URL "+englishUrl+"\nTITLE "+title+"\nCONTENT\n\n"+english

			writeEnglishOriginalFile(fileName, finalEnglishContent)
		except TypeError:
			pass
		except BaseException:
			badFile.append(fileName)
			print("[ArributeError] BAD_URL-- "+englishUrl)


	print(badFile)
	with open(os.environ['HOME']+"/documents/badFile",'w') as f:
		f.write(badFile)




