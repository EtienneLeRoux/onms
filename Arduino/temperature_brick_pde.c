/*

This is for the SeeedStudio Thermistor Electronic Brick
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
char update_id[] = "CiscoASA";//This is a unique id from the control panel at https://www.onms.net/
//IPAddress server(88,198,36,51); //Report to our servers IP address, ie. www.onms.net
char server[] = "www.onms.net"; //Report to our servers hostname, ie. www.onms.net

//Define the pins being used:
int TemperaturePin = 0; //Analog input pin for the Temperature sensor SeeedStudio electronic brick

EthernetClient client; //Used to send values to www.onms.net

float temperature = 0;
float base_temperature = 0;
int val = 0; // variable to store the value coming from the sensor
int baseline = 0;
int null_values = 0;

void setup() {
 Serial.begin(9600); // initialize serial communication with computer
 // start the Ethernet connection and the server:
 Ethernet.begin(mac);//Start the ethernet library and do DHCP...
 null_values = analogRead(TemperaturePin);//Delayed, tossed out reading...
 delay(100);//Delay before correct reading...
 temperature = (5.0 * analogRead(TemperaturePin) * 100.0)/1024.0;//Calc celcius
 base_temperature = temperature;
}

void sendValues(){//Send values to www.onms.net server
  if (client.connect(server, 80)) {
    Serial.println("Connected to www.onms.net server...");
    client.print("GET ");
    client.print("/?update_id=");
    client.print(update_id);
    client.print("&key=temperature&value=");
    client.print(temperature);
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
  null_values = analogRead(TemperaturePin);//Delayed, tossed out reading...
  delay(100);//Delay before correct reading...
  temperature = (analogRead(TemperaturePin)-248)/10;//Calc celcius, -248 needs to be adjusted until temperature matches a normal thermometer, ie. you need to calibrate!
  //Output the temperature to serial...
  Serial.print("Temperature: ");
  Serial.println(temperature);
  //Send to remote server...
  sendValues();
  //Delay between temperature readings...
  delay(60000);//Milliseconds, ie. every 1 minute for 60 000 millis
}
