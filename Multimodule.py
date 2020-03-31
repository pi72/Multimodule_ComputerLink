# * Author:      Peiman Moradi
# * Created:     02th Feb 2019
# * Revised:     28th Mar 2020
# * Description: This code is to control a small drone by a computer
#                through a Multimodule. 
# * User advice: When setting your input channels (ail, elev, ...) be careful for direction.
#                Set the correction factor (cf) for your model and multiply the inputs by the 
#                cf if needed.             
# * References: 
#                1. https://github.com/opentx/opentx/blob/ea1133527313383b84f0ad3e58cb3f0f5463bca6/radio/src/pulses/multi.cpp
#                2. https://github.com/pascallanger/DIY-Multiprotocol-TX-Module
# 
# * License: GNU GENERAL PUBLIC LICENSE http://www.gnu.org/licenses/gpl-2.0.html
# *


# ------------- #
# -- Imports -- #
# ------------- #
import os, sys, inspect, thread, time, serial

# ---------- #
# -- Init -- #
# ---------- #
ser = serial.Serial("/dev/tty.usbserial-A8009e2a",100000,parity=serial.PARITY_EVEN,stopbits=serial.STOPBITS_TWO)

# ------------------ #
# -- Drone params -- #
# ------------------ #
model = 2         # drone model
submodel = 0      # drone sub-model

# -------------------------------- #
# -- Multi-module bind settings -- #
# -------------------------------- #
protoByte = 0     
Multi_Send_Bind = 1<<7 
protoByte |=Multi_Send_Bind 
protoByte |= (model & 0x1f)

subtypeByte = 0x07|(submodel&0x07)<<4 
headerByte  = 0x55

# setupFrame= ['M','P',0x80 (Module Config),1, 0x07 (0x01|0x02|0x04)]
# setupFrame= [0x4D,0x50,0x80,1,0x07]

bindFrame = [headerByte, protoByte, subtypeByte,0x00]

# ---------------------- #
# -- General settings -- #
# ---------------------- #
sensetivity =1.2 # Multiply by the input. Controllable range ~ 1-2

if model==2: # Setup coordinate correction factor for different vehicles
    cf = 1
elif model==18:
    cf = -1
else:
    cf = 1

# ------------------- #
# -- Control Input -- #
# ------------------- #
def controlInput():
    bits=0
    bitsavailable=0
    MULTI_CHAN_BITS=11
    channelBytes = []
    
    # Reference 1:
    # byte 4-25, channels 0..2047
    # ** Multi uses [204;1843] as [-100%;100%]    
    ail=1024
    elev=1023
    thr=204
    rud=1023

    channels = [ail,elev,thr,rud] + 2*[1023] # Setting up 6 channels (you may need to set more channels). More chans = slower serial comms and lag! 
    channels[5] = 1800
        
    for value in channels:
        bits |= value << bitsavailable
        bitsavailable += MULTI_CHAN_BITS
        while (bitsavailable >= 8):
            channelBytes.append( bits & 0xff )
            bits >>= 8
            bitsavailable -= 8

    return channelBytes

# ---------------------------------------- #
# -- Main function where actions happen -- #
# ---------------------------------------- #
def main():
    while(True):    
        # To be able to bind you have to send both bindFrame and controlInput
        ser.write([chr(x) for x in bindFrame])
        ser.write([chr(x) for x in controlInput()])
     
        time.sleep(0.0005)

if __name__=="__main__":
    main()
