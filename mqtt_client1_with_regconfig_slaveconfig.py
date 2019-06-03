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
import paho.mqtt.client as mqtt
import time
import json

#--------------------------------------------------------------------------------------------------------------------------------#
# reg_config dict includes some standard devices register configuration which can be changed or new devices can be added.
#--------------------------------------------------------------------------------------------------------------------------------#
reg_config={"energy_meter": '01',"temp_sensor":'05'}

#------------------------------------------------------------------------------------------------------------#
# slave_config has a list of devices and their slave IDs which can be changed or new devices can be added.
#------------------------------------------------------------------------------------------------------------#
slave_config={"energy_meter":'01',"temp_sensor":'02'}

read_req_value = 0 #to store response of read_req. 

#method to display a message once the user(client1) has connected to mqtt server. Called when connection is succesful.
def on_connect(client, userdata, flags, rc):
	 print("Connected flags"+str(flags)+"result code "\
	 +str(rc)+"client1_id ")
	 client.connected_flag=True

#method to display a message when the data has been published by user client (client1). Called when publish is succesful.
def on_publish(client, userdata, mid):
	print("Data published.")

#method to print the data received from the register after sending a read request.
def data_req_on_message(client,userdata,message):
	print("Data received :\n")
	read_req_value = int(message.payload)
	print("Register value :\n")
	print(read_req_value)
	
broker_address="test.mosquitto.org" #Using online broker

#-------------------------------------------------------------------------------------------------------------------------------------------------------#
# Creating instance client1. This client is the end user which will send requests to read/write data from modbus tcp slaves and can be a remote client. 
# The requests from client1 are sent to the MQTT server. Client2 receives the requsts, reg and slave config from the respective topics on MQTT server. 
# Client2 is both an MQTT client and MODBUS client. It sends the received request to the MODBUS server to cread/write data from the slaves. 
#--------------------------------------------------------------------------------------------------------------------------------------------------------#
print("creating new instance")
client1 = mqtt.Client("P1")
client1.on_publish = on_publish
client1.on_message = data_req_on_message
print("connecting to broker")
client1.connect(broker_address) #connect to broker
client1.loop_start() 			#start the loop

print("Pushing reg_config")
client1.publish('reg_config',json.dumps(reg_config),qos=2) #Pushing initial reg_config
time.sleep(2) 											   #delay to wait till reg_config is pushed before prompting for data input

print("Pushing slave_config")
client1.publish('slave_config',json.dumps(slave_config),qos=2) 	#Pushing initial slave_config
time.sleep(2) 													#delay to wait till slave_config is pushed before prompting for data input

print("Subscribing to data request")
client1.subscribe('data_req',qos=0)  #Subscribing to data request topic where the requested data from register is published by client2. 
time.sleep(2)

cont = 'Y' #loop control variable
while cont == 'Y':
	choice = input('1)data_write\n2)data_read\n3)reg_config\n4)slave_config\n')
	if choice == '3':
		print(reg_config)
		choice = input('1)Change existing\n2)Add new\n3)Exit\n')
		if choice == '1':
			device = input("Enter device\n")
			new_value = input("Enter new register number\n")
			reg_config[locals()['device']] = new_value #Updating reg_config dict. key is given using locals() function which returns all local variables. locals()['device'] will return the string which is stored in variable name 'device'
		elif choice == '2':
			device = input("Enter new device\n")
			value = input("Enter register number\n")
			reg_config[locals()['device']] = value #Updating reg_config dict. key is given using locals() function which returns all local variables. locals()['device'] will return the string which is stored in variable name 'device'
		elif choice ==  '3':
			continue
		else:
			print("Invalid choice\n")
			continue
		print("new reg_config:\n")
		print(reg_config)
		print("Pushing reg_config\n")
		client1.publish('reg_config',json.dumps(reg_config),qos=2)
		time.sleep(3)
	elif choice == '4':
		print(slave_config)
		choice = input('1)Change existing\n2)Add new\n3)Exit\n')
		if choice == '1':
			device = input("Enter device\n")
			new_value = input("Enter new slave ID\n")
			slave_config[locals()['device']] = new_value #Updating slave_config dict. key is given using locals() function which returns all local variables. locals()['device'] will return the string which is stored in variable name 'device'
		elif choice == '2':
			device = input("Enter new device\n")
			value = input("Enter slave ID\n")
			slave_config[locals()['device']] = value	#Updating slave_config dict. key is given using locals() function which returns all local variables. locals()['device'] will return the string which is stored in variable name 'device'
			value = input("Enter register config of new device\n")
			reg_config[locals()['device']] = value
		elif choice == '3':
			continue
		else:
			print("Invalid choice\n")
			continue
		print("new slave_config:\n")
		print(slave_config)
		print("new reg_config:\n")
		print(reg_config)
		print("Pushing slave_config and reg_config\n")
		client1.publish('slave_config',json.dumps(slave_config),qos=2)
		time.sleep(2)
		client1.publish('reg_config',json.dumps(reg_config),qos=2)
		time.sleep(2)
	elif choice == '1':
		device = input("Select device to which data is to be pushed:\n")
		value = int(input("Enter value(in decimal) to put in register :\n"))
		try:
			UNIT = int(slave_config[locals()['device']])  #Checking if entered device has been added as a slave.
		except:
			print("Device does not exist in database. Please add the device to slave_config or select existing device.")
			continue 
		print("Pushing value to device\n",device)
		client1.publish('device_in_use',device,qos=0) #publish the device currently in use. the register number of tht device is taken from reg_config and value is written.
		client1.publish('data',value,qos=0)	#publish value to be put in register
		time.sleep(2)
	elif choice == '2':
		device = input("Select device from which data is to be read:\n")
		try:
			UNIT = int(slave_config[locals()['device']])  #Checking if entered device has been added as a slave.
		except:
			print("Device does not exist in database. Please add device to slave_config or select existing device.")
			continue
		client1.publish('read_req',device,qos=0)
		time.sleep(5)
	else:
		print("Invalid choice")
	cont = input("Continue? [Y/N]\n")
time.sleep(4)
client1.loop_stop()