#include "HttpClient/HttpClient.h"

int led = D7;
int switch0 = D2;

String hostname = "192.168.2.5";
int port = 80;

HttpClient http;
http_header_t headers[] = {
    { "Content-Type", "application/json" },
    { "Accept" , "application/json" },
    { NULL, NULL } // NOTE: Always terminate headers with NULL
};
http_request_t request;
http_response_t response;

unsigned int nextTime = 0;

void setup() {
    pinMode(led, OUTPUT);
    pinMode(switch0, INPUT_PULLUP);

    request.hostname = hostname;
    request.port = port;
}

void toggle(bool on) {
    if (on) {
        digitalWrite(led, HIGH);
        request.path = "/api/v0/wemos/switches/switch0/on/";
    } else {
        digitalWrite(led, LOW);
        request.path = "/api/v0/wemos/switches/switch0/off/";
    }

    http.post(request, response, headers);
}

int oldSwitch0State = -1; // HIGH=1, LOW=0

void loop() {
    if (nextTime > millis()) {
        return;
    }

    int switch0State = digitalRead(switch0);

    if (switch0State != oldSwitch0State) {
        oldSwitch0State = switch0State;
        toggle(switch0State == HIGH);
    }

    nextTime = millis() + 250;
}