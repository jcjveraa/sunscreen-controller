#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266mDNS.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPUpdateServer.h>
#include <WiFiClient.h>
#include "SuperSecretSettings.h" // File containing const char*'s for SSID & PASSWORD & KEY
#include <FS.h>                  // Include the SPIFFS library

// using https://github.com/vdwel/switchKaKu
#include <switchKaKu.h>

#define KAKUPIN D6
#define LED_PIN D4

#define TIMEOUT 1000 * 60 * 30 // 30 minute timeout

ESP8266WebServer server(80);
ESP8266HTTPUpdateServer httpUpdater;

// const static String openWeatherAPI = "https://api.openweathermap.org/data/2.5/onecall?lat=" + String(LAT) + "&lon=" + String(LON) + "&appid=" + String(OPENWEATHERMAP_ORG_KEY);

unsigned long lastPositionChangeTimestamp_luifel = 0;
unsigned long lastPositionChangeTimestamp_screen = 0;
unsigned long lastControllerContactMillis = 0;
byte currentPercentageOpen_luifel = 0;
byte currentPercentageOpen_screen = 0;

boolean moving_luifel = false;
unsigned long stopMoveTime;
boolean movementDirection;

boolean automaticModeEnabled_luifel = false;
boolean automaticModeEnabled_screen = false;

File uploadFile;

void setup()
{
    Serial.begin(115200);
    Serial.println();

    Serial.printf("Connecting to %s ", SSID_1);
    WiFi.mode(WIFI_STA);
    WiFi.begin(SSID_1, PASSWORD_1);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    }
    digitalWrite(LED_PIN, LOW);
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

    //Updater
    httpUpdater.setup(&server, OTAPATH, OTAUSER, OTAPASSWORD);

    server.onNotFound([]() {                                  // If the client requests any URI
        if (!handleFileRead(server.uri()))                    // send it if it exists
            server.send(404, "text/plain", "404: Not Found"); // otherwise, respond with a 404 (Not Found) error
    });

    server.on("/Operate", handleOpenCloseAutomatic);
    server.on("/OperateManual", handleOpenCloseManual);
    server.on("/CurrentPosition", handleGetCurrentPosition);

    server.on("/Operate_screen", handleOpenCloseAutomatic_screen);

    server.on("/Automatic", HTTP_GET, handleGetAutomaticMode);
    server.on("/Automatic", HTTP_POST, handleToggleAutomaticMode);
    server.on("/Automatic_screen", HTTP_POST, handleToggleAutomaticMode_screen);

    server.on("/files", HTTP_GET, handleFileList);
    server.on(
        "/files", HTTP_POST, []
        { server.send(200, "application/json", "{\"fileupload\":1}"); },
        handleFileUpload);

    server.begin(); // Actually start the server

    Serial.printf("Web server started, open %s in a web browser\n", WiFi.localIP().toString().c_str());

    lastControllerContactMillis = millis();
}

void loop()
{
    failSafe();
    if (moving_luifel)
    {
        manageMovement();
    }
    server.handleClient();
}

// Makes sure the screen will close in case there have been no commands for more than TIMEOUT duration
void failSafe()
{
    // Check for a rollover which will happen every 50 days
    // This will mess up the failsafe below, but acceptable risk
    if (millis() < lastControllerContactMillis)
    {
        lastControllerContactMillis = millis();
    }

    if (millis() > (lastControllerContactMillis + TIMEOUT) && currentPercentageOpen_luifel > 0)
    {
        switchKaku(KAKUPIN, TRANSMITTERID1, 1, 1, false, 3);
        currentPercentageOpen_luifel = 0;
    }
}

void manageMovement()
{
    // check the current time vs the moment we are supposed to stop moving_luifel
    if (millis() >= stopMoveTime)
    {
        // Stop the move
        switchKaku(KAKUPIN, TRANSMITTERID1, 1, 1, movementDirection, 3);
        moving_luifel = false;
    }
}

void handleGetAutomaticMode()
{
    const char *autoMode_l = automaticModeEnabled_luifel ? "true" : "false";
    const char *autoMode_s = automaticModeEnabled_screen ? "true" : "false";
    server.send(200, "application/json", "{\"automatic_mode\":\"" + String(autoMode_l) + "\", \"automatic_mode_screen\":\"" + String(autoMode_s) + "\"}");
}

