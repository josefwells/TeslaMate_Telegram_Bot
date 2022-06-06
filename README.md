# TeslaMate Telegram Bot

This is a telegram bot written in Python to notify by Telegram message when their car is A) In the "Home" geofence, B) Not Plugged in, and C) Under some BATTERY_ALERT level (default 50%). It uses the MQTT topic which [TeslaMate](https://github.com/adriankumpf/teslamate) offers.

## Table of contents

- [TeslaMate Telegram Bot](#teslamate-telegram-bot)
  - [Table of contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Update](#update)
  - [Contributing](#contributing)
  - [Donation](#donation)
  - [Disclaimer](#disclaimer)

## Requirements

- A Machine that's always on and runs [TeslaMate](https://github.com/adriankumpf/teslamate)
- Docker _(if you are new to Docker, see [Installing Docker and Docker Compose](https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-raspberry-pi-in-5-simple-steps-3mgl))_
- External internet access, to send telegram messages.
- A mobile with [Telegram](https://telegram.org/) client installed
- your own Telegram Bot, see [Creating a new telegram bot](https://core.telegram.org/bots#6-botfather)
- your own Telegram chat id, see [get your telegram chat id](https://docs.influxdata.com/kapacitor/v1.5/event_handlers/telegram/#get-your-telegram-chat-id)

## Installation

Make sure you fulfill the [Requirements](#requirements).

It is recommended to backup your data first.

This document provides the necessary steps for installation of TeslaMate Telegram Bot on a any system that runs Docker.

This setup is recommended only if you are running TeslaMate Telegram Bot **on your home network**, as otherwise your telegram API tokens might be at risk.

1. Create a file called `docker-compose.yml` with the following content (adopt with your own values):

   ```yml title="docker-compose.yml"
      version: "3"

      services:
        teslamatetelegrambot:
          image: teslamatetelegrambot/teslamatetelegrambot:latest
          restart: unless-stopped
          environment:
	    - BATTERY_ALERT=50 #optional, default 50
            - MQTT_BROKER_HOST=IP_Adress
            - MQTT_BROKER_PORT=1883 #optional, default 1883
            - MQTT_BROKER_USERNAME=username #optional, only needed when broker has authentication enabled
            - MQTT_BROKER_PASSWORD=password #optional, only needed when broker has authentication enabled
            - TELEGRAM_BOT_API_KEY=secret_api_key
            - TELEGRAM_BOT_CHAT_ID=secret_chat_id
          ports:
            - 1883
          build:
            context: .
            dockerfile: Dockerfile
   ```

2. Build and start the docker container with `docker-compose up --build`. To run the containers in the background add the `-d` flag:

   ```bash
   docker-compose up --build -d
   ```

## Update

Restart the stack with `docker-compose up --build`. To run the containers in the background add the `-d` flag:

```bash
docker-compose up --build -d
```

## Contributing

All contributions are welcome and greatly appreciated!

## Disclaimer

Please note that the use of the Tesla API in general and this software in particular is not endorsed by Tesla. Use at your own risk.
