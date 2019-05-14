import re
import pandas as pd
import numpy as np
import datetime
import time
import sqlite3
import traceback

import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

conn = sqlite3.connect('occupancy_data.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS occupancy(timeEpoch real,area varchar(10),building varchar(10),floor varchar(10) ,count int)''')
c.execute('''CREATE TABLE IF NOT EXISTS occupancy_ap(timeEpoch real,area varchar(10),building varchar(10),floor varchar(10) ,ap varchar(10), count int)''')


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

headers = {
    'Connection': 'keep-alive',
    'Authorization': 'Basic Z3Vlc3Q6SWl0Z25AMjAxOSQ=',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://10.1.0.10/screens/dashboard.html',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
}
response = session.get('https://10.1.0.10/screens/dashboard.html', headers=headers,verify=False)
response

def get_time_epoch_minute(minute_):
    t = time.time()
    time_epoch = t - t%(minute_*60)
    return time_epoch

def get_data(skip):
    params = {
    'take': 100,
    'skip': skip,
    }
    data = session.get('https://10.1.0.10/data/client-table.html',headers=headers, params=params)
    data_json = json.loads(data.text)
    return data_json


def get_dataframe():
    data_n = pd.DataFrame(columns=['str','area', 'building', 'floor', 'room'])
    for skip in range(0,2001,100):
        data_json = get_data(skip)
        for client in data_json['data']:
            list_t = re.findall('[A-Z0-9]+',client['AP'])
            # print(list_t)
            if len(list_t)<2:
                continue
            # if list_t[0]=='AC' or list_t[0]=='SH' or list_t[0]=='SFH':
            try:
                string = list_t[0]+list_t[1]+list_t[-1]
                data_n = data_n.append({'str':string,'area':list_t[0],'building':list_t[1],'floor':list_t[2],'ap':list_t[-1]}, ignore_index=True)
            except Exception as e:
                print("Error in get_dataframe: ",str(e))
                print(list_t)
                print(traceback.format_exc())
    return data_n

def get_dataframe_count():
    data_n = get_dataframe()
    if isinstance(data_n, pd.DataFrame)==False:
        return -1
    data_count = data_n.groupby(['area','building','floor','ap'])['str'].count()
    df_count = data_count.to_frame()
    return df_count


def get_occupancy_time(time_epoch):
    df_count = get_dataframe_count()
    if isinstance(df_count, pd.DataFrame)==False:
        return -1

    all_loc_np = np.asarray(list(df_count.index))

    # Delete AP name if not necessary
    # all_loc_np = np.delete(all_loc_np,3,1)

    all_loc_unique_np = np.unique(all_loc_np, axis=0)
    # all_loc_unique_np[:5]

    df_floor_occ = pd.DataFrame(columns=['timeEpoch','area','building','floor','ap','count'])
    for loc_ in all_loc_unique_np:
        sum_ = df_count.loc[tuple(loc_[:])].sum()
        df_floor_occ = df_floor_occ.append({'timeEpoch':time_epoch,'area':loc_[0],'building':loc_[1],'floor':loc_[2],'ap':loc_[3],'count':int(sum_)}, ignore_index=True)

    return df_floor_occ


print('start')

if __name__ == "__main__":
    minute_interval = 2
    while(1):
        try:
            time_epoch = get_time_epoch_minute(minute_interval)
            temp_df = get_occupancy_time(time_epoch)
            if isinstance(temp_df, pd.DataFrame)==False:
                continue
            print('Hi from main', time_epoch)
            for row in temp_df.itertuples():
                # print(int(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5]),int(row[6]))
                c.execute('''INSERT into occupancy_ap VALUES(?,?,?,?,?,?)''',(int(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5]),int(row[6])))
                # print(int(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5]), int(row[6]))
            # temp_df.to_csv('network_data.csv',mode = 'a', header=False, index=False)
            print('NETWORK data added at {}'.format(time_epoch))
            conn.commit()
        except Exception as e:
            print("Error at time {}: \n {}\n".format(time_epoch,str(e)))
            print(traceback.format_exc())
            continue
        time.sleep(minute_interval*60)
