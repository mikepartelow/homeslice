# sonos

Do stuff with a Sonos. Works well with [homebridge-http](https://github.com/rudders/homebridge-http).

```json
{
    "accessory": "Http",
    "name": "Secret Agent",
    "switchHandling": "yes",
    "http_method": "GET",
    "on_url": "http://nucnuc.local/api/v0/sonos/secret-agent/ON",
    "off_url": "http://nucnuc.local/api/v0/sonos/secret-agent/OFF",
    "status_url": "http://nucnuc.local/api/v0/sonos/secret-agent/STATUS",
    "status_on": "ON",
    "status_off": "OFF",
    "service": "Switch",
    "sendimmediately": "",
    "username": "",
    "password": "",
}
```
