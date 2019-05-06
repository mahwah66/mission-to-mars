# Dependencies
import requests
import time
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd


executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
browser = Browser("chrome", **executable_path, headless=True)

def waitforload(url, selector):
    browser.visit(url)
    t1 = time.perf_counter()
    while browser.is_element_not_present_by_css(selector):
        t2 = time.perf_counter()
        if (t2-t1)>10:
            return ""
        # wait?
    return browser.html

def requestsoup(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text,'html.parser')
    return soup


def scrape():
    #t0 = time.perf_counter()
    rinfo={"news":{"title":"", "blurb":""}, "fimage":"", "weather":"", "facts":"", "hemispheres":[]}

    # NASA Mars News ----------------------------#
    news_url = 'https://mars.nasa.gov/news/'

    html = waitforload(news_url, 'div[class="content_title"]')

    if html!="":

        # news_title = browser.find_by_css('div[class="content_title"] a')[0].text   
        # news_p = browser.find_by_css('div[class="article_teaser_body"]')[0].text   
        # soup parse faster
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find('div', 'list_text')
        news_title = results.find('div','content_title').find('a').text
        news_p = results.find('div','article_teaser_body').text
        rinfo["news"]["title"] = news_title
        rinfo["news"]["blurb"] = news_p
    else:
        rinfo["news"]["title"] = "Latest News Currently Unavailable"
        rinfo["news"]["blurb"] = "The connection timed out. Please check back later."

    # JPL Mars Space Images - Featured Image ----------------------------#
    qurl = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    url = qurl.split('/spaceimages')[0]

    soup = requestsoup(qurl)
    try:
        iurl = url + soup.find('a', id='full_image')["data-link"]

        soup = requestsoup(iurl)
        ilink = soup.find('img', 'main_image')
        if ilink!=None:
            featured_image_url = url+ilink["src"]
            rinfo["fimage"] = featured_image_url
        else:
            rinfo["fimage"] = ""
            #print('not finding featured image src')
    except:
        rinfo["fimage"] = ""

    # Mars Weather -----------------------------------------#
    url = 'https://twitter.com/marswxreport?lang=en'
    
    soup = requestsoup(url)
    tweet = soup.find('p','tweet-text')

    try:
        tweet = tweet.text.split('pic.twitter')[0]
        mars_weather = ' '.join(tweet.split('\n'))
        rinfo["weather"] = mars_weather
    except Exception as e:
        rinfo["weather"] = ""
        #print('tweet not found or has no text')


    # Mars Facts -------------------------------------------#
    url = 'https://space-facts.com/mars/'

    tables = pd.read_html(url)
    try:
        df = tables[0]
        df.set_index(0, inplace=True)
        del df.index.name
        html_table = df.to_html(header=False)
        html_table=html_table.replace('\n', '')
        rinfo["facts"] = html_table
    except Exception as e:
        rinfo["facts"] = ""
        #print('not finding tables')

    # Mars Hemispheres -------------------------------------------#
    surl = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    url = surl.split('/search')[0]

    html = waitforload(surl, 'div[class="description"]')
    # this page sometimes takes a long time to load, or fails to load

    if (html!=""):
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div','description')
        hrefs = [d.find('a')['href'] for d in divs]

        hemisphere_image_urls = []
        for href in hrefs:
            furl = url+href
            soup = requestsoup(furl)
            try:
                title = soup.find('h2','title').text
                img_url = soup.find('div','downloads').find('a')['href']
                hemisphere_image_urls.append({"title":title, "img_url":img_url})
            except Exception as e:
                continue
                #print(f'error finding title or image at {furl}')

        rinfo["hemispheres"] = hemisphere_image_urls
    


    # print(f'TIME: {time.perf_counter()-t0}')
    return rinfo


