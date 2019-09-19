import csv
from flask import Flask, render_template, request, url_for, redirect
from flask import make_response
import datetime
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json
import sys



#init flask app
app = Flask(__name__)

co2 = pd.read_csv("co2_data.csv")
#data1 = [go.Scatter(x=co2['Time'],y=co2['Temperature(C)'],name="Response Curve")];

def create_plot(x):
	#co2 = pd.read_csv("co2_data.csv")
	#for i in range(len(co2)):
    		#co2.at[i,'Time']=datetime.datetime.strptime(co2.at[i,'Time'], '%Y-%m-%d %H:%M:%S.%f')
	if x == '1':
		param = "Temperature(C)"
	elif x == '2':
		param = "Moisture"
	elif x == '3':
		param = "CO2 ppm(CCS811)";
	elif x == '4':
		param = "TVOC ppb(CCS811)"
	else:
		param = "Moisture"
	data = [go.Scatter(x=co2['Time'],y=co2[param],name="Response Curve")]
	graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

	return graphJSON

@app.route('/')
def index():
	with open('co2_data.csv', 'r') as f:
		l = list(reversed(list(csv.reader(f))))
	return render_template('index.html', temp=l[0][1], co2=l[0][2], voc=l[0][3],m=l[0][4])
@app.route('/plot', methods=['GET','POST'])
def plot():
	paramx = None
	scatter1 = None
	if request.method == 'POST':
		#paramx = str(request.form('tom'));
		paramx = str(request.form.get("tom",None));
		scatter1 = create_plot(paramx)
		if paramx == '1':
			msg="Currently Showing: Temperature in Celsius Scale"
		elif paramx == '2':
			msg="Currently Showing: Moisture in Percentage Scale"
		elif paramx == '3':
			msg = "Currently Showing: CO2 concentration in ppm"
		elif paramx == '4':
			msg = "Currently Showing: VOC concentration in ppb"
		return render_template('index-plot.html',plot=scatter1, val=msg)
	else:
		#scatter = create_plot("nothing");
		return render_template('index-plot.html',plot=None, val="Select a plot")

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0',port=5007)

    #for row in reversed(list(csv.reader(f))):
     #   print(row)