void handleToggleAutomaticMode()
{
    if (checkKey())
    {
        automaticModeEnabled_luifel = !automaticModeEnabled_luifel;
        handleGetAutomaticMode();
    }
}

void handleToggleAutomaticMode_screen()
{
    if (checkKey())
    {
        automaticModeEnabled_screen = !automaticModeEnabled_screen;
        handleGetAutomaticMode();
    }
}

void handleOpenCloseAutomatic()
{
    if (automaticModeEnabled_luifel)
    {
        handleOpenClose();
    }

    else
    {
        server.send(409);
    }
}

void handleOpenCloseManual()
{
    handleOpenClose();
}

void handleOpenClose()
{
    if (checkKey())
    {
        if (checkArg("targetPercentageOpen") && checkArg("timestamp"))
        {
            // Although we may not take action, store that the controller made contact.
            lastControllerContactMillis = millis();

            // currentPositionOpen = server.arg("direction") == "Open";           // Default to the safe 'Close' option
            byte targetPercentageOpen = byte(server.arg("targetPercentageOpen").toInt());
            float movementTime = calculateMovementTime(targetPercentageOpen, 45.0);
            // Serial.println(movementTime + ", absolute value is " + abs(movementTime) );

            // Only move if we move more than one second
            if (abs(movementTime) > 1)
            {
                movementDirection = movementTime > 0;
                // Calculate how long we should move
                stopMoveTime = millis() + int(1000 * abs(movementTime));
                // Start the move
                switchKaku(KAKUPIN, TRANSMITTERID1, 1, 1, movementDirection, 3); //switch group 1, device 1, repeat 3, on
                moving_luifel = true;

                lastPositionChangeTimestamp_luifel = server.arg("timestamp").toInt();
                Serial.print("Setting luifel to position from " + String(currentPercentageOpen_luifel) + " to " + server.arg("targetPercentageOpen") + " \n");
                currentPercentageOpen_luifel = targetPercentageOpen;
                // Send the response
                handleGetCurrentPosition();
                // server.send(200, "application/json", "{\"command_received\":\"" + server.arg("targetPercentageOpen") + "\"}");
            }
            else
            {
                // Send a response indicating that we have not handled the request
                handleGetCurrentPosition_code(202);
            }
        }
    }
}

void handleOpenCloseAutomatic_screen()
{
    if (automaticModeEnabled_screen)
    {
        handleOpenClose_screen();
    }

    else
    {
        server.send(409);
    }
}

void handleOpenClose_screen()
{
    if (checkKey())
    {
        if (checkArg("targetPercentageOpen") && checkArg("timestamp"))
        {
            // Although we may not take action, store that the controller made contact.
            lastControllerContactMillis = millis();

            // currentPositionOpen = server.arg("direction") == "Open";           // Default to the safe 'Close' option
            byte targetPercentageOpen = byte(server.arg("targetPercentageOpen").toInt());
            float movementTime = calculateMovementTime(targetPercentageOpen, 45.0);
            // Serial.println(movementTime + ", absolute value is " + abs(movementTime) );

            // Only move if we move more than one second
            if (abs(movementTime) > 1)
            {
                movementDirection = movementTime > 0;
                // Calculate how long we should move
                stopMoveTime = millis() + int(1000 * abs(movementTime));
                // Start the move
                switchKaku(KAKUPIN, TRANSMITTERID2, 1, 1, movementDirection, 3); //switch group 1, device 1, repeat 3, on
                // moving_screen = true; // NOT IMPLEMENTED!!! Screen will just move up and down

                lastPositionChangeTimestamp_screen = server.arg("timestamp").toInt();
                Serial.print("Setting screen to position from " + String(currentPercentageOpen_screen) + " to " + server.arg("targetPercentageOpen") + " \n");
                currentPercentageOpen_screen = targetPercentageOpen;
                // Send the response
                handleGetCurrentPosition();
                // server.send(200, "application/json", "{\"command_received\":\"" + server.arg("targetPercentageOpen") + "\"}");
            }
            else
            {
                // Send a response indicating that we have not handled the request
                handleGetCurrentPosition_code(202);
            }
        }
    }
}

