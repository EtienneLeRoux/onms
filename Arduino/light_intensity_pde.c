/*

This is for a Light Dependent Resistor (LDR) sensor
Copyright (C) 2014 Etienne le Roux - monitman.com

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
char update_id[] = "";//This is a unique id from the control panel at https://www.onms.net/
char server[] = "www.onms.net"; //Report to our servers hostname, ie. www.onms.net

//Define the pins being used:
int LDRPin = 0; // select the analog input pin for the Light Dependent Resistor (LDR) sensors

EthernetClient client; //Used to send values to www.onms.net

int light_intensity = 0;
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
    client.print("/update.php?update_id=");
    client.print(update_id);
    client.print("&key1=");
    client.print(light_intensity);
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
  null_values = analogRead(LDRPin);//Delayed, tossed out reading...
  delay(100);//Delay before correct reading...
  light_intensity = analogRead(LDRPin);//Read the LDR value, darkness increases value...
  //Output to serial...
  Serial.print("Light Intensity: ");
  Serial.println(light_intensity);
  //Send to remote server...
  sendValues();
  //Delay between light intensity readings...
  delay(60000);//Milliseconds, ie. every 1 minute for 60 000 millis
}


