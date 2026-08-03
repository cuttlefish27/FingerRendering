##CAN ONLY BE RUN IN A BLENDER INTERFACE

import bpy
import socket
import threading
import math


HOST = "127.0.0.1"
PORT = 8765

pos_loc = threading.Lock()

#Semaphore to wake the client thread when new data is available
work_available = threading.Semaphore(0)

theta = None
curl = None

program_running = True

def client_process():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    while True:
        work_available.acquire() 
          # wait here until new data is available
        if(not program_running):
            message = "EXIT\n"
            break
        global theta
        global curl
        with pos_loc:
            if (theta != None) and (curl != None):
                currTheta = f"{theta[0]} {theta[1]} {curl}\n"
                message = currTheta.encode('utf-8')
                client.send(message)
        
    client.close()

def blender_processes():

    localTheta = None
    localCurl = None

    armature = bpy.data.objects["Armature"]
    curlControl = bpy.data.objects["Empty.001"]
    
    depsgraph = bpy.context.evaluated_depsgraph_get()
    arm_eval = armature.evaluated_get(depsgraph)

    bone1 = arm_eval.pose.bones["Bone"]
    bone2 = arm_eval.pose.bones["Bone.001"]
    
    R1 = bone1.matrix.to_3x3()
    R2 = bone2.matrix.to_3x3()
    
    R_rel = R1.inverted() @ R2
    
    euler1 = R1.to_euler('XYZ')
    euler2 = R_rel.to_euler('XYZ')

    theta1 = euler1.x - math.pi/2
    theta2 = euler2.z
    
    curl1 = curlControl.location.z 

    print(theta1)
    print(theta2)
    print(curl1)

    global theta
    global curl

    localTheta = (theta1, theta2)
    localCurl = curl1

    with pos_loc:
        if (localTheta != theta) or (localCurl != curl):
            theta = localTheta
            curl = localCurl
            work_available.release()  # signal the client thread that new data is available

    return 0.02



bpy.app.timers.register(blender_processes)
client_thread = threading.Thread(target=client_process, daemon=True)
client_thread.start()

