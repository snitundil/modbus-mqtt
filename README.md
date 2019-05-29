# modbus_mqtt
Python implementation of Modbus TCP + MQTT. Data can be written/read to/from multiple MODBUS slave devices from a remote MQTT client.
This code includes a reg_config option which allows the end user to select the registers to be used while writing and reading data. 
This code also includes a slave_config option which allows the end user to assign slave IDs to existing devices or add new devices with their own slave ID. 
Hence this implementation allows for the use of multiple MODBUS TCP slaves whose slave IDs can be changed or new slaves added and register number to be used  for each slave can also be configured by the user. 
Data can be read/written to these slaves from a remote MQTT client connected to iot.eclipse.org MQTT server.
