import sys # needed to exit

import matplotlib.pyplot as plt # needed for graphs
import numpy as np # needed for graph
import collections # needed for deque
import pika # needed for rabbitMQ

import time # needed for sleep
from threading import Thread # needed for threads

import warnings # needed for filtering
warnings.filterwarnings( "ignore") # filter user warning

class LiveView:
    '''
    Simple Python class to visualize sensor data
    '''

    def __init__(self, bufferSize):

        # Ring Buffer setup
        self.buffer = collections.deque(np.full(int(bufferSize), 0.0))
        #print(str(self.buffer))
        

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


    def display(self):

        plt.ion() # turn on interactive mode

        x = np.array([i for i in range(len(self.buffer))])
        y = np.array(self.buffer)
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.autoscale_view()
        line1, = ax.plot(x, y, 'b-')

        while True:
            
            line1.set_ydata(self.buffer)
            
            ax.autoscale_view()
            ax.relim()

            fig.canvas.draw()
            fig.canvas.flush_events()


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
    viewer = LiveView(10000)
    viewer.startViewer()

    print("Press Ctrl + C to exit")

    while True:
        try:
            input("")
        except KeyboardInterrupt:
            print("\nShutting Down")
            sys.exit(0)
            break