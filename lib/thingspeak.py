import binascii
import machine

from mqtt import MQTTClient
from datapoint import DataPoint
from keychain0 import *

def send_to_thingspeak(datapoints):
    # data = DataPoint(datapoints)

    thingspeak_data = datapoints.to_thingspeak()
    print('sending data\n{}'.format(thingspeak_data))

    success = False
    number_of_retries = 3

    while not success and number_of_retries > 0:
        try:
            client_id = binascii.hexlify(machine.unique_id())

            client = MQTTClient(client_id,
                                'mqtt.thingspeak.com',
                                user='wipy{}'.format(client_id),
                                password=MQTT_API_KEY,
                                port=8883,
                                ssl=True)
            client.connect()

            client.publish(topic='channels/{}/publish/{}'.format(CHANNEL, MQTT_WRITE_API_KEY),
                           msg=thingspeak_data)
            client.disconnect()
            success = True
        except OSError as e:
            print('network error: {}'.format(e.errno))
            number_of_retries -= 1

    return success
