import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from random import randrange
import utils.func as func

# Get the hut information
hutIDLimit = 675 #largest hutID (July 2024)
[hutIDs, hutIDsSAC] = func.findHutIDs(hutIDLimit)
#store it in the excel file
hutIDs.to_excel('HutInfo.xlsx', index = False)
hutIDsSAC.to_excel('HutInfoSAC.xlsx', index = False)
print("Hut information has been updated")