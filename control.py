import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO			# using Rpi.GPIO module
from time import sleep, time
import json

GPIO.setmode(GPIO.BCM)			# GPIO numbering
GPIO.setwarnings(False)			# enable warning from GPIO

AN2 = 13				# set pwm2 pin on MD10-Hat
AN1 = 12				# set pwm1 pin on MD10-hat
DIG2 = 24				# set dir2 pin on MD10-Hat
DIG1 = 26				# set dir1 pin on MD10-Hat

GPIO.setup(AN2, GPIO.OUT)		# set pin as output
GPIO.setup(AN1, GPIO.OUT)		# set pin as output
GPIO.setup(DIG2, GPIO.OUT)		# set pin as output
GPIO.setup(DIG1, GPIO.OUT)		# set pin as output

sleep(1)				# delay for 1 seconds

p1 = GPIO.PWM(AN1, 1000)		# set pwm for M1
p2 = GPIO.PWM(AN2, 1000)		# set pwm for M2

# MQTT broker address and port
#setup mqtt broker
mqttBroker = "broker.emqx.io"
port = 1883
keepAlive = 60

# Debouncing variables
last_command = None
last_command_time = 0
debounce_delay = 0.2  # Adjust this value as needed (in seconds)

def on_connect(self, client, userdata, rc):
    print("MQTT Connected.")
    self.subscribe("WasteDetectionOnRaspberryPi/controlCar")

# Define a callback function to handle incoming messages
def on_message(client, userdata, message):
    global last_command, last_command_time

    payload = message.payload.decode()
    current_time = time()
    print(f"Received message: {payload} on topic {message.topic}")
    
    # Parse the payload JSON
    payload_data = json.loads(payload)

    # Get the value of the "message" key
    command = payload_data["message"]

    # Perform actions based on the received key value
    if command != last_command:
        last_command = payload
        last_command_time = current_time

        print(f"Received message: {payload} on topic {message.topic}")

        # Perform actions based on the received key value
        if command == 'w':
            # Move forward
            print("w")
            GPIO.output(DIG1, GPIO.LOW)  # set AN1 as HIGH, M1B will turn ON
            GPIO.output(DIG2, GPIO.HIGH)  # set AN2 as HIGH, M2B will turn ON
            p1.start(80)  # set Direction for M1
            p2.start(80)  # set Direction for M2

        elif command == 'a':
            # Move left
            print("a")
            #GPIO.output(DIG1, GPIO.HIGH)
            GPIO.output(DIG2, GPIO.HIGH)
            #p1.start(100)
            p2.start(100)

        elif command == 's':
            # Move backward
            print("s")
            GPIO.output(DIG1, GPIO.HIGH)
            GPIO.output(DIG2, GPIO.LOW)
            p1.start(80)
            p2.start(80)

        elif command == 'd':
            # Move right
            print("d")
            GPIO.output(DIG1, GPIO.LOW)
            #GPIO.output(DIG2, GPIO.LOW)
            p1.start(100)
            #p2.start(100)

        elif command == 'stop':
            print("stop")
            # Stop movement
            GPIO.output(AN1, GPIO.LOW)  # set AN1 as LOW, M1B will STOP
            GPIO.output(AN2, GPIO.LOW)  # set AN2 as HIGH, M2B will STOP
            p1.start(0)  # Direction can ignore
            p2.start(0)
            
    elif current_time - last_command_time > debounce_delay:
        last_command_time = current_time

            
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttBroker, port)
client.loop_forever()
