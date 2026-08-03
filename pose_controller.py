##CAN ONLY BE RUN IN A BLENDER INTERFACE

import bpy
import socket
import threading
import math


HOST = "127.0.0.1"
PORT = 8765

pos_loc = threading.Lock()
theta = None
curl = None

def client_process():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    while True:
        global theta
        global curl
        with pos_loc:
            if theta != None:
                currTheta = f"{theta[0]} {theta[1]} {curl}\n"
        

                message = currTheta.encode('utf-8')
                client.send(message)
        
    client.close()

def blender_processes():
    
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
    with pos_loc:
# Add as many updates as objects being tracked        
       theta = (theta1, theta2)
       curl = curl1
       
    return 0.02



bpy.app.timers.register(blender_processes)
client_thread = threading.Thread(target=client_process, daemon=True)
client_thread.start()

