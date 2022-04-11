import sys # needed to exit

import pika # needed for rabbitMQ

import time # needed for sleep
from threading import Thread # needed for threads

import RPi.GPIO as GPIO # needed to use GPIO

class AlertLED:

    def __init__(self):
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
        channel.exchange_declare(exchange='alert', exchange_type='fanout')

        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        # channel.queue_bind(exchange='freqSweep', queue=queue_name)
        channel.queue_bind(exchange='alert', queue=queue_name)
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

        status = body.decode('UTF-8')

        if status == "normal":
            self.ledAlert("BLUE")
        elif status == "warning":
            self.ledAlert("YELLOW")
        elif status == "danger":
            self.ledAlert("RED")
        elif status == "timeout":
            self.ledAlert("PURPLE")
        elif status == "usb":
            self.ledAlert("WHITE")
        else:
            print(f"Error, unknown status: {str(status)}")
        

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

    def startLED(self):

        self.rabbitThread = Thread(target=self.linkRabbit, daemon=True)
        self.rabbitThread.start()

if __name__ == "__main__":

    print("Starting Alert LED")
    alertLED = AlertLED()
    alertLED.startLED()

    print("Press Ctrl + C to exit")

    while True:
        try:
            input("")
        except KeyboardInterrupt:
            print("\nShutting Down")
            alertLED.ledAlert("BLACK")
            GPIO.cleanup()
            sys.exit(0)
            break