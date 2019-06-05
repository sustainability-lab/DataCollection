#include <ESP8266WiFi.h>
#include <WiFiClient.h> 
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include "Adafruit_CCS811.h"

 
/* Set these to your desired credentials. */
const char *ssid = "IITGN";  //ENTER YOUR WIFI SETTINGS
const char *password = "12345678";
#define pwmPin 14
int prevVal = LOW;
long th, tl, h, l, ppm, ppm2 = 0.0;

Adafruit_CCS811 ccs;
 
//=======================================================================
//                    Power on setup
//=======================================================================
 
void setup() {
  Serial.begin(9600);
   pinMode(pwmPin, INPUT);
   pinMode(12, OUTPUT);
   pinMode(15, OUTPUT);
   pinMode(13, OUTPUT);
WiFi.mode(WIFI_OFF);        //Prevents reconnection issue (taking too long to connect)
  WiFi.mode(WIFI_STA);        //This line hides the viewing of ESP as wifi hotspot
  WiFi.begin(ssid, password);     //Connect to your WiFi router
  Serial.println("");
  Serial.print("Connecting");
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
   
  }
 
  //If connection successful show IP address in serial monitor
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());  //IP address assigned to your ESP
    Serial.println("CCS811 test");
  
  if(!ccs.begin()){
    Serial.println("Failed to start sensor! Please check your wiring.");
    while(1);
  }
  while(!ccs.available());
  float temp = ccs.calculateTemperature();
  ccs.setTempOffset(temp - 25.0);
  
}
 String ADCData, station, postData;
//=======================================================================
//                    Main Program Loop
//=======================================================================
void loop() {
  HTTPClient http;  ;//Declare object of class HTTPClient
 if(ccs.available()){
  digitalWrite(12,HIGH);
    float temp = ccs.calculateTemperature();
//      Serial.println(temp);
    if(!ccs.readData()){
//      Serial.print("CO2: ");
      ppm=ccs.geteCO2();
//      Serial.print("ppm, TVOC: ");
//      Serial.print(ccs.getTVOC());
//      Serial.print("ppb   Temp:");
//      Serial.println(temp);
    }
    else{
      Serial.println("ERROR!");
      while(1);
    }
  }
  delay(100);
  digitalWrite(12,LOW);
  digitalWrite(15,HIGH);
      do {

        th = pulseIn(pwmPin, HIGH, 1004000)/1000; 

        tl = 1004 - th;

        ppm2 = 5000 * (th-2)/(th+tl-4);

    } while (ppm2 < 0.0);
    digitalWrite(15,LOW); 
  //Post Data
  digitalWrite(13,HIGH);
  postData =ppm ;
  postData = postData +","+ppm2;
  Serial.println(postData);
  
  
  http.begin("http://10.0.137.171:5005/");              //Specify request destination//10.0.71.32
  //http.addHeader("Content-Type", "application/x-www-form-urlencoded");    //Specify content-type header
 
  int httpCode = http.POST(postData);   //Send the request
  String payload = http.getString();    //Get the response payload
 Serial.println(postData);
  Serial.println(httpCode);   //Print HTTP return code
  Serial.println(payload);    //Print request response payload
 
  http.end();  //Close connection
  delay(100);
  digitalWrite(13,LOW);
  delay(5000);  //Post Data at every 5 seconds
}
