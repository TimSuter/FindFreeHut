
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from random import randrange
import streamlit as st

def findHutIDs(hutidLimit = 1000):
    #goes through all hut ids and checks if the hut exists
    #if the hut exists, it saves the hut id, altitude and coordinates in a dataframe
    #if the hut does not exist, it is skipped
    #returns a dataframe with hut information
    hutInfo = pd.DataFrame(columns = ['Hut ID', 'Hut Name', 'Altitude', 'Coordinates', 'Reservation Link'])
    hutInfoSAC = pd.DataFrame(columns = ['Hut ID', 'Hut Name', 'Altitude', 'Coordinates', 'Reservation Link'])
    hutInfoCH = pd.DataFrame(columns = ['Hut ID', 'Hut Name', 'Altitude', 'Coordinates', 'Reservation Link'])
    #parameters
    date = '11.07.2027' #pick a date well into the future
    hutCounter = 0
    hutCounterSAC = 0
    hutCounterCH = 0 
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
        time.sleep(0.25*randrange(0,10))
        page = s.get(f'https://www.alpsonline.org/reservation/calendar?hut_id={hutid}&selectDate={date}&lang=en')
        soup = bs(page.content, 'html.parser')
        
        name_check = ['DAV', 'AIV', 'CAI', 'Alpenverein', 'ZZZ', 'AVS']

        #If the hut does not exist or is not activated, the error message is different
        erm = soup.find_all('div', {'class': 'errorsMessage'})
        noHutError = f'<div class="errorsMessage">The requested hut [{hutid}] cannot be found. Please check your parameters.</div>'
        hutNotActivatedError = f'<div class="errorsMessage">This hut profile is not activated. Bookings cannot be entered at the moment. Please contact the administrator.</div>'
        if str(erm[3]) == noHutError:
            #if the hut does not exist
            print(f'Hut with id {hutid} not found -> Skipped')
            continue
        elif str(erm[3]) == hutNotActivatedError:
            #if the hut is not activated
            print(f'Hut with id {hutid} not activated -> Skipped')
            continue
        else:
            print(f'Hut with id {hutid} found')
            hutInfBS = soup.body.find('div', attrs={'class': 'info'}).find_all('span')
            hutname = soup.body.find('div', {'class': 'info'}).find_all('h4')[0].text

        if hutInfBS[3].text[-1] == 'm':
            altitude = hutInfBS[3].text[24:-2]
        else:
            altitude = hutInfBS[3].text[24:]

        #check if the hut is in Switzerland        
        swissHut = True
        for name in name_check:
            if name in hutname:
                swissHut = False
                break

        if swissHut:
            hutInfoCH.loc[hutCounter] = [hutid, hutname, altitude, hutInfBS[4].text[13:], f'https://www.alpsonline.org/reservation/calendar?hut_id={hutid}&selectDate={date}&lang=en']
            hutCounterCH += 1

        #one dataframe with SAC huts only
        if 'SAC' in hutname and swissHut:
            hutInfoSAC.loc[hutCounter] = [hutid, hutname, altitude, hutInfBS[4].text[13:], f'https://www.alpsonline.org/reservation/calendar?hut_id={hutid}&selectDate={date}&lang=en']
            hutCounterSAC += 1
        #one dataframe with all huts
        hutInfo.loc[hutCounter] = [hutid, hutname, altitude, hutInfBS[4].text[13:], f'https://www.alpsonline.org/reservation/calendar?hut_id={hutid}&selectDate={date}&lang=en']
        hutCounter += 1


    return hutInfo, hutInfoSAC, hutInfoCH


def findBeds(date, NumPeople = 1, nights = 1, SACOnly = True, CHOnly = False):
    progress_text = "Finding free huts..."
    my_bar = st.progress(0, text=progress_text)
    #Input:
        #first night of the reservation
        #look for all huts, not just SAC huts
        #number of people in the reservation
        #number of nights in the reservation
    #Output:
        #dataframe with all suitable huts, their occupation and the number of beds available

    #load hut information (hutid, hutname, altitude)
    if SACOnly:
        df_huts = pd.read_excel('HutInfoSAC.xlsx')
    elif CHOnly:
        df_huts = pd.read_excel('HutInfoCH2.xlsx')
    else:
        df_huts = pd.read_excel('HutInfo.xlsx')
    #initialize pandas dataframe
    df_freeHuts = pd.DataFrame(columns = ['Hut Name', 'Altitude', 'Free Beds', 'Capacity', 'Service', 'Reservation Link'])

    #initialize session to grab data from alpsonline
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
       'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    s = requests.Session()
    s.headers.update(headers)

    hutCounter = 0 #count how many huts we've found
    nHuts = len(df_huts['Hut ID'])
    timeleft = st.text("Estimated time: " + str(round(nHuts)) + " seconds")
    timePerHut = 2
    timeused = 0
    endtime = 0
    #loop through all hutIDs
    for index, hut in enumerate(df_huts['Hut ID']):
        starttime = time.time()
        progress = round((index+1)/nHuts * 100)
        progress_text = f"Finding free huts... {index+1}/{nHuts} checked"
        my_bar.progress(progress, text=progress_text)
        timeleft.write("Estimated time: " + str(round(timePerHut * (nHuts - (index + 1)), 0)) + " seconds")
        #wait a bit to not overload the server
        time.sleep(0.1 + 0.1*randrange(0,5))
        r = s.get(f'https://www.alpsonline.org/reservation/calendar?hut_id={hut}')
        r = s.get(f'https://www.alpsonline.org/reservation/selectDate?date={date}')
        json_list = []
        try:
            for i, value in r.json().items():
                json_list.append(value[0])
        except ValueError:
            endtime = time.time()
            timeused = (timeused + (endtime-starttime))
            timePerHut = timeused / (index + 1)
            continue
        
        df = pd.DataFrame(json_list)
        #go through df, check if there are enough beds available
        for j in range(0,nights):
            hasfreerooms = True
            if df['freeRoom'][j] < NumPeople:
                hasfreerooms = False
                break
        if hasfreerooms:
            #add hutid, hutname, altiude, occupation, freeRoom, Service to df_freeHuts
            isunattended = df['bedCategoryType'][0]
            if isunattended == 'Unattended':
                service = 'Self-Service'
            else:
                service = 'Full-Service'
            
            df_freeHuts.loc[hutCounter] = [df_huts['Hut Name'][index], str(df_huts['Altitude'][index]) + " m", df['freeRoom'][0], str(round(df['reservedRoomsRatio'][0]*100)) + " %", service, f'https://www.alpsonline.org/reservation/calendar?hut_id={hut}&selectDate={date}&lang=en']
            hutCounter += 1
        endtime = time.time()
        timeused = (timeused + (endtime-starttime))
        timePerHut = timeused / (index + 1)
    my_bar.progress(100, text="Done!")
    
    return df_freeHuts