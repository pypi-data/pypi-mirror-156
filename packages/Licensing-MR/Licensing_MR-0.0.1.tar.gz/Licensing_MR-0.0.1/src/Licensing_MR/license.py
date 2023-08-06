import requests
import subprocess
import os
from auth import *

with open ("AW_setup.txt", "r") as AW:
    for line in AW:
        if line:
            AWCODE = line.strip()
            
#print("[AWCODE] ", AWCODE)

mainboard_UUID = subprocess.Popen("WMIC csproduct GET UUID /Value", shell=True, stdout=subprocess.PIPE).stdout.read()
mainboard_UUID = mainboard_UUID.decode("Utf-8").strip().split("=")[1]
print(mainboard_UUID)

mainboard_serial = subprocess.Popen("wmic baseboard get serialnumber", shell=True, stdout=subprocess.PIPE).stdout.read()
mainboard_serial = (mainboard_serial.split()[1].decode("Utf-8"))
print(mainboard_serial)

license_server = "http://key-mrsoft.netlify.app/License.txt"
user_keys = []
valid_keys = []
keytype = None

if os.path.exists("license.txt"):
    pass
else:
    f = open ("license.txt", "w+")
    f.close()

def license():
    global keytype, valid_keys
    keys = requests.get(license_server).text
    
    with open ("license.txt", "r+") as license_from_user:
        for line in license_from_user:
            if line:
                user_keys.append(line.strip() +":"+ mainboard_serial +":"+ mainboard_UUID)
        #print("User_Keys:" , user_keys)
                
        for line in user_keys:
            #print("User_key:  ", line)
            line = line.strip()
            for key in keys.splitlines():
                #print("Online_key:", key)
                if key == line:
                    Anwendung = line.split(":")[0].strip()	
                    #print("[AW] ", Anwendung)
                    if (Anwendung == AWCODE):
                        KEY_TYPE = line.split(":")[1]
                        #print(KEY_TYPE)
                        if KEY_TYPE == '1':
                            keytype = "Full_access"
                        if KEY_TYPE == '2':
                            keytype = "Limited_access"
                        if KEY_TYPE == '3':
                            addon = line.split(":")[2]
                            keytype = "Addon:" + addon
                        #print("Key Match - Type: " + str(keytype))
                        valid_keys.append(keytype)
                    
try:                    
    license()
except:
    valid_keys.append("Restricted_access")
    
run(valid_keys)
