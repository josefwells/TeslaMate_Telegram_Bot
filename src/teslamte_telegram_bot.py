import os
import time

import paho.mqtt.client as mqtt

from telegram.bot import Bot
from telegram.parsemode import ParseMode

if os.getenv('BATTERY_ALERT') == None:
    print("Using default BATTERY_ALERT level: 50")
    BATTERY_ALERT = 50
else:
    BATTERY_ALERT = os.getenv('BATTERY_ALERT')
    
# A global dictionary works, but not using 3 global variables instead
status = {
    "home": False,
    "lowbat": False,
    "charge": False,
    "name": "the car",
    }


# initializing the bot with API_KEY and CHAT_ID
if os.getenv('TELEGRAM_BOT_API_KEY') == None:
    print("Error: Please set the environment variable TELEGRAM_BOT_API_KEY and try again.")
    exit(1)
bot = Bot(os.getenv('TELEGRAM_BOT_API_KEY'))

if os.getenv('TELEGRAM_BOT_CHAT_ID') == None:
    print("Error: Please set the environment variable TELEGRAM_BOT_CHAT_ID and try again.")
    exit(1)
chat_id = os.getenv('TELEGRAM_BOT_CHAT_ID')

# based on example from https://pypi.org/project/paho-mqtt/
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        print("Connected successfully to broker")
    else:
        print("Connection failed")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("teslamate/cars/1/geofence")
    client.subscribe("teslamate/cars/1/battery_level")
    client.subscribe("teslamate/cars/1/plugged_in")
    client.subscribe("teslamate/cars/1/display_name")


# The callback for when a PUBLISH message is received from the server.

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode()))

    if msg.topic == "teslamate/cars/1/display_name":
        status["name"] = str(msg.payload.decode())

    if msg.topic == "teslamate/cars/1/geofence":
        if msg.payload.decode() == "Home":
            status["home"] = True
        else:
            status["home"] = False

    if msg.topic == "teslamate/cars/1/battery_level":
        if int(msg.payload.decode()) < BATTERY_ALERT:
            status["lowbat"] = True
        else:
            status["lowbat"] = False

    if msg.topic == "teslamate/cars/1/plugged_in":
        if msg.payload.decode() == "true":
            status["charge"] = True
            bot.send_message(
                chat_id,
                text=f"<b>{status['name']} charging</b>",
                parse_mode=ParseMode.HTML,
            )
        else:
            status["charge"] = False
            bot.send_message(
                chat_id,
                text=f"<b>{status['name']} unplugged</b>",
                parse_mode=ParseMode.HTML,
            )


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


client.username_pw_set
if os.getenv('MQTT_BROKER_USERNAME') == None:
    pass
else:
    if os.getenv('MQTT_BROKER_PASSWORD') == None:
        client.username_pw_set(os.getenv('MQTT_BROKER_USERNAME', ''))
    else:
        client.username_pw_set(os.getenv('MQTT_BROKER_USERNAME', ''), os.getenv('MQTT_BROKER_PASSWORD', ''))

client.connect(os.getenv('MQTT_BROKER_HOST', '127.0.0.1'),
               int(os.getenv('MQTT_BROKER_PORT', 1883)), 60)

TIMEOUT=60*60  # 60 minutes
count = TIMEOUT
client.loop_start()  # start the loop

time.sleep(5)
bot.send_message(
    chat_id,
    text=f"<b>{status['name']} service online</b>",
    parse_mode=ParseMode.HTML,
)

try:
    while True:
        count = count+1
        time.sleep(1)
        if status["home"] and status["lowbat"] and not status["charge"] and count > TIMEOUT:
            bot.send_message(
                chat_id,
                text=f"<b>Plug in {status['name']}.</b>",
                parse_mode=ParseMode.HTML,
            )
            count = 0
except KeyboardInterrupt:
    print("exiting")

client.disconnect()
client.loop_stop()
