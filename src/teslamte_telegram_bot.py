'''Bot that reads TeslaMate MQTT and sends alerts via telegram'''

import os
import time
import sys

import paho.mqtt.client as mqtt

from telegram.bot import Bot
from telegram.parsemode import ParseMode

# A global dictionary works, but not using 3 global variables.. callbacks, something, something.
status = {
    "home": False,
    "lowbat": False,
    "charge": False,
    "name": "Tesla",
    "level": 100,
    }

# Set Battery Global
BATTERY_ALERT = int(os.getenv('BATTERY_ALERT', "50"))
print(f"Using BATTERY_ALERT level: {BATTERY_ALERT}")

# Set TIMEOUT for repeated alerts
TIMEOUT = int(os.getenv('TIMEOUT', str(60*60)))
print(f"Using TIMEOUT: {TIMEOUT}")

# initializing the bot with API_KEY and CHAT_ID
if os.getenv('TELEGRAM_BOT_API_KEY') is None:
    print("Error: Please set the environment variable TELEGRAM_BOT_API_KEY and try again.")
    sys.exit(1)
bot = Bot(os.getenv('TELEGRAM_BOT_API_KEY'))

if os.getenv('TELEGRAM_BOT_CHAT_ID') is None:
    print("Error: Please set the environment variable TELEGRAM_BOT_CHAT_ID and try again.")
    sys.exit(1)
chat_id = os.getenv('TELEGRAM_BOT_CHAT_ID')

# Disable check since I'm maintaining callback compatibiliy
# pylint: disable=unused-argument
def on_connect(client, userdata, flags, return_code):
    '''The callback for when the client receives a CONNACK response from the server.'''

    print("Connected with result code "+str(return_code))
    if return_code == 0:
        print("Connected successfully to broker")
    else:
        print("Connection failed")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("teslamate/cars/1/geofence")
    client.subscribe("teslamate/cars/1/battery_level")
    client.subscribe("teslamate/cars/1/plugged_in")
    client.subscribe("teslamate/cars/1/display_name")


# Disable check since I'm maintaining callback compatibiliy
# pylint: disable=unused-argument
def on_message(client, userdata, msg):
    '''The callback for when a PUBLISH message is received from the server.'''
    print(msg.topic+" "+str(msg.payload.decode()))

    if msg.topic == "teslamate/cars/1/display_name":
        status["name"] = str(msg.payload.decode())

    if msg.topic == "teslamate/cars/1/geofence":
        if msg.payload.decode() == "Home":
            status["home"] = True
        else:
            status["home"] = False

    if msg.topic == "teslamate/cars/1/battery_level":
        status["level"] = int(msg.payload.decode())
        if int(msg.payload.decode()) < BATTERY_ALERT:
            status["lowbat"] = True
        else:
            status["lowbat"] = False

    if msg.topic == "teslamate/cars/1/plugged_in":
        if msg.payload.decode() == "true":
            status["charge"] = True
            bot.send_message(
                chat_id,
                text="<b>Charging</b>",
                parse_mode=ParseMode.HTML,
            )
        else:
            status["charge"] = False
            bot.send_message(
                chat_id,
                text="<b>Unplugged</b>",
                parse_mode=ParseMode.HTML,
            )


# Set up client and callback functions
my_client = mqtt.Client()
my_client.on_connect = on_connect
my_client.on_message = on_message


# my_client.username_pw_set
if os.getenv('MQTT_BROKER_USERNAME') is None:
    pass
else:
    if os.getenv('MQTT_BROKER_PASSWORD') is None:
        my_client.username_pw_set(os.getenv('MQTT_BROKER_USERNAME', ''))
    else:
        my_client.username_pw_set(os.getenv('MQTT_BROKER_USERNAME', ''),
                                  os.getenv('MQTT_BROKER_PASSWORD', ''))

my_client.connect(str(os.getenv('MQTT_BROKER_HOST', '127.0.0.1')),
                  int(os.getenv('MQTT_BROKER_PORT', '1883')),
                  60)

# This starts the client checking for messages
my_client.loop_start()

# Initial
bot.send_message(
    chat_id,
    text=f"<b>{status['name']} service online</b>",
    parse_mode=ParseMode.HTML,
)

def main_loop():
    ''' This uses all the previous setup to run an infinite loop checking on our status '''
    count = TIMEOUT
    try:
        while True:
            count = count+1
            time.sleep(1)
            if status["home"] and status["lowbat"] and not status["charge"] and count > TIMEOUT:
                bot.send_message(
                    chat_id,
                    text=f"<b>Battery Level: {str(status['level'])} Plug in {status['name']}.</b>",
                    parse_mode=ParseMode.HTML,
                )
                count = 0
    except KeyboardInterrupt:
        print("exiting")

    my_client.disconnect()
    my_client.loop_stop()

main_loop()

