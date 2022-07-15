import random
import sys
import time
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)
## -----------------------------------------------------------------------------

#Arm thresholds (L , R):
#go to pickup (1,0)
#grip (1,1)
#go to dropoff (1,0)
#open/close drawer (0,1)
#ungrip (0,0)

#Function takes in container_id number and returns the location of the dropoff
def locate_bins(number): 
    if number == 1:
        location = [-0.5796, 0.2313, 0.3151] #Red small
        return location
    elif number == 2:
        location = [0.0, -0.6379, 0.3103] #Green small
        return location
    elif number == 3:
        location = [0.0, 0.6339, 0.3123] #Blue small
        return location
    elif number == 4:
        location = [-0.3191, 0.1263, 0.2961] #Red big
        return location
    elif number == 5:
        location = [0.0, -0.3555, 0.2549] #Green big
        return location    
    elif number == 6:
        location = [0.0, 0.3555, 0.2549] #Blue big
        return location

#function takes in a true/false grip statement and depending on if
#It is true or false it will open/close the grippers
def control_gripper(grip):
    while grip == False: #Not gripping anything
        reading_L = arm.emg_left()
        reading_R = arm.emg_right()
        if reading_L == 1 and reading_R == 1:
            arm.control_gripper(45)
            time.sleep(2)
            return True
    while grip == True: #Currently gripping a container
        reading_L = arm.emg_left()
        reading_R = arm.emg_right()
        if reading_L == 0 and reading_R == 0:
            arm.control_gripper(-45)
            time.sleep(2)
            return False

#Function takes in ID and 'initial' corresponds to the 1st and 2nd positions of
#the arm, the arm will move accordingly and return false if its at its
#second position,it will return true if it completed the cycle
def move_end_effector(ID, initial):
    while initial == True: #If object is at its initial position
        reading_L = arm.emg_left()
        reading_R = arm.emg_right()
        if reading_L == 1.0 and reading_R == 0.0:
            arm.move_arm(0.4498, 0.0, 0.0068) #container spawn coordinates
            grip_status = False #initializes control_gripper() function
            time.sleep(2)
            control_gripper(grip_status) #grip container
            arm.move_arm(0.4064, 0.0, 0.4826)
            time.sleep(2)
            return False
    while initial == False: #If object is not at its initial posiiton
        reading_L = arm.emg_left()
        reading_R = arm.emg_right()
        if reading_L == 1.0 and reading_R == 0.0:
            target = locate_bins(ID)
            arm.move_arm(target[0], target[1], target[2])
            return True
        
#function takes in container id, and the status of the door (true/false),
#and will open/close door accordingly (large only)
def open_close_autoclave(containerID, door_status):
    while door_status == False: #while door is closed 
        reading_L = arm.emg_left()
        reading_R = arm.emg_right()
        if reading_L == 0 and reading_R == 1:
            if containerID == 4: #red
                arm.open_red_autoclave(1)
                return True #return True for next cycle (to close door)
            elif containerID == 5: #Green
                arm.open_green_autoclave(1)
                return True
            elif containerID == 6: #Blue
                arm.open_blue_autoclave(1)
                return True
    while door_status == True: #while door is open
        reading_L = arm.emg_left()
        reading_R = arm.emg_right()
        if reading_L == 0 and reading_R == 1:
            reading_L = arm.emg_left()
            reading_R = arm.emg_right()
            if containerID == 4:
                arm.open_red_autoclave(2)
                return False
            elif containerID == 5:
                arm.open_green_autoclave(2)
                return False
            elif containerID == 6:
                arm.open_blue_autoclave(2)
                return False
        
container_in_bin = [] #List to keep track of whats been put into bin
counter = 0 #How many times loop has been run

while counter != 6: #ends program if process has been run 6 times
    container_ID = random.randint(1,6) #randomly spawn one of the containers
    while True:
        if container_ID in container_in_bin: #Checks if container is already in bin
            container_ID = random.randint(1,6)
        else: #if not in bin continue with original loop
            break
    time.sleep(2)
    arm.spawn_cage(container_ID)
    while True:
        reading_L = arm.emg_left() 
        reading_R = arm.emg_right()
        if container_ID >= 4:
            door_status = False #door is closed
            initial = True #at first movement step
            time.sleep(2)
            initial = move_end_effector(container_ID, initial) #move to pickup and grip
            move_end_effector(container_ID, initial) #move to dropoff
            door_status = open_close_autoclave(container_ID, door_status) #open door
            grip_status = True #gripper is holding something, therfore: "True"
            control_gripper(grip_status) #ungrip container
            open_close_autoclave(container_ID, door_status) #close door
            arm.home()                  
            container_in_bin.append(container_ID) #Keeps track finished containers
            counter += 1
            break
        else:
            initial = True
            initial = move_end_effector(container_ID, initial) #move to pickup and grip
            move_end_effector(container_ID, initial) #move to dropoff
            grip_status = True
            control_gripper(grip_status) #ungrip container
            arm.home()
            container_in_bin.append(container_ID) #add to list
            counter += 1
            break

