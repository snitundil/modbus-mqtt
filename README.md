# modbus-mqtt
Python implementation of Modbus TCP + MQTT. Data can be written to/read from multiple MODBUS slave devices from a remote MQTT client. <br />
This code includes a reg_config option which allows the end user to select the registers to be used while writing and reading data. <br />
This code also includes a slave_config option which allows the end user to assign slave IDs to existing devices or add new devices with their own slave ID. <br />
Hence this implementation allows for the use of multiple MODBUS TCP slaves whose slave IDs can be changed or new slaves added and register number to be used  for each slave can also be configured by the user. <br />
Data can be read/written to these slaves from a remote MQTT client connected to iot.eclipse.org/test.mosquitto.org MQTT server. <br /><br />
The implementation consists of 3 inter-dependent programs : <br />
modbus_server.py - The pymodbus Modbus TCP server which reads/writes modbus data from slaves. <br />
modbus-mqtt_client.py - This is a pymodbus Modbus TCP client and a paho-mqtt MQTT client which receives requests (read/write) from remote MQTT client from the MQTT broker and sends requests (read/write) to the modbus server. If it is a read function, it sends the read data back to remote client through the MQTT broker. <br />
mqtt_remote_client.py - This is the user end from where requests are sent to read/write slave data into respective topics n MQTT broker and this is received by modbus-mqtt_client which is subscribed to the those topics. <br />
