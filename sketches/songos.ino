#include "HttpClient/HttpClient.h"

int led0            = D0;
int playPauseSwitch = D6;

String hostname = "192.168.2.5";
int port = 80;

HttpClient http;
http_header_t headers[] = {
    { "Content-Type", "application/json" },
    { "Accept" , "application/json" },
    { NULL, NULL } // NOTE: Always terminate headers with NULL
};
http_request_t request;

void setup() {
  pinMode(led0, OUTPUT);
  pinMode(playPauseSwitch, INPUT_PULLUP);

  request.hostname = hostname;
  request.port = port;
}

void togglePlayPause(bool on) {
    http_response_t response;

    if (on) {
        request.path = "/api/v0/sonos/play/";
    } else {
        request.path = "/api/v0/sonos/pause/";
    }

    http.post(request, response, headers);
}

void setLedState() {
  http_response_t response;

  request.path = "/api/v0/sonos/Garden/";
  response.body = "";
  http.get(request, response, headers);

  if (response.body.indexOf("\"mute\": true") < 0) {
    digitalWrite(led0, HIGH);
  } else {
    digitalWrite(led0, LOW);
  }
}

unsigned int nextTime = 0;
unsigned int loopCount = 0;

int oldPlayPauseSwitchState = -1; // HIGH=1, LOW=0

void loop() {
  if (nextTime > millis()) {
      return;
  }

  ++loopCount;

  if (loopCount > 4) {
    loopCount = 0;
    setLedState();
  }

  int playPauseSwitchState = digitalRead(playPauseSwitch);

  if (playPauseSwitchState != oldPlayPauseSwitchState) {
      oldPlayPauseSwitchState = playPauseSwitchState;
      togglePlayPause(playPauseSwitchState == HIGH);
  }

  nextTime = millis() + 250;
}