import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from random import randrange
from datetime import datetime
import utils.func as func

import plotly.express as px

#build input for calendar
#year = int(datetime.today().strftime('%Y'))
#month = int(datetime.today().strftime('%m'))
#day = int(datetime.today().strftime('%d'))



def display_map(location_data):
    fig = px.scatter_mapbox(location_data, lat="Latitude", lon="Longitude", hover_name="Hut Name", hover_data=["Altitude"],)
    
    fig.update_layout(mapbox_style="open-street-map")
    
    return fig


#On what date is the first nicht of the reservation?
date = st.date_input("When do you want to start your stay?", datetime.today())
#How many people?
beds = st.number_input("How many beds do you need?", min_value = 1, max_value = 99, value = 1, step = 1)
#How many nights?
nights = st.number_input("How many nights do you want to stay?", min_value = 1, max_value = 99, value = 1, step = 1)

SACOnlyToggle = st.toggle("Only SAC huts?", True)
SACOnly = True

#button to start search
if st.button("Find free huts!"):
    dateStr = str(date.day) + '.' + str(date.month) + '.' + str(date.year)
    #use input information (date, beds, nights) to find free huts
    df_freeHuts = func.findBeds(dateStr, beds, nights, SACOnly)
    #display the results with streamlit
    st.markdown(df_freeHuts.to_html(render_links=True, escape=False, index = False), unsafe_allow_html=True)

    #display the huts on a map
