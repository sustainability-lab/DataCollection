import pymodbus
from serial import Serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.transaction import ModbusRtuFramer
from os import path
import time
from datetime import datetime
import os
from decoding_data import decoder

def write_csv(csv_path, data):
    with open(csv_path, 'a') as f:
         f.write(data)
def write_csv_header(csv_file, header):
    with open(csv_file, 'a') as f:
        f.write(header)
def write_csv_header(csv_file, header):
    with open(csv_file, 'a') as f:
        f.write(header)
params_recorded =  "Current Phase 1 (A1),Current Phase 2 (A2), Current Phase 3 (A3), Current Average(A),Avg. Line to Neutral Voltage(VLN),Active Power Phase 1 (W1), Active Power Phase 2 (W2), Active Power Phase 3 (W3),Total Active Power(W),Reactive Power Phase 1 (VAR1), Reactive Power Phase 2 (VAR2), Reactive Power Phase 3 (VAR3), Total Reactive Power(VAR), Apparent Power Phase 1 (VA1), Apparent Power Phase 2 (VA2),Apparent Power Phase 3 (VA3), Total Apparent Power(VA), Frquency (F), Total Power Factor(PF)"

DATA_PATH = "/home/pi/smart_meter"
no_of_meters = 4
meter_id = 1

try:
    client = ModbusClient(method="rtu", port="/dev/ttyUSB0", stopbits=1, bytesize=8, parity='E', baudrate=19200)
    connection = client.connect()
except:
    print("Unable to connect to the Com Port, Please try Again \n")

l= 1

answer = []

while (l <= no_of_meters):
    csv_file_path = os.path.join(DATA_PATH, "meter_id_" + str(l) + ".csv")
    if path.isfile(csv_file_path):
        break
    else:
        write_csv_header(csv_file_path, "Timestamp," +
                         params_recorded + "\n")
    l+=1



register_record_array = [2999, 3009, 3035, 3053, 3109, 3191]
block_size_record_arr = [6, 2, 2, 24, 2, 2]


j=0

while True:
    answer= []
    data = ""
    try:
        if meter_id > no_of_meters :
            meter_id = 1
        print("Reading Data from Meter ID : " + str(meter_id))
        for (base_reg, block_size) in zip(register_record_array, block_size_record_arr):
            q = divmod(block_size,12)
            i=1
            print(q)
            while i <= q[0]:
                result= client.read_holding_registers(base_reg,12,unit=meter_id) # address, count, slaveAddress
                answer+=result.registers
                base_reg+=12
                i+=1
            if (q[0] == 0 and q[1]!=0) or (i >q[0] and q[1]!=0):
                result= client.read_holding_registers(base_reg,q[1],unit=meter_id)
                answer+=result.registers
        for i in range(len(answer)):
            answer[i] = str(answer[i])
        for i in range(0,len(answer),2):
            j = int(i/2)
            answer[j] = answer[i] + answer[i+1]
        answer= answer[:int(len(answer)/2)]
        data_convert = list(map(decoder,answer))
        for x in range(len(data_convert)):
            data_convert[x] = str(data_convert[x])    
        data_convert.insert(0,str(time.time()))
        for x in data_convert:
            data +=x + ','
        data = data+"\n"
            
        csv_file_path = os.path.join(DATA_PATH, "meter_id_" + str(meter_id) + ".csv")
        write_csv(csv_file_path, data)
        print ("Size : " + str(len(data_convert)))
        meter_id+=1
    except:
        print("Error Reading from the Meter ID : " + str(meter_id))
        if meter_id < no_of_meters:
            meter_id += 1
        elif meter_id == no_of_meters:
            meter_id = 1
    time.sleep(1)

    

