from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import RPi.GPIO as GPIO
import json
import math
from sympy import symbols
from utils.command_line_utils import CommandLineUtils
from datetime import datetime


cmdData = CommandLineUtils.parse_sample_input_pubsub()

received_count = 0
received_all_event = threading.Event()

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count
    received_count += 1
    if received_count == cmdData.input_count:
        received_all_event.set()

# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailuredata)
    print("Connection failed with error code: {}".format(callback_data.error))

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")
    
#def calcSoundValue():
	

if __name__ == '__main__':
    #setting device ID
    deviceID = 1

    #setup code for the sound sensors and calculate the average for each of them
    # Set pin numbering mode
    GPIO.setmode(GPIO.BCM)

    # Define pins
    microphonePin1 = 14
  
    microphonePin3 = 18
    ledPin = 25
    ledPinlow = 7

    # Set pin modes
    GPIO.setup(microphonePin1, GPIO.IN)
    GPIO.setup(microphonePin3, GPIO.IN)
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.setup(ledPinlow, GPIO.OUT)

    # Initialize variables
    count1 = count3 = 0
    total1 = total3 = 0
    interval = 2  # 2-second interval
    previous_time = time.time()
        
    # Create the proxy options if the data is present in cmdData
    proxy_options = None
    if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
        proxy_options = http.HttpProxyOptions(
            host_name=cmdData.input_proxy_host,
            port=cmdData.input_proxy_port)

    # Create a MQTT connection from the command line data
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=cmdData.input_endpoint,
        port=cmdData.input_port,
        cert_filepath=cmdData.input_cert,
        pri_key_filepath=cmdData.input_key,
        ca_filepath=cmdData.input_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=cmdData.input_clientId,
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=proxy_options,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed)

    if not cmdData.input_is_ci:
        print(f"Connecting to {cmdData.input_endpoint} with client ID '{cmdData.input_clientId}'...")
    else:
        print("Connecting to endpoint with client ID")
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    message_count = cmdData.input_count
    message_topic = cmdData.input_topic

    #Custom code for our specific device
    deviceID = 1
    
    fullTime = datetime.now()
    dateTimeString = fullTime.strftime("%d/%m/%Y %H:%M:%S")
    soundVal = 15
    OutputDict = {'deviceID': deviceID, 'soundVal': soundVal,'currentTime': dateTimeString}

    # Subscribe
    print("Subscribing to topic '{}'...".format(message_topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=message_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    if OutputDict:
        if message_count == 0:
            print("Sending messages until program killed")
        else:
            print("Sending {} message(s)".format(message_count))

        publish_count = 1

while True:
        current_time = time.time()
        
        # Read values from sound sensors
        microphoneValue1 = GPIO.input(microphonePin1)
     
        microphoneValue3 = GPIO.input(microphonePin3)
        
        # Update counters and totals
        total1 += microphoneValue1
        
        total3 += microphoneValue3
        count1 += 1
      
        count3 += 1
        
        # Check if 2 seconds have passed
        if current_time - previous_time >= interval:
            # Calculate average values
            averageValue1 = total1 / count1
          
            averageValue3 = total3 / count3
            
            # Print average values
            print(f"Sensor 1 Average: {averageValue1}")
            
            print(f"Sensor 3 Average: {averageValue3}")
            
            # Check if LED should be turned on
            if averageValue1 > 0.25 or averageValue3 > 0.25:
                GPIO.output(ledPin, GPIO.HIGH)
            else:
                GPIO.output(ledPin, GPIO.LOW)
                
            if 0.25 > averageValue1 > 0.14 or 0.25 > averageValue3 > 0.14:
                GPIO.output(ledPinlow, GPIO.HIGH)
            else:
                GPIO.output(ledPinlow, GPIO.LOW)
            
            #Forming the message to be sent via MQTT established earlier
            soundVal = (averageValue1 + averageValue3) / 2
           
            DB = 350*soundVal+10
            print(DB)
            
            fullTime = datetime.now()
            dateTimeString = fullTime.strftime("%d/%m/%Y %H:%M:%S")
            outputDict = {'deviceID': deviceID, 'sensor1': averageValue1, 'sensor2': averageValue3, 'soundVal': DB ,'currentTime': dateTimeString}
            #outputVal = soundVal
            #forming the message
            message_json = json.dumps(outputDict)
            print(message_json)
            mqtt_connection.publish(
                topic=message_topic,
                payload=message_json,
                qos=mqtt.QoS.AT_LEAST_ONCE)
            
            
            # Reset counters and totals
            count1 = count3 = 0
            total1 = total3 = 0
            previous_time = current_time
            
            #after this, return to top of loop





