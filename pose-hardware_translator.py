import serial
import socket
import threading
import queue
import numpy as np
from serial.tools import list_ports
import math
import time

def calculateA(theta):
    theta1 = -theta[0]
    theta2 = -theta[1]

    


    x1 = 0.5
    y1 = 0.9
    z1 = 0.70

    A_1 = np.array([[x1 * np.cos(theta2) + z1 * np.sin(theta2)],
                    [x1 * np.sin(theta1) * np.sin(theta2) + y1 * np.cos(theta1) - z1 * np.sin(theta1)*np.cos(theta2) - 0.55 * np.sin(theta1)],
                    [-x1 * np.cos(theta1) * np.sin(theta2) + y1 * np.sin(theta1) + z1 * np.cos(theta1)*np.cos(theta2) + 0.55 * np.cos(theta1)],
                    [1]
                    ])
    A_2 = np.array([[x1 * np.cos(theta2) + z1 * np.sin(theta2)],
                    [x1 * np.sin(theta1) * np.sin(theta2) - y1 * np.cos(theta1) - z1 * np.sin(theta1)*np.cos(theta2) - 0.55 * np.sin(theta1)],
                    [-x1 * np.cos(theta1) * np.sin(theta2) - y1 * np.sin(theta1) + z1 * np.cos(theta1)*np.cos(theta2) + 0.55 * np.cos(theta1)],
                    [1]
                    ])
    
    #print("A1 = ", A_1)
    #print("A2 = ", A_2)

    return A_1, A_2


def calculateL(theta):

    gx1 = 0.7
    gx2 = 0.7
    gy1 = 0.91
    gy2 = -0.91
    gz1 = -0.6
    gz2 = -0.6

    G_1 = np.array([[gx1], [gy1], [gz1], [1]])
    G_2 = np.array([[gx2], [gy2], [gz2], [1]])

    A_1, A_2 = calculateA(theta)

    

    L1 = np.linalg.norm(G_1 - A_1)
    L2 = np.linalg.norm(G_2 - A_2)

    
    return L1, L2


def CMD(theta, curl):
    L1, L2 = calculateL(theta)
    L1_0 = 1.861
    L2_0 = 1.861
    dL1 = L1_0 - L1
    dL2 = L2_0 - L2

    

    dPhi1 = (dL1/0.40) * (180/math.pi)
    dPhi2 = 180 - ((dL2/0.40) * (180/math.pi))

    curlCMD = (curl + (- theta[1])) * 180/math.pi

    #print("dPhi1 = ", dPhi1)
    #print("dPhi2 = ", dPhi2)

    cmd = (str) (dPhi1) + " " + (str) (dPhi2) + " " + (str) (curlCMD)

    print(cmd)
    
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


    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0, write_timeout = 0)

    last_message = None

    while True:
        message = None
        with message_lock:
            message = current_message
        
        if message is None or message == last_message:
            time.sleep(0.001)
            continue

        last_message = message

        data = message.split()

        theta = ((float)(data[0]), (float)(data[1]))
        curl = (float)(data[2])
        cmd = CMD(theta, curl)
            

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
        buffer = ""
        while True:
            try:
                buffer += conn.recv(1024).decode()
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    with message_lock:
                        current_message = line

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

