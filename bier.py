import requests
from bs4 import BeautifulSoup
import re
import smtplib
import os

shops = [
                        'Albert Heijn',
                        'Gall En Gall',
                        'Coop Supermarkt',
                        'JUMBO'
                        ]

base_url = 'https://www.biernet.nl/bier/aanbiedingen/'
brands_url = [
                        'grolsch-premium-pilsener/krat-van-24-flesjes-a-030-liter',
                        'grolsch-premium-pilsener/krat-van-16-flesjes-a-045-liter',
                        'hertog-jan-pilsener/krat-van-24-flesjes-a-030-liter',
                        'warsteiner-premium-pilsener/krat-van-24-flesjes-a-030-liter'
                        ]
beer_discount = []

for brand in brands_url:
        r = requests.get(base_url+brand)
        c = r.content
        soup = BeautifulSoup(c, "lxml")

        discount = soup.find('ul', {"class":"aanbiedingen"})
        textdiscount = discount.find_all('div', {"class":"textaanbieding"})
        for shop in textdiscount:
                if shop.find('p', {"class":"Kratten"}) is not None and shop.find('img')['title'].title() in shops:
                        shop_info = {}
                        shop_info['name'] = shop.find('img')['title'].title()
                        shop_info['price'] = shop.find('span', {"class":"prijs"}).text
                        shop_info['brand'] = shop.find('span', {"class":"merke"}).text
                        shop_info['product'] = shop.find('p', {"class":"Kratten"}).text
                        shop_info['valid'] = re.sub(r"\s+", " ", shop.find('p', {"style":"margin:0;"}).text.strip())
                        beer_discount.append(shop_info)

beer_discount = sorted(beer_discount, key=lambda k: k['price'], reverse=True)

def generatebody():
        body = []
        for i in range(0,len(beer_discount)):
                body.append('Winkel:\t'+beer_discount[i]['name']+'\n')
                body.append('Merk:\t'+beer_discount[i]['brand']+'\n')
                body.append('Prijs:\t'+(beer_discount[i]['price'])+' - '+beer_discount[i]['product']+'\n')
                body.append('Geldig:\t'+beer_discount[i]['valid']+'\n')
                body.append('\n')
        return ''.join(body)

gmail_user = os.environ['gmail_user']
gmail_password = os.environ['gmail_pass']

sent_from = os.environ['gmail_user']
to = os.environ['gmail_user']
subject = 'Bier aanbiedingen - Daily'
body = generatebody()

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
server.close