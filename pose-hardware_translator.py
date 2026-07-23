import serial
import socket
import threading
import queue
import numpy as np
import scipy as sc
from serial.tools import list_ports

def calculateP(theta1,theta2):
    P = np.array([[np.sin(theta2)],
                  [-np.sin(theta1) * np.cos(theta2) - 5.5 * np.sin(theta1)],
                  [np.cos(theta1) * np.cos(theta2) + 5.5 * np.cos(theta1)],
                  [1]
                  ])
    return P


def EndEffectorToCMD(P):
    
    cmd = P
    return cmd


def find_ports():
    for p in list_ports.comports():
        if "CP2102" in p.description:
            return p.device
    return None

##Host and port info for sockets connection
HOST = "127.0.0.1"
PORT = 8765


## Port and Baud rate info for Serial connection

SERIAL_PORT = None 
if SERIAL_PORT == None:
    SERIAL_PORT = find_ports()

if SERIAL_PORT == None:
    raise Exception("Serial Device not found")

BAUD = 115200


serial_queue = queue.Queue()

message_lock = threading.Lock()
current_message = None



def serial_process():
    global current_message
    

    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0)
    while True:
        message = None
        with message_lock:
            if current_message != None:
                message = current_message
        cmd = EndEffectorToCMD(message)
        if cmd == "EXIT":
            break

        ser.write((cmd + "\n").encode("utf-8"))
    ser.close()

def socket_thread() :
    global current_message


    conn = None
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)


    server.settimeout(60)


    print("Server listening...")
    try:
        conn, addr = server.accept()
        print("Connected:", addr)

    except socket.timeout:
        print("No client connected in time")
    if conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                message = data.decode("utf-8")

                with message_lock:
                    current_message = message

            except ConnectionResetError:
                print("Client disconnected abruptly")
                break
            except OSError as e:
                print("Socket error: ", e)
                break

        conn.close()




if SERIAL_PORT:
    print("starting serial process")
    serial_thread = threading.Thread(target=serial_process, daemon=False)
    serial_thread.start()

server_thread = threading.Thread(target=socket_thread, daemon=False)
server_thread.start()


serial_thread.join()
server_thread.join()