// Returns the amount of seconds the movement should last
// My sunscreen opens in 45 seconds
float calculateMovementTime(byte targetPercentageOpen, float totalOpenTime)
{
    if (targetPercentageOpen == 0)
    {
        return -100.0f;
    }

    if (targetPercentageOpen == 100)
    {
        return 100.0f;
    }

    float deltaMovement = targetPercentageOpen - currentPercentageOpen_luifel;
    return deltaMovement / 100.0 * totalOpenTime;
}

void handleGetCurrentPosition()
{
    handleGetCurrentPosition_code(200);
    // if (checkKey())
    // {
    //     Serial.print("Handling handleGetCurrentPosition()\n");
    //     server.send(200, "application/json", "{\"position\": \"" + String(currentPercentageOpen_luifel) + "\",\"lastPositionChangeTimestamp_luifel\": \"" + lastPositionChangeTimestamp_luifel + "\"" + "} ");
    // }
}

void handleGetCurrentPosition_code(int code)
{
    if (checkKey())
    {
        lastControllerContactMillis = millis();
        Serial.print("Handling handleGetCurrentPosition()\n");
        server.send(code, "application/json", "{\"position_luifel\": \"" + String(currentPercentageOpen_luifel) + "\",\"lastPositionChangeTimestamp_luifel\": \"" + lastPositionChangeTimestamp_luifel + "\"" + ", " +

                                                  "\"position_screen\": \"" + String(currentPercentageOpen_screen) + "\",\"lastPositionChangeTimestamp_screen\": \"" + lastPositionChangeTimestamp_screen + "\"" + "} ");
    }
}

// inspired by https://www.youtube.com/watch?v=QLGwI5tC9yk
void handleFileList()
{
    if (checkKey())
    {
        Serial.print("Handling handleGetCurrentPosition()\n");
        String path = "/";
        Dir dir = SPIFFS.openDir(path);
        String output = "{\"files\": [\"";
        bool firstFile = false;
        while (dir.next())
        {
            File entry = dir.openFile("r");
            if (!firstFile)
            {
                output += "\",\"";
            }
            else
            {
                firstFile = true;
            }
            output += String(entry.name()).substring(1); // Start at idx 1 to skip single /
            entry.close();
        }
        output += "\"]}";
        server.send(200, "application/json", output);
        Serial.print("sending: " + output + "\n");
    }
}

void handleFileUpload()
{
    if (checkKey())
    {
        HTTPUpload &upload = server.upload();
        String filename = upload.filename;
        if (upload.status == UPLOAD_FILE_START)
        {

            if (!filename.startsWith("/"))
            {
                filename = "/" + filename;
            }
            Serial.println("Handling fileupload for file " + filename);
            uploadFile = SPIFFS.open(filename, "w");
        }
        else if (upload.status == UPLOAD_FILE_WRITE)
        {
            if (uploadFile)
            {
                uploadFile.write(upload.buf, upload.currentSize);
                Serial.println("Handling fileupload for file " + filename + " start write!");
            }
            else
                Serial.println("Handling fileupload for file " + filename + " failed in step UPLOAD_FILE_WRITE!");
        }
        else if (upload.status == UPLOAD_FILE_END)
        {
            if (uploadFile)
            {
                uploadFile.close();
                Serial.println("Handling fileupload for file " + filename + " complete!");
                Serial.println(String(upload.totalSize) + " bytes written.");
            }
            else
                Serial.println("Handling fileupload for file " + filename + " failed in step UPLOAD_FILE_END!");
        }
    }
}

bool checkKey()
{
    if (checkArg("key"))
    {
        bool keycheck = server.arg("key") == KEY; // KEY to be defined somewhere safe
        if (keycheck)
        {
            Serial.print("Correct key provided\n");
            return true;
        }
        else
        {
            Serial.print("Incorrect key provided!\n");
            server.send(403, "text/plain", "Hax!"); // KEY Invalid
            return false;
        }
    }
}

bool checkArg(String arg)
{
    if (!server.hasArg(arg))
    {
        Serial.print("Argument " + arg + " was not supplied\n");
        server.send(400, "text/plain", "Invalid parameters");
        return false;
    }
    Serial.print("Argument " + arg + " was supplied, all OK\n");
    // All good!
    return true;
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
