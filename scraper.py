from bs4 import BeautifulSoup
from googleplaces import GooglePlaces
import MySQLdb
import re
import requests
import sys
from pprint import pprint


def gettwitter(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    twitter_link = soup.find('a', href=re.compile('twitter'))
    if twitter_link:
        return twitter_link.get('href')
    else:
        return None

def getfacebook(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    facebook_link = soup.find('a', href=re.compile('www.facebook'))
    if facebook_link:
        return facebook_link.get('href')
    else:
        return None

def getinfo(church_name, location, postalcode):
    google_places = GooglePlaces(sys.argv[1])

    query_result = google_places.nearby_search(location=location, keyword=church_name)
    
    for place in query_result.places:
        place.get_details()
        return place


def handler_event(event, context):
    db = MySQLdb.connect(user="MovementAdmin", passwd="CityMovement!", host="movementmap.cjtdrwjqblil.us-east-1.rds.amazonaws.com", db= "MovementMap")
    cursor = db.cursor()
    cursor.execute('SELECT Legal_Name, S, Postal_Code FROM MovementMapExcelImport WHERE Legal_Name LIKE (\'%church%\') ORDER BY Rev_2014 DESC')

    info_json = []
    for x in range(0, 5):
        url = ""
        try:
            lst = cursor.fetchone()
            place = getinfo(*lst)
            url = place.website
        except:
            pass

        if url:
            web_json = {} 
            web_json['name'] = lst[0]
            web_json['url'] = url
            facebook_url = getfacebook(url)
            twitter_url = gettwitter(url)
            if facebook_url:
               web_json['facebook'] = facebook_url
            if twitter_url:
               web_json['twitter'] = twitter_url
            info_json.append(web_json)
    return info_json
