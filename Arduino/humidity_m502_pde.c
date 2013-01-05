//This is for the M502 humidity sensor

//Author: Etienne le Roux (etienne@linux.com) for ONMS.Net
//Address: PoBox 634, Menlyn Retail Park, Pretoria, South Africa, 0063

/*
    Copyright (C) 2012 Etienne le Roux

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/

//LGPL Libraries:
#include <SPI.h>
#include <EthernetServer.h>
#include <EthernetClient.h>
#include <Ethernet.h>
#include <EthernetUdp.h>
#include <Dns.h>
#include <util.h>
#include <Dhcp.h>
#include "string.h"

/*
 This is the code for a basic sensor box, we have a sketch for every kind of sensor I could get my hands on, measure the results and send them through to our monitoring server. The chances are that your setup will be different, eg. you may want to only run humidity sensors or only use certain sensors... The code below can pretty much be changed to do anything but it intended to give you a structure to modify for whatever purpose...
*/

//Enter a MAC address and IP address for your controller below.
byte mac[] = { 0x90, 0xA2, 0xDA, 0x00, 0x7E, 0x4E };//MAC Address of your Ethernet Shield, eg. on my shield it is 90-A2-DA-00-7E-4E
char update_id[] = "SouthAfrica";//This is a unique id from the control panel at https://client.onms.net/
//IPAddress server(88,198,36,51); //Report to our servers IP address, ie. www.onms.net
char server[] = "www.onms.net"; //Report to our servers hostname, ie. www.onms.net

//Define the pins being used:
int HumidityPin = 0; //Analog input pin for the M502 Humidity sensor

EthernetClient client; //Used to send values to www.onms.net

float reading = 0;
float humidity = 0;
int val = 0; // variable to store the value coming from the sensor
int null_values = 0;

void setup() {
 Serial.begin(9600); // initialize serial communication with computer
 // start the Ethernet connection and the server:
 Ethernet.begin(mac);//Start the ethernet library and do DHCP...
}

void sendValues(){//Send values to www.onms.net server
  if (client.connect(server, 80)) {
    Serial.println("Connected to www.onms.net server...");
    client.print("GET ");
    client.print("/?update_id=");
    client.print(update_id);
    client.print("&key=humidity&value=");
    client.print(humidity);
    client.println(" HTTP/1.1");
    client.println("Host: www.onms.net");
    client.println();
    Serial.println("Disconnecting from www.onms.net server...");
    client.stop();
  } else {
    Serial.println("Connection to www.onms.net failed...");
  }
}

void loop() {
  //Read the values from the sensor...
  null_values = analogRead(HumidityPin);//Delayed, tossed out reading...
  delay(100);//Delay before correct reading...
  reading = analogRead(HumidityPin); // read the value from the sensor
  humidity = reading/3.4;//every 3.4 increase in reading indicates 1% increase in humidity
  if (humidity > 100){//Ensure the max humidity % is 100, not that it ever should be, hehe...
   humidity = 100;
  }
  //Output the humidity to serial...
  Serial.print("Humidity %: ");
  Serial.println(humidity);
  //Send to remote server...
  sendValues();
  //Delay between humidity readings...
  delay(60000);//Milliseconds, ie. every 1 minute for 60 000 millis
}



