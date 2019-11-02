import re
import pandas as pd
import time
import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib3
import traceback
# import sqlite3


def get_rounded_current_time_inEpoch(minute_):
    t = time.time()
    time_epoch = t - t % (minute_ * 60)
    return time_epoch


import pymysql as PyMySQL
# Open database connection
db = PyMySQL.connect(host="10.0.62.222",
                     user="root",
                     password="root",
                     db="CampusData")

# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor.execute(
    'CREATE TABLE IF NOT EXISTS occupancy(anonID real, timeEpoch real,area varchar(10),building varchar(10),floor varchar(10) ,ap varchar(10), str varchar(50))'
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Define Requests Session
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
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
response = session.get('https://10.1.0.10/screens/dashboard.html',
                       headers=headers,
                       verify=False)


# This function scraps data for skip to skip+100 clients from Cisco WLC Manager
def get_data(skip):
    params = {
        # 'columns': 123319,
        'take': 100,
        'skip': skip,
    }
    data = session.get('https://10.1.0.10/data/client-table.html',
                       headers=headers,
                       params=params)
    data_json = json.loads(data.text)
    return data_json


def get_dataframe(time_epoch):
    # The next 2 variables are used to assign anonymous user_id
    global anon_user
    global last_anonid
    # define Dataframe
    data_n = pd.DataFrame(
        columns=['id', 'time', 'area', 'building', 'floor', 'ap', 'str'])
    # Scrap all data
    for skip in range(0, 2001, 100):
        data_json = get_data(skip)
        for client in data_json['data']:
            list_t = re.findall('[A-Z0-9]+', client['AP'])
            #             if list_t[0]=='AC' or list_t[0]=='SH' or list_t[0]=='SFH':
            if len(list_t) < 2:
                continue

            try:
                string = list_t[0] + list_t[1] + list_t[2] + list_t[-1]
                client_name = client['Name']
                client_mac = client['macaddr']
                anonid = -1
                # first check whether given mac address in anonymising master table
                if (anon_user['mac'] == client_mac).any() == False:
                    # mac not present in master table

                    # if unknown user, simple add to table
                    if client_name == 'unknown':
                        anon_user = anon_user.append(
                            {
                                'anonID': last_anonid,
                                'name': client_name,
                                'mac': client_mac
                            },
                            ignore_index=True)

                        anonid = last_anonid
                        last_anonid += 1
                        # print('new unknown',anonid)

                    # check if user with given name exists.
                    # if user does not exist, append new entry and allocate anonid
                    elif (anon_user['name'] == client_name).any() == False:
                        anon_user = anon_user.append(
                            {
                                'anonID': last_anonid,
                                'name': client_name,
                                'mac': client_mac
                            },
                            ignore_index=True)
                        anonid = last_anonid
                        last_anonid += 1
                        # print('new known',anonid)
                    # if user exists, get its anonid and add the new macaddr for the given user
                    else:
                        anonid = list(anon_user[anon_user['name'] ==
                                                client_name]['anonID'])[0]
                        anon_user = anon_user.append(
                            {
                                'anonID': anonid,
                                'name': client_name,
                                'mac': client_mac
                            },
                            ignore_index=True)
                        # print('existing user with new mac/device',anonid)
                else:
                    anonid = list(
                        anon_user[anon_user['mac'] == client_mac]['anonID'])[0]
                    # print('Already present',anonid)

                data_n = data_n.append(
                    {
                        'id': anonid,
                        'time': int(time_epoch),
                        'area': list_t[0],
                        'building': list_t[1],
                        'floor': list_t[2],
                        'ap': list_t[-1],
                        'str': string
                    },
                    ignore_index=True)

            except Exception as e:
                print("Error in get_dataframe: ", str(e))
                print(traceback.format_exc())
    return data_n


# Read Master Table which anonymises users
try:
    anon_user = pd.read_csv('anon_master_table.csv')
# Create Master Table if not found
except FileNotFoundError:
    anon_user = pd.DataFrame(columns=['anonID', 'name', 'mac'])

if __name__ == '__main__':

    # If any anonymous ID exists, get next anonymous id
    if anon_user['anonID'].any():
        last_anonid = anon_user['anonID'].max() + 1
    # Else asign first anonymous id
    else:
        last_anonid = 1
    minute_interval = 10
    te = get_rounded_current_time_inEpoch(minute_interval)
    try:
        temp_df = get_dataframe(te)
        for row in temp_df.itertuples():
            print(int(row[1]), int(te), str(row[3]), str(
                               row[4]), str(row[5]), str(row[6]), str(row[7]))
            print(type(int(row[1])), type(int(te)), type(str(row[3])), type(str(row[4])), type(str(row[5])), type(str(row[6])), type(str(row[7])))
            cursor.execute('''INSERT into occupancy VALUES(?,?,?,?,?,?,?)''',
                           (int(row[1]), int(te), str(row[3]), str(
                               row[4]), str(row[5]), str(row[6]), str(row[7])))
        db.commit()

        print('data collection at {} done'.format(te))

        anon_user.to_csv('anon_master_table.csv',
                         header=['anonID', 'name', 'mac'],
                         mode='w',
                         index=False)

    except Exception as e:
        print("Error at time {}: \n {}\n".format(te, str(e)))
        print(traceback.format_exc())