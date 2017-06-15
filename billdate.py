# -*- coding: utf-8 -*-

#Importing the libraries
import os
import sys
import time 
import io
import json
import requests
import cv2
import re
import operator
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import PIL.ImageOps
import pytesseract
from PIL import ImageFilter
import nltk
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

java_path = "C:/Program Files (x86)/Java/jre1.8.0_131/bin/java.exe"
os.environ['JAVA_HOME'] = java_path

# Variables used for calling MS Azure

_url = 'https://southeastasia.api.cognitive.microsoft.com/vision/v1.0/RecognizeText'
_key = '3ed1c21174694438b28cdc4375999f2c'
_maxNumRetries = 10


#Extracting text from the json file
def print_the_text(res,stat):
    texts = ' '
    if stat=="printed":
        for item in res['regions']:
            for line in item['lines']:
                for word in line['words']:
                    texts += ' ' + word['text']
    else:
        lines = res['recognitionResult']['lines']
        for i in range(len(lines)):
            words = lines[i]['words']
            for j in range(len(words)):
                texts += ' ' + words[j]['text']
    return texts


def stNER(text):

    """
    Function to call Stanford NER Tagger to recognize  PERSON names and ORGANIZATIONS
    It returns tags that is the list of tupples containing words and their NER tag respectively
    """
    path_to_model='C:/Users/PRAMOD/AppData/Roaming/nltk_data/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'
    path_to_jar = 'C:/Users/PRAMOD/AppData/Roaming/nltk_data/stanford-ner/stanford-ner.jar'
    nertagger=StanfordNERTagger(path_to_model, path_to_jar)
    text=str(text)
    token_text = word_tokenize(text)
    tags = nertagger.tag(token_text)
    return tags



def processRequest( json, data, headers, params ):

    """
    Function to process the request to Project Oxford
    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """
    retries = 0
    result = None

    while True:
        response = requests.request( 'post', _url, json = json, data = data, headers = headers, params = params )

        if response.status_code == 429:
            #print( "Message: %s" % ( response.json() ) )
            if retries <= _maxNumRetries: 
                time.sleep(1) 
                retries += 1
                continue
            else: 
                print( 'Error: failed after retrying!' )
                break
        elif response.status_code == 202:
            result = response.headers['Operation-Location']
        else:
            print( "Error code: %d" % ( response.status_code ) )
            result = response.json()
            #print( "Message: %s" % ( response.json() ) )
        break
    return result


def getOCRTextResult( operationLocation, headers ):
    """
    Function to get text result from operation location
    Parameters:
    operationLocation: operationLocation to get text result, See API Documentation
    headers: Used to pass the key information
    """
    retries = 0
    result = None

    while True:
        response = requests.request('get', operationLocation, json=None, data=None, headers=headers, params=None)
        if response.status_code == 429:
            #print("Message: %s" % (response.json()))
            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break
        elif response.status_code == 200:
            result = response.json()
            text=''
            #resu=response.json()
            for item in result['regions']:
                for line in item['lines']:
                    for word in line['words']:
                        text += ' ' + word['text']
            print(text)
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()))
        break
    return result


def call_ms_azure(path):
    # Load raw image file into memory
    pathToFileInDisk = path
    with open(pathToFileInDisk, 'rb') as f:
        data = f.read()

    # Computer Vision parameters
    params = {'handwriting' : 'false'}

    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = _key
    headers['Content-Type'] = 'application/octet-stream'

    json = None

    operationLocation = processRequest(json, data, headers, params)
    return operationLocation
 


def get_date(text): 
    date= re.findall(r'(0?[1-9]|[12][0-9]|3[01])[-/.](0?[1-9]|1[012])[-/.](20\d\d|0\d|1\d)? | (20\d\d)[-/.](0?[1-9]|1[012])[-/.](0?[1-9]|[12][0-9]|3[01]) | (0?[1-9]|1[012])[-/.](0?[1-9]|[12][0-9]|3[01])[-/.](20\d\d)\s', text) 
    date=[(tuple(int(x) if x.isdigit() else x for x in dt if x)) for dt in date]
    if len(date)==0:
        err="No Date element detected!"
        date.append(err)
    return date

def get_name(tags):
    name_list=[]
    i=0
    while i<len(tags)-2 :
        if tags[i][1]=='PERSON':
            if tags[i+1][1]=='PERSON':
                if tags[i+2][1]=='PERSON':
                    name=tags[i][0]+str(" ")+tags[i+1][0]+str(" ")+tags[i+2][0]
                    name_list.append(name)
                    i+=3
                else:
                    name=tags[i][0]+str(" ")+tags[i+1][0]
                    name_list.append(name)
                    i+=2
            else:
                # name=tags[i][0]
                # name_list.append(name)
                i+=2
        else:
            i+=1
                
    nameadd = ''
    for nm in name_list :
        nameadd=nameadd + nm + '  |  '
    return set(nameadd)


def get_org(tags):
    org_list=[]
    i=0
    while i<len(tags)-2 :
        if tags[i][1]=='ORGANIZATION':
            if tags[i+1][1]=='ORGANIZATION':
                if tags[i+2][1]=='ORGANIZATION':
                    org=tags[i][0]+str(" ")+tags[i+1][0]+str(" ")+tags[i+2][0]
                    org_list.append(org)
                    i+=3
                else:
                    org=tags[i][0]+str(" ")+tags[i+1][0]
                    org_list.append(org)
                    i+=2
            else:
                org=tags[i][0]
                org_list.append(org)
                i+=2
        else:
            i+=1
                
    orgadd = ''
    for og in org_list :
        orgadd=orgadd + og + '  |  '
    return orgadd


def get_loc(tags):
    loc_list=[]
    for i in range(len(tags)):
        if tags[i][1]=='LOCATION':
            loc=tags[i][0]
            loc_list.append(loc)
    locadd = ''
    for lc in loc_list :
        locadd=locadd + lc + '  |  '
    return locadd
 

def mainCall(filename):
    file_name="{}.{}".format(filename,"png")
    dir = os.path.abspath('C:/Users/PRAMOD/Desktop/Project EY/Bill_Images_png')
    ##for file_name in os.listdir(dir):
##  if file_name=="bill7.png":
    pathTofile='%s/%s' % (dir,file_name)
    img = Image.open(pathTofile)
    if min(img.size) < 40:
        img = img.crop((0, 0, max(img.size[0], 40), max(img.size[1], 40)))
        img.save(pathTofile)
    result = call_ms_azure(pathTofile)
##    else:
##        continue
    typ="printed"    
    text=print_the_text(result,typ)
    storeText="{0} : \n {1}\n\n".format(file_name,text)
    appendFile=open('C:/Users/PRAMOD/Desktop/Project EY/extractedText.txt','a')
    appendFile.write(storeText)
    appendFile.close()
    tags = stNER(text)
    names=get_name(tags)
    orgs=get_org(tags)
    locs=get_loc(tags)
    dates=get_date(text)
    storeData="{0} - Date: {1} , PERSON - {2} , ORGANIZATIONS - {3} , LOCATIONS - {4} \n".format(file_name,dates,names,orgs,locs)
    appendFile=open('C:/Users/PRAMOD/Desktop/Project EY/output.txt','a')
    appendFile.write(storeData)
    appendFile.close()




