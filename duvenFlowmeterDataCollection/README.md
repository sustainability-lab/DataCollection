This code collects data from four daisy chained flow meter. The flow meter is installed at Duven Dormitory of IIT Gandhinagar.

## Best Practices
The following lines must exists in Crontab (```crontab -e```). The first will make sure that the scripts restarts after every reboot of pi. The second lines will dump the locally collected data to Turing Serer everyday at 1600 hours. 

```@reboot sleep 180 && python3 /home/pi/water_meter/main_code.py```
```0 16 * * * scp /home/pi/water_meter/flow_meter_id_1.csv /home/pi/water_meter/flow_meter_id_2.csv /home/pi/water_meter/flow_meter_id_3.csv rishiraj.a@10.0.62.222:/home/rishiraj.a/duven_water/```

## Send IP address of RPi to Turing Server.
The following line will do the trick. This was not tested with WiFi and works well on LAN connected RPi
```*/5 * * * * echo "ip-duven-rpi=`hostname -I`" | curl -d @- 10.0.62.222:5008 > /home/pi/ip-log.txt 2>1&```

Note that a server should be running at 10.0.62.222:5008 (```app.py```) to catch the POST request coming form ```CURL```.

