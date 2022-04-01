import sys # needed to exit

import matplotlib.pyplot as plt # needed for graphs
import numpy as np # needed for graph
import collections # needed for deque
import pika # needed for rabbitMQ

import time # needed for sleep
from threading import Thread # needed for threads

import RPi.GPIO as GPIO # needed to use GPIO

import warnings # needed for filtering
warnings.filterwarnings( "ignore") # filter user warning

class LiveView:
    '''
    Simple Python class to visualize sensor data
    '''

    def __init__(self, bufferSize):

        

        # Ring Buffer setup
        self.buffer = collections.deque(np.full(int(bufferSize), 0.0))
        print(str(self.buffer))

        # GPIO Setup
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(36, GPIO.OUT) # Red pin on LED
        GPIO.setup(38, GPIO.OUT) # Green pin on LED
        GPIO.setup(40, GPIO.OUT) # Blue pin on LED

        # Sets startup color to green
        GPIO.output(36, GPIO.LOW)
        GPIO.output(38, GPIO.HIGH)
        GPIO.output(40, GPIO.LOW)
        

    def linkRabbit(self):
        """Setup and start lisenting for RabbitMQ messages
        """

        print("Listening for RabbitMQ messages")

        # RabbitMQ setup
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        #channel.exchange_declare(exchange='freqSweep', exchange_type='fanout')
        channel.exchange_declare(exchange='sensorRead', exchange_type='fanout')

        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        # channel.queue_bind(exchange='freqSweep', queue=queue_name)
        channel.queue_bind(exchange='sensorRead', queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.rabbitCallback, auto_ack=True)
        channel.start_consuming()

    def rabbitCallback(self, ch, method, properties, body):
        """Callback method for rabbitMQ
        Args:
            ch ([type]): [description]
            method ([type]): [description]
            properties ([type]): [description]
            body (String): The message body as a string
        """

        data = float(body)

        #update buffer by appending to right and poping left most value
        self.buffer.append(data)
        self.buffer.popleft()

        if data < 0.04:
            self.ledAlert("BLUE")
        elif data < 1:
            self.ledAlert("YELLOW")
        else:
            self.ledAlert("RED")

    def ledAlert(self, color):
        """
        Changes RGB LED to different colors to show alerts

        Args:
            color (str): RED, BLUE, GREEN, YELLOW, PURPLE, CYAN, WHITE, BLACK
        """

        if str(color).startswith("RED"):
            GPIO.output(36, GPIO.HIGH)
            GPIO.output(38, GPIO.LOW)
            GPIO.output(40, GPIO.LOW)
        elif str(color).startswith("GREEN"):
            GPIO.output(36, GPIO.LOW)
            GPIO.output(38, GPIO.HIGH)
            GPIO.output(40, GPIO.LOW)
        elif str(color).startswith("YELLOW"):
            GPIO.output(36, GPIO.HIGH)
            GPIO.output(38, GPIO.HIGH)
            GPIO.output(40, GPIO.LOW)
        elif str(color).startswith("BLUE"):
            GPIO.output(36, GPIO.LOW)
            GPIO.output(38, GPIO.LOW)
            GPIO.output(40, GPIO.HIGH)
        elif str(color).startswith("PURPLE"):
            GPIO.output(36, GPIO.HIGH)
            GPIO.output(38, GPIO.LOW)
            GPIO.output(40, GPIO.HIGH)
        elif str(color).startswith("CYAN"):
            GPIO.output(36, GPIO.LOW)
            GPIO.output(38, GPIO.HIGH)
            GPIO.output(40, GPIO.HIGH)
        elif str(color).startswith("WHITE"):
            GPIO.output(36, GPIO.HIGH)
            GPIO.output(38, GPIO.HIGH)
            GPIO.output(40, GPIO.HIGH)
        elif str(color).startswith("BLACK"):
            GPIO.output(36, GPIO.LOW)
            GPIO.output(38, GPIO.LOW)
            GPIO.output(40, GPIO.LOW)
        else:
            GPIO.output(36, GPIO.LOW)
            GPIO.output(38, GPIO.LOW)
            GPIO.output(40, GPIO.LOW)

            print(f"Error, unknown color: {str(color)}")

    def display(self):

        while True:
            
            plt.close()

            x = np.array([i for i in range(len(self.buffer))])
            y = np.array(self.buffer)

            #print(str(x))
            #print(str(y))

            plt.stem(x, y, use_line_collection = True, bottom= 0.0)
            

            plt.draw()
            plt.pause(1)
            time.sleep(1)
            plt.figure().clear()


    def startViewer(self):
        '''
        Simple method to start the different threads
        '''
        
        self.rabbitThread = Thread(target=self.linkRabbit, daemon=True)
        self.rabbitThread.start()

        self.displayThread = Thread(target=self.display, daemon=True)
        self.displayThread.start()


if __name__ == "__main__":

    print("Starting Sensor Viewer")
    viewer = LiveView(10)
    viewer.startViewer()

    print("Press Ctrl + C to exit")

    while True:
        try:
            input("")
        except KeyboardInterrupt:
            print("\nShutting Down")
            viewer.ledAlert("BLACK")
            GPIO.cleanup()
            sys.exit(0)
            break