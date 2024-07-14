
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from random import randrange


def findHutIDs(SACOnly = False):
    #goes through all hut ids and checks if the hut exists
    #if the hut exists, it saves the hut id, altitude and coordinates in a dataframe
    #if the hut does not exist, it is skipped
    #returns a dataframe with hut information
    hutInfo = pd.DataFrame(columns = ['Hut ID', 'Hut Name', 'Altitude', 'Coordinates', 'Reservation Link'])

    #parameters
    date = '11.07.2027' #pick a date well into the future
    hutCounter = 0
    hutidLimit = 5  #up to which hut we should check
    #------------change hutidLmit to 1000 to check all huts-----------

    
    #initialize session
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
    s = requests.Session()
    s.headers.update(headers)


    for hutid in range(1,hutidLimit):
        #wait a bit to not overload the server
        time.sleep(0.5+ 0.1*randrange(0,10))
        page = s.get(f'https://www.alpsonline.org/reservation/calendar?hut_id={hutid}&selectDate={date}&lang=en')
        soup = bs(page.content, 'html.parser')
        
        #Check if the hut exists
        erm = soup.find_all('div', {'class': 'errorsMessage'})
        #check if a hut exists for the given hutid
        noHutError = f'<div class="errorsMessage">The requested hut [{hutid}] cannot be found. Please check your parameters.</div>'
        hutNotActivatedError = f'<div class="errorsMessage">This hut profile is not activated. Bookings cannot be entered at the moment. Please contact the administrator.</div>'
        if str(erm[3]) == noHutError:
            print(f'Hut with id {hutid} not found')
        elif str(erm[3]) == hutNotActivatedError:
            print(f'Hut with id {hutid} not activated')
        else:
            print(f'Hut with id {hutid} found')
            hutInfBS = soup.body.find('div', attrs={'class': 'info'}).find_all('span')
            hutname = soup.body.find('div', {'class': 'info'}).find_all('h4')[0].text
            if SACOnly:
                if 'SAC' in hutname:
                    hutInfo.loc[hutCounter] = [hutid, hutname, hutInfBS[3].text[24:-2], hutInfBS[4].text[13:], f'https://www.alpsonline.org/reservation/calendar?hut_id={hutid}&selectDate={date}&lang=en']
                    hutCounter += 1
            else:
                hutInfo.loc[hutCounter] = [hutid, hutname, hutInfBS[3].text[24:-2], hutInfBS[4].text[13:], f'https://www.alpsonline.org/reservation/calendar?hut_id={hutid}&selectDate={date}&lang=en']
                hutCounter += 1


    return hutInfo