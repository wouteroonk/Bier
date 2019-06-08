import requests
from bs4 import BeautifulSoup
import re
import smtplib
import os

winkels = [
			'Albert Heijn',
			'Gall En Gall',
			'Coop Supermarkt',
			'JUMBO'
			]

base_url = 'https://www.biernet.nl/bier/aanbiedingen/'
merk_url = [
			'grolsch-premium-pilsener/krat-van-24-flesjes-a-030-liter',
			'grolsch-premium-pilsener/krat-van-16-flesjes-a-045-liter',
			'hertog-jan-pilsener/krat-van-24-flesjes-a-030-liter',
			'warsteiner-premium-pilsener/krat-van-24-flesjes-a-030-liter'
			]
output = []

for merk in merk_url:
	r = requests.get(base_url+merk)
	c = r.content
	soup = BeautifulSoup(c, "lxml")

	aanbieding = soup.find('ul', {"class":"aanbiedingen"})
	text_aanbieding = aanbieding.find_all('div', {"class":"textaanbieding"})
	for winkel in text_aanbieding:
		if winkel.find('p', {"class":"Kratten"}) is not None and winkel.find('img')['title'].title() in winkels:
			winkel_prijs = {}
			winkel_prijs['naam'] = winkel.find('img')['title'].title()
			winkel_prijs['prijs'] = winkel.find('span', {"class":"prijs"}).text
			winkel_prijs['merk'] = winkel.find('span', {"class":"merke"}).text
			winkel_prijs['product'] = winkel.find('p', {"class":"Kratten"}).text
			winkel_prijs['geldig'] = re.sub(r"\s+", " ", winkel.find('p', {"style":"margin:0;"}).text.strip())
			output.append(winkel_prijs)

output = sorted(output, key=lambda k: k['naam'])
txtbody = open('body.txt', 'w')
for i in range(0,len(output)):
	txtbody.write('Winkel:\t'+output[i]['naam']+'\n')
	txtbody.write('Merk:\t'+output[i]['merk']+'\n')
	txtbody.write('Prijs:\t'+(output[i]['prijs'])+' - '+output[i]['product']+'\n')
	txtbody.write('Geldig:\t'+output[i]['geldig']+'\n')
	txtbody.write('\n')

gmail_user = os.environ['gmail_user']
gmail_password = os.environ['gmail_pass']

sent_from = os.environ['gmail_user']
to = os.environ['gmail_pass']
subject = 'Bier aanbiedingen - Daily'
txtbody = open('body.txt', 'r')
body = txtbody.read()

email_text = """\
From: %s  
To: %s  
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login(gmail_user, gmail_password)
server.sendmail(sent_from, to, email_text.encode('utf8'))
server.close()