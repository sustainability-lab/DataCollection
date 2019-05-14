#!/usr/bin/env python
# coding: utf-8

# In[1]:

import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time

import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# In[2]:


def get_time_epoch_minute(minute_):
    t = time.time()
    time_epoch = t - t % (minute_ * 60)
    return time_epoch


# In[3]:

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# In[4]:

headers = {
    'Connection': 'keep-alive',
    'Authorization': 'Basic Z3Vlc3Q6SWl0Z25AMjAxOSQ=',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://10.1.0.10/screens/dashboard.html',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
}
response = session.get(
    'https://10.1.0.10/screens/dashboard.html', headers=headers, verify=False)
response

# In[5]:


def get_data(skip):
    params = {
        # 'columns': 123319,
        'take': 100,
        'skip': skip,
        # 'page': 0,
        # 'pageSize': 500
    }
    data = session.get(
        'https://10.1.0.10/data/client-table.html',
        headers=headers,
        params=params)
    data_json = json.loads(data.text)
    return data_json


# In[7]:

try:
    anon_user = pd.read_csv('anon_master_table.csv')
except FileNotFoundError:
    anon_user = pd.DataFrame(columns=['anonID', 'name', 'mac'])

# In[8]:

if anon_user['anonID'].any():
    last_anonid = anon_user['anonID'].max() + 1
else:
    last_anonid = 1

print('last_anonid: ', last_anonid)

# In[9]:


def get_dataframe(time_epoch):
    global anon_user
    global last_anonid
    data_n = pd.DataFrame(
        columns=['id', 'time', 'area', 'building', 'floor', 'ap', 'str'])
    for skip in range(0, 2001, 100):
        data_json = get_data(skip)
        for client in data_json['data']:
            list_t = re.findall('[A-Z0-9]+', client['AP'])
            #             if list_t[0]=='AC' or list_t[0]=='SH' or list_t[0]=='SFH':
            string = list_t[0] + list_t[1] + list_t[2] + list_t[-1]
            cname = client['Name']
            cmac = client['macaddr']
            anonid = -1
            # first check whether given mac address in anonymising master table
            if (anon_user['mac'] == cmac).any() == False:
                # mac not present in master table

                # if unknown user, simple add to table
                if cname == 'unknown':
                    anon_user = anon_user.append({
                        'anonID': last_anonid,
                        'name': cname,
                        'mac': cmac
                    },
                                                 ignore_index=True)
                    anonid = last_anonid
                    last_anonid += 1
#                     print('new unknown',anonid)

# check if user with given name exists.
# if user does not exist, append new entry and allocate anonid
# if user exists, get its anonid and add the new macaddr for the given user.
                elif (anon_user['name'] == cname).any() == False:
                    anon_user = anon_user.append({
                        'anonID': last_anonid,
                        'name': cname,
                        'mac': cmac
                    },
                                                 ignore_index=True)
                    anonid = last_anonid
                    last_anonid += 1
#                     print('new known',anonid)
                else:
                    anonid = list(
                        anon_user[anon_user['name'] == cname]['anonID'])[0]
                    anon_user = anon_user.append({
                        'anonID': anonid,
                        'name': cname,
                        'mac': cmac
                    },
                                                 ignore_index=True)
#                     print('existing user with new mac/device',anonid)
            else:
                anonid = list(anon_user[anon_user['mac'] == cmac]['anonID'])[0]
#                 print('Already present',anonid)

            data_n = data_n.append({
                'id': anonid,
                'time': int(time_epoch),
                'area': list_t[0],
                'building': list_t[1],
                'floor': list_t[2],
                'ap': list_t[-1],
                'str': string
            },
                                   ignore_index=True)
    return data_n


# In[10]:

te = get_time_epoch_minute(10)
temp_df = get_dataframe(te)

import sqlite3
conn = sqlite3.connect('user_network.db')
c = conn.cursor()

c.execute(
    '''CREATE TABLE IF NOT EXISTS network_user(anonID real, timeEpoch real,area varchar(10),building varchar(10),floor varchar(10) ,ap varchar(10), str varchar(50))'''
)

for row in temp_df.itertuples():
    print(
        int(row[1]), int(row[2]), str(row[3]), str(row[4]), str(row[5]),
        str(row[6]), str(row[7]))
    c.execute('''INSERT into network_user VALUES(?,?,?,?,?,?,?)''',
              (int(row[1]), int(row[2]), str(row[3]), str(row[4]), str(row[5]),
               str(row[6]), str(row[7])))
    conn.commit()

anon_user.to_csv(
    'anon_master_table.csv',
    header=['anonID', 'name', 'mac'],
    mode='w',
    index=False)