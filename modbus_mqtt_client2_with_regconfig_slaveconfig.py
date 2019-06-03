#!/usr/bin/env python
'''
Python implementation of Modbus TCP + MQTT. Data can be read/written from remote MQTT client into MODBUS slave.

This code includes a REGISTER CONFIG option which allows the end user to select the registers to be used while writing and reading data.
reg_config is a topic on the mqtt server and is updated every time it is changed. Existing devices register number can be changed or new devices can be added and data written into that register.

This code also includes a SLAVE CONFIG option which allows the end user to assign slave IDs to devices or add new devices with their own slave ID.
slave_config is a topic on the mqtt server and is updated every time it is changed. Existing devices slave/unit ID can be changed or new devices can be added.

Hence this implementation allows for the use of multiple MODBUS TCP slaves whose slave IDs can be changed or new slaves added and register number to be used 
for each slave can also be configured by the user. Data can be read/written to these slaves from a remote MQTT client connected to iot.eclipse.org MQTT server.
'''

#importing all required methods from pymodbus for estalishing MODBUS TCP connection
import serial
import socket
import traceback
from pymodbus.framer.rtu_framer import ModbusRtuFramer
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Defaults
from pymodbus.utilities import hexlify_packets
from pymodbus.factory import ServerDecoder
from pymodbus.datastore import ModbusServerContext
from pymodbus.device import ModbusControlBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.transaction import *
from pymodbus.exceptions import NotImplementedException, NoSuchSlaveException
from pymodbus.pdu import ModbusExceptions as merror
from pymodbus.compat import socketserver, byte2int
from binascii import b2a_hex
from pymodbus.server.sync import StartTcpServer
from pymodbus.server.sync import ModbusTcpServer 
from pymodbus.server.sync import StartUdpServer
from pymodbus.server.sync import StartSerialServer
import pymodbus.server.sync
from pymodbus.server.sync import ModbusConnectedRequestHandler
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusBinaryFramer
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

import paho.mqtt.client as mqtt #import the client1
import time 					#for time delays

import logging 
import json 					#to convert reg_config and slave_config from received json format

reg_config = {} 				#global variale to store reg_config as it is updated by remote mqtt client1
slave_config = {} 				#global variable to store slave_config as it is updated by remote mqtt client1
device_in_use = '' 				#global variable which stores the name of device currently being accessed by remote mqtt client1


#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# device_in_use variable has the key(name) of the device which is currently being accessed. This is set when data is written when user selects the device.
# This method updates the device_in_use variable when a new device is accessed.
#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
def device_in_use_on_message(client, userdata, message):
	global device_in_use 				#to specifiy that the global variable is being referenced.
	device_in_use = message.payload
	print("Device in use ",device_in_use)

	
#-------------------------------------------------------------------------------------------------------------------------------------------------------------#
# This method is called when data is written into a device. It first finds the device name from device_in_use which was updated in device_in_use_on_message().
# Then it uses reg_config and slave_config and finds corresponding register number and slave ID respectively.
# Finally it writes the data received into that register and slave ID of the MODBUS device by establishing a connection with the MODBUS server.
#-------------------------------------------------------------------------------------------------------------------------------------------------------------#
def data_on_message(client, userdata, message):
	global device_in_use 
	diu1 = device_in_use.decode("utf-8") #to convert from binary array to string
	topic = message.topic
	value = int(message.payload) #Converting the bytearray to integer value.
	print('Data received.')
	print('Value :',value)
	reg = int(reg_config[locals()['diu1']])
	UNIT = int(slave_config[locals()['diu1']])
	print("Register to write into :\n")
	print(reg)
	print("Slave unit to write into :\n")
	print(UNIT)
	mclient = ModbusClient(host = "localhost", port = 502, framer = ModbusRtuFramer) #Initialise the ModbusTcpClient
	mclient.connect()
	rw = mclient.write_register(reg,value,unit=UNIT)
	mclient.close()	

#----------------------------------------------------------------------------------------------------------#
# This method updates reg_config global variable when the reg_config is updated by remote mqtt client1 
# so that data_on_message and read_req_on_message read and write from correct register.
#----------------------------------------------------------------------------------------------------------#
def reg_config_on_message(client, userdata, message):
	print("reg_config received\n")
	global reg_config 							#referring to global variable reg_config. 
	reg_config = json.loads(message.payload) 	#converting from json data
	print(reg_config)
	

#----------------------------------------------------------------------------------------------------------#
# This method updates slave_config global variable when the slave_config is updated by remote mqtt client1 
# so that data_on_message and read_req_on_message read and write from correct slave unit.
#----------------------------------------------------------------------------------------------------------#
def slave_config_on_message(client,userdata,message):
	print("slave_config received")
	global slave_config 						#referring to global variable slave_config. 
	slave_config = json.loads(message.payload)	#converting from json data
	print(slave_config)

