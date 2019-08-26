import pymodbus
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.transaction import ModbusRtuFramer
from os import path
import time
from datetime import datetime
import os

def write_csv(csv_path, data):
    with open(csv_path, 'a') as f:
         f.write(data)
def write_csv_header(csv_file, header):
    with open(csv_file, 'a') as f:
        f.write(header)
def write_csv_header(csv_file, header):
    with open(csv_file, 'a') as f:
        f.write(header)
params_recorded =  "Forward Volumetric Flow (m3/hr), FV Totalizer (m3/hr), Reverse Volumetric Flow (m3/hr), RV Totalizer (m3/hr), Velocity (m/sec), Forward Mass Flow, Forward Mass Totalizer, Reverse Mass Flow, Reverse Mass Totalizer"

DATA_PATH = "/home/pi/water_meter"
no_of_meters = 3
meter_id = 1
lim = 0

try:
    client = ModbusClient(method="rtu", port="/dev/ttyUSB0", stopbits=1, bytesize=8, parity='N', baudrate=9600)
    connection = client.connect()
except:
    print("Unable to connect to the Com Port, Please try Again \n")

l= 1

answer = []
data_convert = []

while (l <= no_of_meters):
    csv_file_path = os.path.join(DATA_PATH, "flow_meter_id_" + str(l) + ".csv")
    if path.isfile(csv_file_path):
        break
    else:
        write_csv_header(csv_file_path, "Timestamp," +
                         params_recorded + "\n")
    l+=1



register_record_array = [0,11]
block_size_record_arr = [8,10]


while True:
    answer= []
    data = ""
    j=0
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
        for x in range(len(answer)):
            answer[x] = str(answer[x])    
        answer.insert(0,str(time.time()))
        for x in answer:
            data +=x + ','
        data = data+"\n"

        print("Data to be written")
        print (data)
        csv_file_path = os.path.join(DATA_PATH, "flow_meter_id_" + str(meter_id) + ".csv")
        write_csv(csv_file_path, data)
        print ("Size : " + str(len(answer)))
        meter_id+=1
    except:
        print("Error Reading from the Meter ID : " + str(meter_id))
        if meter_id < no_of_meters:
            meter_id += 1
        elif meter_id == no_of_meters:
            meter_id = 1
    time.sleep(1)

    

