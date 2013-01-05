//This is for a PIR from Parallax

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
 This is the code for a basic sensor box, we have a sketch for every kind of sensor I could get my hands on, measure the results and send them through to our monitoring server. The chances are that your setup will be different, eg. you may want to only run temperature sensors or only use certain sensors... The code below can pretty much be changed to do anything but it intended to give you a structure to modify for whatever purpose...
*/

//Enter a MAC address and IP address for your controller below.
byte mac[] = { 0x90, 0xA2, 0xDA, 0x00, 0x7E, 0x4E };//MAC Address of your Ethernet Shield, eg. on my shield it is 90-A2-DA-00-7E-4E
char update_id[] = "MotionSensor";//This is a unique id from the control panel at https://client.onms.net/
//IPAddress server(88,198,36,51); //Report to our servers IP address, ie. www.onms.net
char server[] = "www.onms.net"; //Report to our servers hostname, ie. www.onms.net

//Define the pins being used:
int PassiveDetectorPin = 7; // Digital input pin for the Passive Infrared Sensor (PIR) sensor
int motion_count = 0; //How many times the PIR picked-up motion in 1 minute

EthernetClient client; //Used to send values to www.onms.net

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
    client.print("&key=motion_count&value=");
    client.print(motion_count);
    client.println(" HTTP/1.1");
    client.println("Host: www.onms.net");
    client.println();
    Serial.println("Disconnecting from www.onms.net server...");
    client.stop();
  } else {
    Serial.println("Connection to www.on
ms.net failed...");
  }
}

void loop() {
  //Read the values from the sensor...
  motion_count = 0;  
  for (int a=1; a<=60; a++){
   if (digitalRead(PassiveDetectorPin) == HIGH) {//Read the PIR value, if HIGH then motion has been sensed, The NOC server will interpret it further...
    motion_count++;
   }
   //Delay between PIR readings...
   delay(1000);//Milliseconds, ie. run every second...
  }
  //Output to serial...
  Serial.print("PIR Motion Count: ");
  Serial.println(motion_count);
  //Send to remote server...
  sendValues();
}