#---------------------------------------------------------------------------------------------------------------------------------------------------#
# This method is called when data read request is sent from remote mqtt client1. 
# It finds the register number and slave ID of that device (device name is sent as payload of the request message) from reg_config and slave_config.
# Then it establishes a MODBUS TCP link and reads the value. Read value is published to data_req which is received by remote client.
#---------------------------------------------------------------------------------------------------------------------------------------------------#


#Method to call when requested data is published. Used as a confirmation that data has been published. 
def data_req_on_publish(client, userdata, mid):
	print("Data request published\n")

def req_response_on_connect(client, userdata, flags, rc):
	print("Connection established.")
	
def read_req_on_message(client,userdata,message):
	print("Data read request received")
	diu1 = message.payload.decode("utf-8")
	print("Reading data from ",diu1)
	reg = int(reg_config[locals()['diu1']])
	UNIT = int(slave_config[locals()['diu1']])
	mclient = ModbusClient(host = "localhost", port = 502, framer = ModbusRtuFramer) #Initialise the ModbusTcpClient
	mclient.connect()
	rr = mclient.read_holding_registers(reg,1,unit=UNIT)
	value = rr.registers
	print(value)
	client.publish('data_req',value[0],qos=2) #published to data_req to which user client is subscribed. 
#--------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

broker_address = "test.mosquitto.org"  #Using online mqtt broker

#------------------------------------------------------------------------------------------------------------#
# Creating reg_config instance. This instance subscribes to and hence receives data from topic reg_config.
# Any changes made in reg_config by user and uploaded here and received by this client.
# Once received, reg_config global variable is updated.
#------------------------------------------------------------------------------------------------------------#
print("creating reg_config instance")
client_reg = mqtt.Client("REG")
client_reg.on_message = reg_config_on_message
print("connecting to broker")
client_reg.connect(broker_address)
client_reg.loop_start()
print("Subscribing to reg_config")
client_reg.subscribe('reg_config',qos=2)

#------------------------------------------------------------------------------------------------------------#
# Creating slave_config instance. This instance subscribes to and hence receives data from topic slave_config.
# Any changes made in slave_config by user and uploaded to this topic and received by this client.
# Once received, slave_config global variable is updated.
#------------------------------------------------------------------------------------------------------------#
print("creating slave_config instance")
client_slave = mqtt.Client("SLAVE")
client_slave.on_message = slave_config_on_message
print("connecting to broker")
client_slave.connect(broker_address)
client_slave.loop_start()
print("Subscribing to slave_config")
client_slave.subscribe('slave_config',qos=2)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Creating device is use instance. This instance subscribes to and hence receives data from topic device_in_use.
# Whenever a request is send by the user to read/write from a slave, the name of the slave which has been reqested is updated on this topic and received by this client.
# Once received, device_in_use global variable is updated.
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
print("Creating device_in_use instance")
client_diu = mqtt.Client("DIU")
client_diu.on_message = device_in_use_on_message
print("connecting to broker")
client_diu.connect(broker_address)
client_diu.loop_start()
print("Subscribing to device_in_use")
client_diu.subscribe('device_in_use',qos=2)

#----------------------------------------------------------------------------------------------------------------------------------------------#
# Creating data instance. This instance subscribes and hence receives data from topic data.
# Whenever data to write into a slave is sent by the user, it is updated on this topic and received by this client.
# Once received, it is written into the register specified by reg_config of that slave and slave unit specified by slave_config in function data_on_message.
#----------------------------------------------------------------------------------------------------------------------------------------------#
print("Creating data instance")
client_data = mqtt.Client("DATA")
client_data.on_message = data_on_message
print("connecting to broker")
client_data.connect(broker_address)
client_data.loop_start()
print("Subscribing to data")
client_data.subscribe('data',qos=2)


#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Creating data request instance. This instance subscribes and hence recieves data from topic read_req.
# Wheber data is to be read from a slave, the name of the slave to read data from is updated on this topic and hence received by this client.
# Once received, it is read from register specified by reg_config of that slave and published to be received by user in method read_req_on_message.
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
print("Creating data req instance")
client_data_req = mqtt.Client("DATA_REQ")
client_data_req.on_message = read_req_on_message
client_data_req.on_publish = data_req_on_publish
print("connecting to broker")
client_data_req.connect(broker_address)
client_data_req.loop_start()
print("Subscribing to read req")
client_data_req.subscribe('read_req',qos=2)


time.sleep(100000) #time delay to keep this client online, running and waiting for requests. Can be manually shut down.

#stop loops and disconnect all clients 
client_reg.loop_stop()
client_slave.loop_stop()
client_diu.loop_stop()
client_data.loop_stop()
client_data_req.loop_stop()
client_reg.disconnect()
client_slave.disconnect()
client_diu.disconnect()
client_data.disconnect()
client_data_req.disconnect()
