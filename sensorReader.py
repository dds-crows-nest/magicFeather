import os # needed for file stuff
import time # needed for sleep
import smbus # needed to read I2C
import sys # needed to exit

import pika # needed for rabbitMQ

class SensorReader:
    """
    Class to handle reading the pressure senor and transmitting via RabbitMQ
    """

    def __init__(self):

        self.sensor = smbus.SMBus(1)
        self.addr = 0x28 # TODO: change this to something from a config file

        self.sampleDelay = 0.025

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='sensorRead', exchange_type='fanout')

    def readDLVRF50D1NDCNI3F(self):
	#this function specifically reads data over i2c from a 
	#DLVRF50D1NDCNI3F Amphenol mems differential pressure sensor 
	
	# this routine will need to be changed for a diffent input device
	#such as a voltage via an a/d convertor
	# note: the return value 'pressure' is a floting point number
	
        raw_data = bytearray
        z=bytearray
        raw_pressure= int
        raw_data=[]

        z = [0,0,0,0]
        z = self.sensor.read_i2c_block_data(self.addr, 0, 4) #offset 0, 4 bytes

        d_masked = (z[0] & 0x3F)
        raw_data = (d_masked<<8) +  z[1]    

        raw_pressure= int(raw_data)
        pressure = (((raw_pressure-8192.0)/16384.0)*250.0 *1.25)
        
        return pressure



if __name__ == "__main__":

    print("Starting DLVRF50D1NDCNI3F sensor reader")
    sensorReader = SensorReader()
    print("starting to write data")

    try:
        while True:

            data = sensorReader.readDLVRF50D1NDCNI3F()
            #print(str(data))
            #time.sleep(1)
            sensorReader.channel.basic_publish(exchange='sensorRead', routing_key='', body=str(data))

        
    except KeyboardInterrupt:
        print("Shutting down")
        sys.exit(0)