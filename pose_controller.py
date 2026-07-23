##CAN ONLY BE RUN IN A BLENDER INTERFACE
## All lines of code containing one # need to be uncommented
## keep all lines that have two ##
## comment out any lines that say comment out next to them
## All comments are here to ensure that code for sockets and threading compiles inside of an external editor

#import bpy
import socket
import threading


HOST = "127.0.0.1"
PORT = 8765

pos_loc = threading.Lock()
current_location = None

def client_process():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    while True:
        global current_location
        location = None
        with pos_loc:
            if current_location != None:
                location = current_location
        

        message = location.encode('utf-8')
        client.send(message)
        
    client.close()

def blender_processes():
    #cube = bpy.data.objects["Cube"]
    global current_location
    with pos_loc:
# Add as many updates as objects being tracked        
#       current_location = (cube.location.x,
#                           cube.location.y,
#                           cube.location.z)
        pass
    return 0.1

##set daemon = True and remove .join() when running in a blender file

#bpy.app.timers.register(blender_processes)
client_thread = threading.Thread(target=client_process, daemon=True)
client_thread.start()


blender_processes() #comment out
client_thread.join() #comment out

