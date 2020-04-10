#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266mDNS.h>
#include <ESP8266WebServer.h>
#include <WiFiClient.h>
#include "SuperSecretSettings.h" // File containing const char*'s for SSID & PASSWORD & KEY
#include <FS.h>                  // Include the SPIFFS library

// using https://github.com/vdwel/switchKaKu
#include <switchKaKu.h>
#define TRANSMITTERID1 34107862 // Randomly chosen
#define KAKUPIN 1

ESP8266WebServer server(80);

bool currentPositionOpen = false;
const static String openWeatherAPI = "https://api.openweathermap.org/data/2.5/onecall?lat=" + LAT + "&lon=" + LON + "&appid=" + OPENWEATHERMAP_ORG_KEY;

long lastUpdateTime = 0;

void setup()
{
    Serial.begin(115200);
    Serial.println();

    Serial.printf("Connecting to %s ", SSID);
    WiFi.begin(SSID, PASSWORD);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println(" connected");

    if (MDNS.begin("esp8266-sunscreen.local"))
    { // Start the mDNS responder for esp8266.local
        Serial.println("mDNS responder started");
    }
    else
    {
        Serial.println("Error setting up MDNS responder!");
    }

    SPIFFS.begin(); // Start the SPI Flash Files System

    server.onNotFound([]() {                                  // If the client requests any URI
        if (!handleFileRead(server.uri()))                    // send it if it exists
            server.send(404, "text/plain", "404: Not Found"); // otherwise, respond with a 404 (Not Found) error
    });

    server.on("/Operate", handleOpenClose);
    server.on("/CurrentPosition", handleGetCurrentPosition);

    server.begin(); // Actually start the server

    Serial.printf("Web server started, open %s in a web browser\n", WiFi.localIP().toString().c_str());
}

void loop()
{
    server.handleClient();
}

void handleOpenClose()
{
    if (checkKey())
    {
        if (checkArg("direction"))
        {
            currentPositionOpen = server.arg("direction") == "Open";           // Default to the safe 'Close' option
            switchKaku(KAKUPIN, TRANSMITTERID1, 1, 1, currentPositionOpen, 1); //switch group 1, device 1, repeat 3, on
            server.send(200, "text/plain", "Sending command: " + server.arg("direction"));
        }
    }
}

void handleGetCurrentPosition()
{
    if (checkKey())
    {
        String position = currentPositionOpen ? "Open" : "Closed";
        server.send(200, "text/plain", "{\"position\": \"" + position + "\"} " + server.arg("direction"));
    }
}

bool checkKey()
{
    if (checkArg("key"))
    {
        bool keycheck = server.arg("key") == KEY; // KEY to be defined somewhere safe
        if (keycheck)
        {
            return true;
        }
        else
        {
            server.send(403, "text/plain", "Hax!"); // KEY Invalid
            return false;
        }
    }
}

bool checkArg(String arg)
{
    if (!server.hasArg(arg))
    {
        server.send(400, "text/plain", "Invalid parameters");
    }
}

// from https://tttapa.github.io/ESP8266/Chap11%20-%20SPIFFS.html
bool handleFileRead(String path)
{ // send the right file to the client (if it exists)
    Serial.println("handleFileRead: " + path);
    if (path.endsWith("/"))
        path += "index.html";                  // If a folder is requested, send the index file
    String contentType = getContentType(path); // Get the MIME type
    String pathWithGz = path + ".gz";
    if (SPIFFS.exists(pathWithGz) || SPIFFS.exists(path))
    {                                                       // If the file exists, either as a compressed archive, or normal
        if (SPIFFS.exists(pathWithGz))                      // If there's a compressed version available
            path += ".gz";                                  // Use the compressed version
        File file = SPIFFS.open(path, "r");                 // Open the file
        size_t sent = server.streamFile(file, contentType); // Send it to the client
        file.close();                                       // Close the file again
        Serial.println(String("\tSent file: ") + path);
        return true;
    }
    Serial.println(String("\tFile Not Found: ") + path);
    return false; // If the file doesn't exist, return false
}

String getContentType(String filename)
{
    if (filename.endsWith(".html"))
        return "text/html";
    else if (filename.endsWith(".css"))
        return "text/css";
    else if (filename.endsWith(".js"))
        return "application/javascript";
    else if (filename.endsWith(".ico"))
        return "image/x-icon";
    else if (filename.endsWith(".gz"))
        return "application/x-gzip";
    return "text/plain";
}
