from bs4 import BeautifulSoup
from googleplaces import GooglePlaces
import MySQLdb
import json
import re
import requests
import sys

def getinstagram(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    twitter_link = soup.find('a', href=re.compile('www.instagram'))
    if twitter_link:
        return twitter_link.get('href')
    else:
        return None


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


def handler_event():
    db = MySQLdb.connect(user="MovementAdmin", passwd=sys.argv[2], host="movementmap.cjtdrwjqblil.us-east-1.rds.amazonaws.com", db= "MovementMap")
    cursor = db.cursor()

    info_json = []
    for y in range(0, int(sys.argv[4])):
        url = ""

        offset = str(y + int(sys.argv[3]))
        lst = []
        try:
            cursor.execute('SELECT Legal_Name, S, Postal_Code FROM MovementMapExcelImport ORDER BY Rev_2014 DESC LIMIT ' + offset + ', 1')
            lst = cursor.fetchone()
            place = getinfo(*lst)
            if place:
                url = place.website
        except Exception as e:
            print(e)
            pass
        
        web_json  = {}

        try:
            if url:
                web_json['Website'] = url
                #web_json['location'] = place.formatted_address
                
                cursor.execute('SELECT OrganizationID FROM organization WHERE CRALegalName=\"{}\"'.format(lst[0]))
                bn = int(cursor.fetchone()[0])

                facebook_url = getfacebook(url)
                twitter_url = gettwitter(url)
                instagram_url = getinstagram(url)
                if facebook_url:
                   web_json['Facebook'] = facebook_url
                if twitter_url:
                   web_json['Twitter'] = twitter_url
                if instagram_url:
                   web_json['Instagram'] = instagram_url
                info_json.append(web_json)
            
            for x in web_json:
                cursor.execute('SELECT URLTypeId FROM url_type WHERE URLTypeName=\'{}\''.format(x))
                name_id = cursor.fetchone()[0]
                print(offset +' INSERT INTO organization_url (OrganizationID, URLTypeId, URL) VALUE ({}, {}, \'{}\')'.format(bn, name_id, web_json[x]))
                cursor.execute('INSERT INTO organization_url (OrganizationID, URLTypeId, URL) VALUE ({}, {}, \'{}\')'.format(bn, name_id, web_json[x]))

            if web_json:
                db.commit()
        except Exception as e:
            print(e)
            pass
           
            
handler_event()
