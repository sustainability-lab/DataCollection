from flask import Flask, request
import sys
import datetime
text_file=open("co2_data.csv","a+")
text_file.write("Time,Temperature(C),CO2 ppm(CCS811),TvOC ppb(CCS811),CO2 ppm(Mhz19B) \n")
text_file.close()
a=0
try:
    app = Flask(__name__)
    @app.route('/',methods=['POST'])
    def result():    
        ppm = request.data
        ppm=str(ppm, 'utf-8')
        print(ppm)
        text_file=open("co2_data.csv","a+")
        text_file.write("{0},{1}\n".format(datetime.datetime.now(),ppm))
        text_file.close()
        print("SUCCESS")
        return "Received Successfully"
except Exception as e:
    print(e)
    sys.exit(1)
    
if __name__ == '__main__':
     app.run(host='0.0.0.0',port=5005)
