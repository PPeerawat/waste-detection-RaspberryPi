from time import sleep
from picamera2 import Picamera2
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import json
import cv2
import base64
from read_mq import MQ

#setup mqtt broker
mqttBroker = "broker.emqx.io"
port = 1883
keepAlive = 60

class MQTT():
    def publish(self, class_predicted, mq_data):
        def send(class_predicted, mq_data):
    
            data_to_send = {
                "class_predicted": class_predicted,
                "mq_data": mq_data
            }
    
            json_data = json.dumps(data_to_send)
    
            result = client.publish("WasteDetectionOnRaspberryPi", json_data, 0)
            print(result)
    
        def on_connect(client, userdata, flags, reason_code):
            print("CONNACK received with code %d." % (reason_code))
    
        def on_publish(client, userdata, mid):
            print("published..." + str(mid))
            #client.loop_stop()
            
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_publish = on_publish

        client.connect(mqttBroker, port, keepAlive)
        #client.loop_start()
        print('running...')
        try:
            print("send data...")
            send(class_predicted, mq_data)

        finally:
            print("cleanup")
        


