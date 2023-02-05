#!/usr/bin/python3
import os
import sys
import subprocess
import time

from python_mpv_jsonipc import MPV

mpv = MPV(start_mpv=False, ipc_socket="/tmp/mpv-socket")




script_dir = os.path.dirname(os.path.abspath(__file__))


def time_in_seconds(time):
    h, m, s, ms = map(int, time.split('.'))
    total_seconds = (h * 3600) + (m * 60) + s
    return "{}.{}".format(total_seconds, ms)

#vvvvvvvvvvvvv
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

    if not os.path.exists(file):
        with open(file, 'w') as f:
                f.write(f"{v1} {START} {END} {number}")
                f.close()
    if not os.path.exists(file2):
        with open(file2, 'w') as f:
                f.write(f"{END}")
                f.close()
    try:
        with open(file2, "r") as f:
            line = f.readline().strip()
        if line:
            var5 = float(line.split()[0])
        else:
            var5 = float(0)
    except FileNotFoundError: open(file2, "w").close()





    if "1" == v6:
        mpv.command("set_property", "sub-visibility", True)
    else:
        mpv.command("set_property", "sub-visibility", False)


    workingfile=str(mpv.command("get_property", "path"))
    if str(workingfile) != ankivideo + v1:
        mpv.command("loadfile", ankivideo + v1)

    while True:
        stream=str(mpv.command("get_property", "stream-pos"))
        try:
            if int(stream) > 0:
                break
        except: pass
###

    if var1 == v1 and var4 == number - 1 and var3 < START: 
        pass
    else:
        if v5 == "yes" and number == 1 and var4 != 1:
            mpv.command("seek", 0, "absolute")
        else:
            if v5 == "yes" and var5 < START and var5 != 0.0:

                mpv.command("seek", str(var5), "absolute")
            else:
                mpv.command("seek", str(START), "absolute")

    mpv.command("set_property", "pause", False)

    

    with open(file, 'w') as f:
            f.write(f"{v1} {START} {END} {number}")
            f.close()
    with open(file2, 'w') as f:
            f.write(f"{END}")
            f.close()

    while True:
        position=str(mpv.command("get_property", "time-pos"))
        if float(position) >= float(END):
            mpv.command("set_property", "pause", True)
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


mpvankii(a1, a2, a3, a4, a5, a6)
mpv.terminate()
