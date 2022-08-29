#include <NewPing.h> //extra library that was downloaded from: https://playground.arduino.cc/Code/NewPing/
#include <WiFi.h> //standard arduino library
#include <HTTPClient.h> //standard arduino library

#define TRIGGER_PIN  2  // pin tied to trigger pin via the MUX
#define ECHO_PIN     5  // pin tied to echo pin via the MUX
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters). 


const char* ssid = "Tranedisko"; //WiFi name UPDATE!
const char* password =  "knappe2018"; //WiFi password UPDATE!
String msg;


NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.


// defines variables
long duration;
int distance;
int i = 0;
int parkingSpots[6];
int parkingSpotsNew[6];
int parkingSpotsOld1[6];
int parkingSpotsOld2[6];

//function to construct message that is send to Raspberry PI
void constructMsg(){

  msg = "";
  
  for(int i = 0; i<6; i++){
    msg += i;
    msg += ":";
    msg += parkingSpots[i];
    msg += ":";
  }
  

}


//function that checks for erros and only changes state from 1 to 0 if 0 for 3 consecutive readings
void checkError(){
  for(int i = 0; i<6; i++){
    if(parkingSpotsOld2[i] == 0 && parkingSpotsOld1[i] == 0 && parkingSpotsNew[i] == 0){
    parkingSpots[i]=0;
    }else{
    parkingSpots[i]=1;
    }

  parkingSpotsOld2[i] = parkingSpotsOld1[i];
  parkingSpotsOld1[i] = parkingSpotsNew[i];
  } 
}

//function to make POST-requests 
void sendData(){
  if(WiFi.status()== WL_CONNECTED){   //Check WiFi connection status
 
   HTTPClient http;   
 
   http.begin("http://192.168.86.46:5050/post"); //target IP-address of Raspberry Pi UPDATE
   http.addHeader("Content-Type", "text/plain");             
 
   int httpResponseCode = http.POST(msg);   //Send the actual POST request
 
   if(httpResponseCode>0){
 
    Serial.println(httpResponseCode); 
 
   }else{
 
    Serial.println("Error on sending POST");
 
   }
 
   http.end();  //Free resources
 
 }else{
 
    Serial.println("Error in WiFi connection");   
 
 }
  
}

//control mux by setting bits high and low 
void setMUX(int channel){
    //set S0
    digitalWrite(18, bitRead(channel, 0));
    digitalWrite(25, bitRead(channel, 0));

    //set S1
    digitalWrite(19, bitRead(channel, 1));
    digitalWrite(26, bitRead(channel, 1));

    //set s2
    digitalWrite(21, bitRead(channel, 2));
    digitalWrite(27, bitRead(channel, 2));
    delay(500);
  
}


void setup() {

//Trigger MUX S0, S1, S2
pinMode(18, OUTPUT);
pinMode(19, OUTPUT);
pinMode(21, OUTPUT);

//ECHO MUX S0, S1, S2
pinMode(25, OUTPUT);
pinMode(26, OUTPUT);
pinMode(27, OUTPUT);


Serial.begin(115200); // Starts the serial communication

//connect to wifi
WiFi.begin(ssid, password);

while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
 
Serial.println("Connected to the WiFi network");
 
  
}



void loop() {

//check the 6 sensors
for(int k = 0; k<6; k++){
  
setMUX(k);

int reading = sonar.ping_cm(); //read distance in cm
if(reading > 0 && reading < 15){ //only reading within 0-15cm of the sensor counts. 
  parkingSpotsNew[k] = 1;
}else{
  parkingSpotsNew[k] = 0;
}


}
// Prints the distance on the Serial Monitor
for(int i = 0; i<6;i++){
Serial.print("Parking spot new");
Serial.print(i+1);
Serial.print(" status: ");
Serial.print(parkingSpotsNew[i]);
Serial.println();
}
Serial.println();
Serial.println();

//error-correction
checkError();

for(int i = 0; i<6;i++){
Serial.print("Parking spot ");
Serial.print(i+1);
Serial.print(" corrected status: ");
Serial.print(parkingSpots[i]);
Serial.println();
}

//construct message
constructMsg();

//send message
sendData();

//delay system to save energy and make sure nothing crashes due to running too fast
delay(5000);



}
