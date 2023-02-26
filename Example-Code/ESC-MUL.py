# Multi ESC Calibration for Drones
import os    
import time   
os.system ("sudo pigpiod") 
time.sleep(1) 
import pigpio 

ESC = 17  
ESC_2 = 18
ESC_3 = 27
ESC_4 = 22

Count_ESC = [ESC , ESC_2, ESC_3, ESC_4]
 

pi = pigpio.pi();

for E in Count_ESC:
    pi.set_servo_pulsewidth(E, 0) 

max_value = 2000 
min_value = 790  

    print("please disconnect battery.. then press kal")
                
def calibrate():   
    for E in Count_ESC: 
        pi.set_servo_pulsewidth(E, 0)
        time.sleep(1)
        pi.set_servo_pulsewidth(E, max_value)
    print("Connect battery.. then press Enter")
    inp = raw_input()
    if inp == '': 
        for E in Count_ESC:
            pi.set_servo_pulsewidth(E, min_value)   
        time.sleep(7)
        time.sleep (5)        
        for E in Count_ESC:
            pi.set_servo_pulsewidth(E, 0)           
        time.sleep(2) 
        print "Arming.."
        for E in Count_ESC:
            pi.set_servo_pulsewidth(E, min_value)
        time.sleep(1)
        control()
                   
             
def control(): 

    time.sleep(1)
    speed = min_value
    print "a : decrease speed & d : increase speed | q : decrease a lot & e : increase a lot"
    while True:
        for E in Count_ESC:
            pi.set_servo_pulsewidth(E, speed)
        inp = raw_input()
        
        if inp == "q":
            speed -= 100    
            print "speed = %d" % speed
        elif inp == "e":    
            speed += 100    
            print "speed = %d" % speed
        elif inp == "d":
            speed += 10     
            print "speed = %d" % speed
        elif inp == "a":
            speed -= 10     
            print "speed = %d" % speed
        elif inp == "stop":
            stop()          
            break
        else:
            print "Press a,q,d or e"
      
def stop(): 
    for E in Count_ESC:
        pi.set_servo_pulsewidth(E, 0)
    pi.stop()

  
inp = raw_input()

if inp == "kal":
    calibrate()

elif inp == "stop":
    stop()
