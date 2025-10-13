import numpy as np
import epics
import socket
import time

#Set all global variables
global IP_ADDR
global PORT_NUMBER1
global PORT_NUMBER2
global MOXA_IP 
global MOX_PORT
IP_ADDR = "10.97.106.119"
PORT_NUMBER1 = 8080
PORT_NUMBER2 = 8081

#Creating initial socket connection
NT230_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    NT230_socket.connect((IP_ADDR, PORT_NUMBER1))
    print('Connection Successful')
    print(f"Client socket is {NT230_socket}")
except socket.error as e:
    print(f"Initial socket connection failed: {e}. Try different port")
    NT230_socket = None

#Next defining a simple function that sends commands to the Laser

def send_message(message):
    global NT230_socket
    NT230_socket.settimeout(3)
    if NT230_socket is None:
        try:
            print("Trying to connect again.")
            NT230_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            NT230_socket.connect((IP_ADDR, PORT_NUMBER1))
            print("Connection successful")
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
    #Now trying to send a message in a loop. If timeouts will try again
    while True:
        try:
            NT230_socket.send(message.encode())
            print(f"Message {message} has been sent")
            time.sleep(0.1)
            response = NT230_socket.recv(2048)
            if response:
                print(f"Machine response: {response}")
                return response
                break
            
        except socket.timeout:
            print("Socket timed out, retrying again in 5 seconds")
            time.sleep(5)
        except Exception as e:
            print(f"Program crashed due to the error: {e}")
            break

message1 = "/?RDVAR/State\r\n\x03" #Using the end line from the manual
message2 = "*IDN?\r\n\x03"

response = send_message(message2)

print(f"The response is {response}")



