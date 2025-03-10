#!/usr/bin/python3
import argparse
import json
import logging
import paho.mqtt.client as paho
import ssl
import subprocess
import sys
import time
from datetime import datetime
import tzlocal

PUSH_ALL = {"pushing": {"sequence_id": "0", "command": "pushall"}}

def publish(client, userdata, msg):
    result = client.publish(f"device/{userdata['device_id']}/request", json.dumps(msg))
    status = result[0]
    if status == 0:
        logging.info(f"Sent {msg} to topic device/{userdata['device_id']}/request")
        return True
    else:
        logging.info(f"Failed to send message to topic device/{userdata['device_id']}/request")
        return False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT server")
        client.subscribe(f"device/{userdata['device_id']}/report")
        publish(client, userdata, PUSH_ALL)
    else:
        logging.error(f"Failed to connect with result code {rc}")
        client.disconnect()

def on_disconnect(client, userdata, rc):
    logging.warning("Disconnected from MQTT server with result code {}".format(str(rc)))

def on_message(client, userdata, msg):
    data_dict = json.loads(msg.payload.decode('utf-8'))
    process_message(data_dict, userdata['callback_notifier'])

def process_message(data, callback_notifier):
    if 'print' in data:
        print_info = data['print']
        gcode_state = print_info.get('gcode_state', '')
        percent_done = print_info.get('mc_percent', 0)
        previous_state = process_message.previous_state
        if gcode_state != previous_state and gcode_state != '':
            print(f"Transition from {previous_state} to {gcode_state} at {percent_done}%")
            process_message.previous_state = gcode_state
            if previous_state == 'RUNNING' and gcode_state != 'RUNNING':
                msg_text = f"Print Status: {gcode_state} at {percent_done}% completion."
                send_notification(callback_notifier, msg_text)

process_message.previous_state = 'NULL'

def send_notification(callback_notifier, message):
    logging.info(message)
    subprocess.run([callback_notifier, message], check=True)

def parse_args():
    parser = argparse.ArgumentParser(description='Monitor Bambu Labs 3D printer status.')
    parser.add_argument('host', help='Printer IPv4 address')
    parser.add_argument('access_code', help='Access Code')
    parser.add_argument('serial_number', help='Serial Number from Bambu Studio')
    parser.add_argument('callback_notifier', help='Path to the callback notifier executable')
    args = parser.parse_args()

    args.port = 8883
    args.user = "bblp"
    if not all([args.host, args.port, args.user, args.access_code, args.serial_number, args.callback_notifier]):
        parser.print_usage()
        sys.exit(1)

    args.password = args.access_code
    args.device_id = args.serial_number

    return args

def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting Bambu Labs printer monitor")

    while True:
        try:
            client = paho.Client(userdata={
                'device_id': args.device_id,
                'callback_notifier': args.callback_notifier
            })
            client.tls_set(cert_reqs=ssl.CERT_NONE)
            client.tls_insecure_set(True)
            client.username_pw_set(args.user, args.password)
            client.on_connect = on_connect
            client.on_disconnect = on_disconnect
            client.on_message = on_message
            client.connect(args.host, args.port, keepalive=60)
            client.loop_forever()
        except KeyboardInterrupt:
            logging.info("Program terminated by user")
            sys.exit(0)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        logging.info("Connection lost, waiting 30 seconds before reconnecting...")
        time.sleep(30)

if __name__ == "__main__":
    main()
