from ODriveCAN import ODriveCAN

# Initialize ODriveCAN for 1st Motor 
odrive1 = ODriveCAN(0) #Set Node ID = 0
odrive1.initCanBus()

#Initialize ODriveCAN for 2nd Motor 
odrive2 = ODriveCAN(1) #Set Node ID = 1
odrive2.initCanBus()


def set_motors_vel(target_vel):
    #Set Odrive1 to target_vel
    odrive1.set_velocity(target_vel)

    #Convert target_vel from Turns/second to degrees/second
    motor1_vel_deg_per_sec = target_vel * 360

    #Vel 1st motor - 0.5 deg/s 
    motor2_vel_deg_per_sec = motor1_vel_deg_per_sec - 0.5

    #Convert Motor 2 Vel Deg/Sec back to Turn/Sec
    motor2_target_vel_turns_per_sec = motor2_vel_deg_per_sec / 360 

    #Set Odrive 2 to calulated Motor2 Target Velocity
    odrive2.set_velocity(motor2_target_vel_turns_per_sec)

    #Print Motor 1 & 2 set velocity
    print(f"Set Motor 1 to {target_vel} turn/s, Motor 2 to {motor2_target_vel_turns_per_sec} turns/s")

try:
    while True:
        #User Input target velocity
        user_target_velocity = input("Enter your target velocity (0-20 turns/second):")

        #Function that sets both motors velocity
        set_motors_vel(float(user_target_velocity))
except KeyboardInterrupt:
    #When program is ended set ODrive 1 & 2 Velocity to 0
    odrive1.set_velocity(0)
    odrive2.set_velocity(0)
    print("Program interrupted by user. Exiting.")