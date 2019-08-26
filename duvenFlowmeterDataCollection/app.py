from flask import Flask, request
import sys
import datetime

try:
	app=Flask(__name__)
	@app.route('/',methods=['POST'])
	def record():
		ip_duven_rpi = request.form['ip-duven-rpi']
		file = open('duven-ip.txt','a')
		file.write("\n"+str(datetime.datetime.now())+" IP of Rpi at Duven = "+ip_duven_rpi) 
		file.close()
		return 'Success'
	@app.route('/wscip', methods=['POST'])
	def recordWSCip():
		ip_wsc2_rpi = request.form['ip-wsc-rpi']
		file2 = open('wsc2-ip.txt','a')
		file2.write("\n"+str(datetime.datetime.now())+" IP of RPi at WSC-2= "+ip_wsc2_rpi)
		file2.close();
		return 'Success'

except Exception as e:
	print(e)
	sys.exit(1)

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5008)
