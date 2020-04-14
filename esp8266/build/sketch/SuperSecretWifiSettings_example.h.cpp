#include <Arduino.h>
#line 1 "c:\\Users\\jcjve\\source\\repos\\sunscreen-controller\\SuperSecretWifiSettings_example.h"
// #pragma once
// SuperSecretWifiSettings.h
// Uset to store the wifi password and SSID
// put in your custom libraries
// you can also include these constants in the sketch of course, but not suitable for github uploads :-)


// const char* SSID = "your SSID";
//const char* PASSWORD = "your password";

#line 1 "c:\\Users\\jcjve\\source\\repos\\sunscreen-controller\\sunscreen.ino"
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <SuperSecretWifiSettings.h> // File containing const char*'s for SSID & PASSWORD
void setup()
{
}

void loop() {
    
}

