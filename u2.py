from bs4 import BeautifulSoup
import urllib2
import re
import json

#Below function returns the soup for the url specified in the parameter
def souper(url):        
    req=urllib2.Request(url,headers={'User-Agent':"sbk browser"})
    response=urllib2.urlopen(req)
    html=response.read()
    soup=BeautifulSoup(html)
    return soup

#Below function returns the request generated for the url
#specified in the parameter.
def reqGen(url):
    req=urllib2.Request(url,headers={'User-Agent':"web browser"})
    return req

#Generates the file name from the url.
def nameGen(url):
    match=re.search(r'uploads/.*',url)
    str=match.group()
    str1=str.split('/')
    return str1[1]
    

#Save the image
def saveImage(url):
    BS=souper(url)
    for link in BS.find_all('img',title_='',alt_=''):
        x='uploads' in link['src']
        y='button' in link['src']
        if(x==True and y==False):
            #print link['src']
            name=nameGen(link['src'])
            #print name
            imgreq=reqGen(link['src'])
            imgres=urllib2.urlopen(imgreq)
            localfile=open(name,'wb')
            localfile.write(imgres.read())
            localfile.close()
            break
#Generates the links 
def getAllLinks():
    url='http://zenpencils.com/comic/'
    soup=souper(url)
    links=soup.find_all('option')
    for link in links:
        saveImage(link['value'])


getAllLinks()

    
