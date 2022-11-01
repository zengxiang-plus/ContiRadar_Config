#!/usr/bin/env python
import time
import can
import threading
import sys
import os

msgConfigLeftConti = can.Message(
    arbitration_id = 0x200, data = [0xBB, 0x1F, 0x40, 0xFF, 0x08, 0x80, 0x01, 0xFF], is_extended_id = False
)
msgConfigLeftFliter = can.Message(
    arbitration_id = 0x202, data = [0xC6, 0x00, 0x06, 0x00, 0x07, 0xFF, 0xFF, 0xFF], is_extended_id = False
)
msgReadLeftFliter = can.Message(
    arbitration_id = 0x202, data = [0xC4, 0x00, 0x06, 0x00, 0x07, 0xFF, 0xFF, 0xFF], is_extended_id = False
)

msgExpectContiCfgRes = can.Message(
    arbitration_id = 0x201, data = [0xC0, 0x1F, 0x40, 0x00, 0x00, 0xC4, 0x00, 0x00], is_extended_id = False
)
msgExpectHeaderRes = can.Message(
    arbitration_id = 0x203, data = [0x00, 0x08], is_extended_id = False
)
msgExpectContiFliterRes = can.Message(
    arbitration_id = 0x204, data = [0xC4, 0x00, 0x06, 0x00, 0x07], is_extended_id = False
)

msgConfigRightConti = can.Message(
    arbitration_id = 0x210, data = [0xBB, 0x1F, 0x40, 0xFF, 0x08, 0x80, 0x01, 0xFF], is_extended_id = False
)
msgCovertLefttoRight = can.Message(
    arbitration_id = 0x200, data = [0xBB, 0x1F, 0x40, 0xFF, 0x09, 0x80, 0x01, 0xFF], is_extended_id = False
)



def canRecv(can0, sensor_type):
    startTime  = time.time()
    flowState = 0
    count = 0
    while(1):
        currentTime = time.time()
        msg = can0.recv(0.1)
        time.sleep(0.1)
        if flowState == 0:
            if msg.arbitration_id & 0x0F0F == msg.arbitration_id:
                flowState = 1
                print("SUCCESS STEP 1: Change Mode to Left Conti Radar Mode!")
        if flowState == 1:
            count = 0
            if msg.arbitration_id == msgExpectContiCfgRes.arbitration_id:
                if msg.data == msgExpectContiCfgRes.data:
                    print("SUCCESS STEP 2: Config Conti Radar General Configureation!")
                    flowState = 2
                else:
                    count = count +1
            if count > 2:
                print("ERROR STEP 2: Config Conti Radar General Configureation!")
                break
        if flowState == 2:
            count = 0
            if (msg.arbitration_id == msgExpectHeaderRes.arbitration_id):
                if msg.data == msgExpectHeaderRes.data:
                    print("SUCCESS STEP 3: Check Msg Header!")
                    flowState = 3
                else:
                    count = count +1
                if count > 2:
                    print("ERROR STEP 3: Check Msg Header!")
                    break
        if flowState == 3:
            count = 0
            if (msg.arbitration_id == msgExpectContiFliterRes.arbitration_id):
                if msg.data == msgExpectContiFliterRes.data:
                    print("SUCCESS STEP 4: Config Conti Radar Fliter Configureation!")
                    flowState = 4
                else:
                    count = count +1
            if count > 2:
                    print("ERROR STEP 4: Config Conti Radar Fliter Configureation!")
                    break
        if flowState == 4:
            count = 0
            if (msg.arbitration_id == msgExpectContiFliterRes.arbitration_id):
                if msg.data == msgExpectContiFliterRes.data:
                    print("SUCCESS STEP 5: Check Conti Radar Fliter Configureation!")
                    flowState = 5
                else:
                    count = count +1
            if count > 2:
                    print("ERROR STEP 5: Check Conti Radar Fliter Configureation!")
                    break
        if flowState == 5:
            if currentTime - startTime > 20:
                if sensor_type == "rightrear":
                    if msg.arbitration_id & 0x0F0F != msg.arbitration_id:
                        print("SUCCESS STEP 6: Convert Left Config to Right!")
                    else:
                        print("ERROR STEP 6: Convert Left Config to Right!")
                        break
                print("SUCCESS: Conti Radar Config All Steps")
                break





def main():
    sensor_type = sys.argv[1]
    if sensor_type == "rightrear":
        print("INFO: This Flow is Confige Right Rear Conti Radar!")
    else:
        print("INFO: This Flow is Confige Left Rear / Front Conti Radar!")
    can0 = can.interface.Bus(bustype='socketcan_ctypes', channel='can0')

    threadCanRecv = threading.Thread(target = canRecv, args=(can0, sensor_type))
    threadCanRecv.start()
    for i in range(5):
        can0.send(msgConfigRightConti)
        time.sleep(0.5) 
    for i in range(5):
        can0.send(msgConfigLeftConti)
        time.sleep(0.5)
    for i in range(5):
        can0.send(msgConfigLeftFliter)
        time.sleep(0.5)
    for i in range(5):
        can0.send(msgReadLeftFliter)
        time.sleep(0.5)
    if sensor_type == "rightrear":
        for i in range(5):
            can0.send(msgCovertLefttoRight)
            time.sleep(0.5) 

if __name__ == '__main__':
    main()
    



