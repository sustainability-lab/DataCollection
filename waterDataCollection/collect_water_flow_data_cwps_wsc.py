from pycomm.ab_comm.slc import Driver as SlcDriver
import time
import sqlite3
import sys
import traceback

print('start')
conn = sqlite3.connect('water_data.db')
dbc = conn.cursor()
dbc.execute('''CREATE TABLE IF NOT EXISTS cwps(timeEpoch real, Current_Flow real, Daily_Flow real, Cum_flow real, Wet_Well_Level real )''')
dbc.execute('''CREATE TABLE IF NOT EXISTS wsc1_fwp(timeEpoch real, current_flow real, daily_flow real, cum_flow real ,ult real, pt real)''')
dbc.execute('''CREATE TABLE IF NOT EXISTS wsc1_rwp(timeEpoch real, current_flow real, daily_flow real, cum_flow real ,ult real, pt real)''')

def get_rounded_current_time_inEpoch(minute_):
    t = time.time()
    time_epoch = t - t % (minute_ * 60)
    return time_epoch

def collect_cwps_data(ip, t_):
    c1 = SlcDriver()
    # t_ = time.time()
    if c1.open(ip):
        dbc.execute('''INSERT into cwps VALUES(?,?,?,?,?)''', \
            (t_, float(c1.read_tag("F8:5")), float(c1.read_tag("F8:15")), float(c1.read_tag("F8:7")), float(c1.read_tag("F8:4"))))
        
        # print(t_, float(c1.read_tag("F8:5")), float(c1.read_tag("F8:15")), float(c1.read_tag("F8:7")), float(c1.read_tag("F8:4")))
    conn.commit()
    # print("CWPS data at time: {} added to db".format(t_))


def collect_wsc_data(ip, t_):
    c2 = SlcDriver()
    if c2.open(ip):
        dbc.execute('''INSERT into wsc1_rwp VALUES(?,?,?,?,?,?)''', \
            (t_, float(c2.read_tag("F8:20")), float(c2.read_tag("F8:23")), \
                float(c2.read_tag("F8:22")), float(c2.read_tag("F8:2")), float(c2.read_tag("F8:1"))))

        dbc.execute('''INSERT into wsc1_fwp VALUES(?,?,?,?,?,?)''', \
            (t_, float(c2.read_tag("F8:5")), float(c2.read_tag("F8:15")), \
                float(c2.read_tag("F8:7")), float(c2.read_tag("F8:4")), float(c2.read_tag("F8:0"))))

    conn.commit()
    # print("WSC data at time: {} added to db".format(t_))

if __name__ == "__main__":
    count = 0
    round_off_time_to_minute = 2

    t_ = get_rounded_current_time_inEpoch(round_off_time_to_minute)
    sys.stdout.flush()
    try:
        collect_cwps_data('10.0.111.14', t_)
        # print('14 WATER data collected {}'.format(t_))
    except Exception as e:
        print("10.0.111.14: Error at time {}: \n {}\n".format(t_,str(e)))
        print(traceback.format_exc())
    try:
        collect_wsc_data('10.0.111.13', t_)
        # print('13 WATER data collected {}'.format(t_))
    except Exception as e:
        print("10.0.111.13: Error at time {}: \n {}\n".format(t_,str(e)))
        print(traceback.format_exc())
