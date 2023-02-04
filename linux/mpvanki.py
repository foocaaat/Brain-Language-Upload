#!/usr/bin/python3
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
import sys
import subprocess


def time_in_seconds(time):
    h, m, s, ms = map(int, time.split('.'))
    total_seconds = (h * 3600) + (m * 60) + s
    return "{}.{}".format(total_seconds, ms)

import os
import time

ankivideo="/home/foocaaat/.local/share/AnkiVideo/"

def mpvankii(v1, v2, v3, v4, v5, v6):
    if not v5:
        v5=0
    if not v6:
        v6=0

    file=script_dir +"/mpvanki.log"
    file2=script_dir + "/" + v1 +  "mpvanki.log"

    START=float(time_in_seconds(v2))
    END=float(time_in_seconds(v3))
    number = int(str(v4).lstrip("0"))




    global var1,var2,var3,var4,var5
    try:
        with open(file, "r") as f:
            line = f.readline().strip()
        if line:
            var1 = line.split()[0]
            var2 = float(line.split()[1])
            var3 = float(line.split()[2])
            var4 = int(line.split()[3])
        else:
            var1 = float(0)
            var2 = float(0)
            var3 = float(0)
            var4 = int(0)
    except FileNotFoundError: open(file, "w").close()
    try:
        with open(file2, "r") as f:
            line = f.readline().strip()
        if line:
            var5 = float(line.split()[0])
        else:
            var5 = float(0)
    except FileNotFoundError: open(file2, "w").close()





    if "1" == v6:
        os.system("echo '{\"command\":[\"set_property\", \"sub-visibility\", true]}' | socat - /tmp/mpv-socket") 
    else:
        os.system("echo '{\"command\":[\"set_property\", \"sub-visibility\", false]}' | socat - /tmp/mpv-socket") 


    workingfile=os.popen("echo '{\"command\":[\"get_property\", \"path\"]}' | socat - /tmp/mpv-socket | jq '.data' | tr -d '\"' ").read()
    if str(workingfile) != ankivideo + v1 + "\n":
        os.system("echo '{\"command\":[\"loadfile\", \"" + ankivideo + v1 + "\"]}' | socat - /tmp/mpv-socket") 

    while True:
        stream=os.popen("echo '{\"command\":[\"get_property\", \"stream-pos\"]}' | socat - /tmp/mpv-socket | jq '.data' | tr -d '\"' ").read()
        try:
            if int(stream) > 0:
                break
        except: pass
###


    if var1 == v1 and var4 == number - 1 and var3 < START: 
        print("e")
    else:
        if v5 == "yes" and number == 1 and var4 != 1:
            os.system("echo '{\"command\":[\"seek\", \'0\', \"absolute\"]}' | socat - /tmp/mpv-socket") 
        else:
            print(var5)
            if v5 == "yes" and var5 < START and var5 != 0.0:

                os.system("echo '{\"command\":[\"seek\", \'" + str(var5) + "', \"absolute\"]}' | socat - /tmp/mpv-socket") 
            else:
                os.system("echo '{\"command\":[\"seek\", \'" + str(START) + "', \"absolute\"]}' | socat - /tmp/mpv-socket") 

    os.system("echo '{\"command\":[\"set_property\", \"pause\", false]}' | socat - /tmp/mpv-socket") 
    

    with open(file, 'w') as f:
            f.write(f"{v1} {START} {END} {number}")
    with open(file2, 'w') as f:
            f.write(f"{END}")

    while True:
        position=os.popen("echo '{\"command\":[\"get_property\", \"time-pos\"]}' | socat - /tmp/mpv-socket | jq '.data' | tr -d '\"' ").read()
        if float(position) >= float(END):
            print(float(position))
            print(float(END))
            os.system("echo '{\"command\":[\"set_property\", \"pause\", true]}' | socat - /tmp/mpv-socket") 
            break
        time.sleep(0.05)


try:
    a1 = sys.argv[1]
except:
    a1 = "null"
try:
    a2 = sys.argv[2]
except:
    a2 = float(0)
try:
    a3 = sys.argv[3]
except:
    a3 = float(0)
try:
    a4 = sys.argv[4]
except:
    a4 = str(99999)
try:
    a5 = sys.argv[5]
except:
    a5 = "0"
try:
    a6 = sys.argv[6]
except:
    a6 = "0"

result = subprocess.run(["pgrep", "-f", "mpvplayer.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if result.stdout != b'':
    mpvankii(a1, a2, a3, a4, a5, a6)
