import tkinter as tk
from main import setup

#----------------------------- Licensing ---------------------------------------------
Full_access = 0
Limited_access = 0
Addons = []
Restricted_access = 0
No_License = 0
#-------------------------------------------------------------------------------------
window_width = 800
window_height = 400

def run(*kwargs):
#----------------------------- Licensing ---------------------------------------------
    global Full_access, Limited_access, Addon_Test, Restricted_access, No_License
    for element in kwargs:
        element = str(element)
        element = element.split(",")
        for elem in element:
            elem = elem.replace("[", "")
            elem = elem.replace("]", "")
            elem = elem.replace("'", "")
            elem = elem.strip()
            #print(elem)
            if elem == "Full_access":
                Full_access = 1
                #print("FULL ACCESS")
            elif elem == "Limited_access":
                Limited_access = 1
                #print("LIMITED ACCESS")
            elif elem == "Restricted_access":
                Restricted_access = 1
                print("NO INTERNET CONNECTION - RESTRICTED ACCES")
            elif "Addon:" in elem:
                Addons.append(elem)
                #print(elem)
            else:
                No_License = 1
                #print("NO VALID LICENSE")
#-------------------------------------------------------------------------------------
    setup(Full_access, Limited_access, Restricted_access, Addons, No_License)