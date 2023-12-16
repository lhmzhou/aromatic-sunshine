import pandas as pd
import urllib.request
from decimal import Decimal
import json 
import os 
from datetime import date

dt = pd.read_csv("./csv/hospital.csv")
dt = dt[dt.can_automate == True]
