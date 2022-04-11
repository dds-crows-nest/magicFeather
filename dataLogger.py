import gc
import os # needed for file stuff
import time # needed for sleep
from threading import Thread # needed for threads
import sys # needed to exit

import numpy as np # needed for graph
import collections
from obspy import UTCDateTime # needed for deque

import pika # needed for rabbitMQ

class DataLogger:

    def __init__(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='alert', exchange_type='fanout')

        self.buffer = collections.deque()
        self.readTime = UTCDateTime()
        self.pastRead = 0.0
        self.status = ""
        self.average = 0.0
        
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

        #update buffer by appending to right
        self.buffer.append(data)

        #print(UTCDateTime() - self.readTime)
        self.readTime = UTCDateTime()

        self.average = (abs(data) + self.pastRead) / 2.0
        self.pastRead = abs(data)

        #print(str(self.average))

        if self.average < 0.2:
            status = 'normal'
        elif self.average < 1:
            status = 'warning'
        else:
            status = 'danger'

        self.channel.basic_publish(exchange='alert', routing_key='', body=status)

    def startLogger(self):
        '''
        Simple method to start the different threads
        '''
        
        self.rabbitThread = Thread(target=self.linkRabbit, daemon=True)
        self.rabbitThread.start()


if __name__ == "__main__":

    print("Starting Data")
    dataLogger = DataLogger()

    dataLogger.startLogger()

    print("Press Ctrl + C to exit")

    while True:
        try:
            input("")
        except KeyboardInterrupt:
            print("\nShutting Down")
            sys.exit(0)
            break