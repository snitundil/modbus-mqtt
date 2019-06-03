# modbus_mqtt
## Python implementation of Modbus TCP + MQTT. Data can be written to/read from multiple MODBUS slave devices from a remote MQTT client. <br /><br />

This code includes a **reg_config** option which allows the end user to select the registers to be used while writing and reading data. <br />
This code also includes a **slave_config** option which allows the end user to assign slave IDs to existing devices or add new devices with their own slave ID. <br />
**Data read/write** to these slaves can be done from a remote MQTT client connected to an [online MQTT server](https://test.mosquitto.org/).<br />
*Hence this implementation allows for the use of multiple MODBUS TCP slaves whose slave IDs can be changed or new slaves added and register number to be used for each slave can also be configured by the user. Data read/write can be done from a remote client. Usage is as explained below.* <br /><br />

The implementation consists of 3 inter-dependent programs : <br /><br />

1) modbus_server.py - The pymodbus Modbus TCP server which reads/writes modbus data from slaves. <br /><br />

2) modbus-mqtt_client.py - This is a pymodbus Modbus TCP client and a paho-mqtt MQTT client which receives requests (read/write) from remote MQTT client from the MQTT broker and sends requests (read/write) to the modbus server. If it is a read function, it sends the read data back to remote client through the MQTT broker. <br /><br />

3) mqtt_remote_client.py - This is the user end from where requests are sent to read/write slave data into respective topics n MQTT broker and this is received by modbus-mqtt_client which is subscribed to the those topics. <br /><br />

Applications : <br /><br />
The code is a general implementation of Modbus TCP and MQTT which can be modified and used for various IoT applications.<br />
An example would bean energy monitoring system for a home or office. To do this, one could run modbus_server.py and modbus-mqtt_client.py on a Raspberry Pi connected to one or more slave Modbus sensors. The data of the sensors can be accesed remotely by running mqtt_remote_client.py (with slight changes to read data at regular time intervals) on a remote personal computer and an [IoT Dashboard](https://thingsboard.io/) can be used to visualise the data. <br />
Various applications like this can be implemented with slight adjustments to the code. 
