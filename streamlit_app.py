import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from random import randrange
from datetime import datetime
import utils.func as func


#On what date is the first nicht of the reservation?
date = st.date_input("When do you want to start your stay?", datetime.today())
#How many people?
beds = st.number_input("How many beds do you need?", min_value = 1, max_value = 99, value = 1, step = 1)
#How many nights?
nights = st.number_input("How many nights do you want to stay?", min_value = 1, max_value = 99, value = 1, step = 1)

def switchCHOnly():
    if st.session_state.t1:
        st.session_state.t2 = True

SACOnlyToggle = st.toggle("Only SAC huts", True, on_change= switchCHOnly, key = "t1")
ChOnlyToggle = st.toggle("Only huts in Switzerland", True, key = "t2")


#button to start search
if st.button("Find free huts!"):
    if SACOnlyToggle:
        SACOnly = True
    if ChOnlyToggle:
        CHOnly = True
    dateStr = str(date.day) + '.' + str(date.month) + '.' + str(date.year)
    #use input information (date, beds, nights) to find free huts
    df_freeHuts = func.findBeds(dateStr, beds, nights, SACOnlyToggle, ChOnlyToggle)
    #display the results with streamlit
    st.markdown(df_freeHuts.to_html(render_links=True, escape=False, index = False), unsafe_allow_html=True)
    st.dataframe(df_freeHuts)

    #display the huts on a map
    #this is a bit annyoing to do, because the coordinates are stored in a special swiss format
    #put on hold for now
