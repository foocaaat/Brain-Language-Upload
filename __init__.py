# -*- coding: utf-8 -*-

"""
Anki Add-on: Edit Field During Review

Edit text in a field during review without opening the edit window

Copyright: (c) 2019-2020 Nickolay Nonard <kelciour@gmail.com>
"""


from __future__ import unicode_literals

############## USER CONFIGURATION START ##############

# Shortcuts need to be single keys on Anki 2.0.x
# Key combinations are supported on Anki 2.1.x

# Shortcut that will reveal the hint fields one by one:
SHOWER = "Down"
ANSWER = "Right"
GOBACK = "Left"
HALFSHOW = "Up"

# Shortcut that will reveal all hint fields at once:
SHORTCUT_START1 = ","
SHORTCUT_START2 = "."
SHORTCUT_END1 = "["
SHORTCUT_END2 = "]"


ansa = 0
##############  USER CONFIGURATION END  ##############

from aqt.qt import *
from aqt import mw
from aqt.reviewer import Reviewer
import json
import time
from aqt import gui_hooks
import anki
import os
import subprocess
from anki.hooks import wrap, addHook
from aqt.operations import QueryOp
from anki import version as ankiversion
from aqt.import_export.importing import import_file
import threading
from datetime import timedelta
from anki.schedv2 import * 
import platform
operating_system = platform.system()
from aqt.utils import tooltip
from aqt.utils import showInfo
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from python_mpv_jsonipc import MPV
from pysubs2 import SSAFile
import pysubs2
from PyQt5.QtWidgets import QApplication, QFileDialog

###############
class DevNull:
    def write(self, msg):
        pass
sys.stderr = DevNull()
##################
script_dir = os.path.dirname(os.path.abspath(__file__))

old_fillRev = anki.schedv2.Scheduler._fillRev
is_old_fillRev = True





def jessygo(object_key, object_value):
    # Load the JSON file
    try:
        with open(os.path.abspath(os.path.join(script_dir, "mpvanki.json")), "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, create an empty dictionary
        data = {}

    # Add or update the object in the dictionary
    data[object_key] = object_value

    # Write the updated dictionary to the JSON file
    with open(os.path.abspath(os.path.join(script_dir, "mpvanki.json")), "w") as file:
        json.dump(data, file, indent=4)

def jessycome(object_key):
    # Load the JSON file
    try:
        with open(os.path.abspath(os.path.join(script_dir, "mpvanki.json")), "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, return None
        return None

    # Return the value of the object
    return data.get(object_key)

def  new_fillRev(self, recursing=False) -> bool:
        "True if a review card can be fetched."
        if self._revQueue:
            return True
        if not self.revCount:
            return False

        lim = min(self.queueLimit, self._currentRevLimit())
        if lim:
            self._revQueue = self.col.db.list(
                f"""
select id from cards where
did in %s and queue = {QUEUE_TYPE_REV} and due <= ?
order by nid
limit ?"""
# order by due, random()
                % self._deckLimit(),
                self.today,
                lim,
            )

            if self._revQueue:
                # preserve order
                self._revQueue.reverse()
                return True

        return False


def created_order_on_off():
    if is_old_fillRev == True:
        anki.schedv2.Scheduler._fillRev = new_fillRev
        is_old_fillRev == False
    else:
        anki.schedv2.Scheduler._fillRev = old_fillRev
        is_old_fillRev == True

created_order_on_off()

if operating_system == "Windows":
    windows_dir = os.path.join(script_dir, "windows")
    path = os.environ.get("PATH", "")
    if windows_dir not in path:
        os.environ["PATH"] = windows_dir + os.pathsep + path


def millis_to_time_format(milliseconds):
    milliseconds = int(milliseconds)
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:01d}.{:02d}.{:02d}.{:03d}'.format(hours, minutes, seconds, milliseconds)

def extract_timestamps(file):
    subs = SSAFile.load(file)
    timestamps = []
    added = set()
    start2 = 0
    end2 = 0
    for line in subs:
        start0 = int(line.start)
        end0 = int(line.end)
        start = int(line.start - 500)
        end = int(line.end + 500)
        if start < 0:
            start = 0
        startt = millis_to_time_format(start)
        endd = millis_to_time_format(end)
        timestamp = f"{startt} - {endd}"
        if timestamp not in added:
            if end0 - start0 > 100:
                if start0 >= end2:
                    added.add(timestamp)
                    end2 = end0
                    timestamps.append((f"{startt}", f"{endd}"))
    return timestamps


def assemble(mkve, stampa):
    tempy = os.path.join(str(ankivideo),"stamp/tmp.srt") 
    for file in mkve:
        src_video_paths = []
        filey = str(file)
        file = os.path.join(str(ankivideo), file)
        if file.endswith('mkv'):
            src_video_paths.append(file)
        for src_video_path in src_video_paths:
            command = ['ffprobe', '-v', 'error', '-select_streams', 's', '-show_entries', 'stream=index,codec_name:stream_tags=NUMBER_OF_BYTES-eng,NUMBER_OF_BYTES,language', '-of', 'default=noprint_wrappers=1', '-print_format', 'csv', src_video_path]
            tete = subprocess.check_output(command).decode()



            try:
                filty = sorted(tete.splitlines(), key=lambda x: int(x.split(',')[-1]), reverse=True)
                filty = '\n'.join(filty)
            except:
                pass
                filty = tete

            lines = filty.splitlines()
            filtered_lines = [line for line in lines if "ass" in line or "srt" in line or "subrip" in line]
            filty = '\n'.join(filtered_lines)

            tete = '\n'.join(line.split(',')[1] for line in filty.splitlines())
            try:
                tete = int(tete.splitlines()[0])
            except:
                global sniff
                sniff.append(file)
                return
            os.system(f'mkvextract "{src_video_path}" tracks {tete}:{tempy}\n')
            subs = pysubs2.load(tempy)
            subs.save(tempy, format="srt")
        timestamps = extract_timestamps(tempy)
        os.remove(tempy)
        counter = 0

        with open(os.path.join(str(ankivideo), f'stamp/{os.path.splitext(stampa)[0]}.txt') , 'a') as f:
            for start, end in timestamps:
                counter += 1
                formatted_counter = str(counter).zfill(5)
                f.write(f"{filey}{formatted_counter}	{filey}	{start}	{end}	{formatted_counter}\n")

        try:
            liste = list(jessycome("filelist"))
        except:
            liste = []
        liste.append(filey)
        jessygo("filelist", liste)

def find_missing_items(list1, list2):
    missing_items = []
    for item in list1:
        if item not in list2:
            missing_items.append(item)
    return missing_items
def synclist():
    if not os.path.exists(os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp"))):
        os.makedirs(os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp")))
    exclude_list = os.listdir(os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp")))
    if not exclude_list:
        exclude_list = []
    exclude_list = [f for f in exclude_list if f.endswith('.txt')]
    exclude_list = [os.path.splitext(name)[0] for name in exclude_list]

    all_files = os.listdir(jessycome("ankivideo"))
    result = [f for f in all_files if (os.path.isdir(os.path.join(ankivideo, f)) or f.endswith('.mkv')) and f != 'stamp']
    result = [os.path.splitext(name)[0] for name in result]
    result = [item for item in result if item not in exclude_list]
    result.sort()
    return result

def filesinside(folder):
    all_files = os.listdir(folder)
    result = [f for f in all_files if f.endswith('.mkv') ]
    result.sort()
    return result

def ofolder(where):
    if platform.system() == "Windows":
        os.startfile(where)
    else:
        os.system('xdg-open "%s" &' % os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp")))
    return


def addnewstuff(number=0):
    global sniff
    sniff = []
    global ankivideo
    ankivideo = jessycome("ankivideo") 
    if not os.path.exists(os.path.abspath(str(jessycome("ankivideo")))):
        if jessycome("speeed"):
            subprocess.Popen(['mpv', '--no-config', '--terminal', os.path.join(script_dir, "speeed", 'selectfolder.wav')])
        else:
            showInfo("make sure you selected the video folder")
        return
    be = synclist()
    if be != []:
        if jessycome("speeed"):
            subprocess.Popen(['mpv', '--no-config', '--terminal',os.path.join(script_dir, "speeed", 'startimport.wav')])
        else:
            showInfo("there are some files that are going to be imported")
    else:
        if number == 0:
            if jessycome("speeed"):
                subprocess.Popen(['mpv', '--no-config', '--terminal',os.path.join(script_dir, "speeed", 'nonewfile.wav')])
            else:
                showInfo("there are no new files")
            return

    def my_background_op(be) -> int:
        for thing in be:
            if os.path.isdir(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing))):
                thingss = filesinside(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing)))
                thingss = [os.path.join(thing, name) for name in thingss]
                print(f"folder {thingss}")
                assemble(thingss, thing)
            if os.path.isfile(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing + ".mkv"))):
                thing = thing + ".mkv"
                print(f"file {thing}")
                assemble([thing], thing)

        return len(be)

    def on_success(count: int) -> None:
        mw.progress.finish()
        if count > 0:
            ofolder(os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp")))
            if jessycome("speeed"):
                subprocess.Popen(['mpv', '--no-config', '--terminal',os.path.join(script_dir, "speeed", 'done.wav')])
            else:
                showInfo("the files are locked and loaded")
        if sniff != []:
            showInfo(f"i sniff a non combatable mkv: {sniff}")

    op = QueryOp(parent=mw, op=lambda col: my_background_op(be), success=on_success)
    op.with_progress().run_in_background()

def on_anki_startup():
    addnewstuff(1)


def videofilelocation():
    directory = QFileDialog.getExistingDirectory(None, "Select Directory", "./")
    if not directory:
        return
    jessygo("ankivideo", f"{directory}")

try:
    ankivideo = jessycome("ankivideo") 
except:
    try:
        if jessycome("speeed"):
            subprocess.Popen(['mpv', '--no-config', '--terminal',os.path.join(script_dir, "speeed", 'selectfolder.wav')])
        else:
            showInfo("make sure you selected the video folder")
    except:
        pass

# create a new menu item, "test"
action = QAction("On - Off Review Created Order", mw)
action2 = QAction("Select videos location", mw)
action3 = QAction("turn new videos to srs", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(created_order_on_off)
action2.triggered.connect(videofilelocation)
action3.triggered.connect(addnewstuff)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
mw.form.menuTools.addAction(action2)
mw.form.menuTools.addAction(action3)



def dueToday(): # formeeeeeeeeeee
    # Globals and reset variables
    if operating_system == "Linux":
        global dueMessage
        dueCount = 0

        # Loop through deckDueTree to find cards due
        for i in mw.col.sched.deckDueTree():
            name, did, due, lrn, new, children = i
            dueCount += due + lrn + new

        # Correct for single or no cards
        os.system("echo " + str(dueCount) + " > " + os.path.join("$HOME/.cache", "ankileft") + " &" )
        tooltip(dueCount)





def time_in_seconds(time):
    h, m, s, ms = map(int, time.split('.'))
    total_seconds = (h * 3600) + (m * 60) + s
    return "{}.{}".format(total_seconds, ms)
global stopa
stopa = []
stopan = -1
def mpvankii(v1, v2, v3, v4, v5, v6):
    ankivideo = str(jessycome("ankivideo"))
    os.path.abspath(os.path.join(ankivideo, v1))
    if not os.path.exists(os.path.abspath(os.path.join(ankivideo, v1))):
        try:
            if jessycome("speeed"):
                subprocess.Popen(['mpv', '--no-config', '--terminal',os.path.join(script_dir, "speeed", 'notinthefolder.wav')])
            else:
                tooltip("the file is not in the folder")
        except:
            pass
        return
    mpv = MPV(start_mpv=False, ipc_socket=os.path.abspath("/tmp/mpv-socket"))
    if not v5:
        v5=0
    if not v6:
        v6=0

    START=float(time_in_seconds(v2))
    END=float(time_in_seconds(v3))
    try:
        number = int(str(v4).lstrip("0"))
    except:
        number = int(999)




    global var1,var2,var3,var4,var5
    var1 = jessycome("var1") 
    var2 = str(jessycome("var2")) 
    var3 = str(jessycome("var3"))
    var4 = jessycome("var4") 
    try:
        if v5 == "yes":
            var5 = float(jessycome(str(v1)))
    except:
        jessygo(str(v1),END) 
        var5 = float(jessycome(str(v1)))

    if "1" == v6:
        mpv.command("set_property", "sub-visibility", True)
    else:
        mpv.command("set_property", "sub-visibility", False)


    workingfile=str(mpv.command("get_property", "path"))
    if os.path.abspath(str(workingfile)) != os.path.abspath(os.path.join(ankivideo, v1)):
        mpv.command("loadfile", os.path.abspath(os.path.join(ankivideo, v1)))
        if os.path.isfile(os.path.abspath(os.path.join(ankivideo, v1))):
            while True:
                stream=str(mpv.command("get_property", "stream-pos"))
                try:
                    if int(stream) > 0:
                        break
                except: pass
###

    if var1 == v1 and var4 == number - 1 and float(var3) < START: 
        pass
    else:
        if v5 == "yes" and number == 1 and var4 != 1:
            mpv.command("seek", 0, "absolute")
        else:
            if v5 == "yes" and float(var5) < START and var5 != 0.0:

                mpv.command("seek", str(var5), "absolute")
            else:
                mpv.command("seek", str(START), "absolute")

    mpv.command("set_property", "pause", False)

    
# 2. Update json object
# 3. Write json file

    jessygo("var1",v1) 
    jessygo("var2",START) 
    jessygo("var3",END) 
    jessygo("var4",number) 

    if v5 == "yes":
        jessygo(str(v1),END) 


    global stopan
    global stopa
    try:
        stopa[-1] = False
    except:
        pass
    stopan += 1
    stopa.append(True)
    process = threading.Thread(target=stoopu, args=(str(END),))
    process.start()

def stoopu(when):
    global stopan
    global stopa
    soso = stopan 
    while True:
        if str(mpv.command("get_property", "time-pos")) != 'None':
                if not stopa[soso]:
                    print(2)
                    break
                elif 0 <= float(str(mpv.command("get_property", "time-pos"))) - float(when) <= 0.5:
                    if not stopa[soso]:
                        print(2)
                        break
                    print(3)
                    mpv.command("set_property", "pause", True)
                    break
        time.sleep(0.05)
    print("done")

def run_command_field(num=0):
    global ansa
    ansa = 3

    if mw.reviewer.card.queue == 0:
        new = "yes"
    else:
        new = "no"
        if num == 1:
            ansa = 1

    # Get the current note
    sub = "0"
    if num == 1:
        sub = "1"
    note = mw.reviewer.card.note()
    # Check if a field called "Command" exists
    if "mpvanki-filename" in note:
#        if num == 1:
#            os.system("mpvanki " + command + " e &")
#        else:
        global mpv
        try:
            mpv.command("get_property", "stream-pos")
        except:
            mpv = MPV(start_mpv=True, ipc_socket=os.path.abspath("/tmp/mpv-socket"))

        mpvankii( note["mpvanki-filename"], note["mpvanki-start"], note["mpvanki-end"], note["mpvanki-number"], new, sub)



def ansae(ansa):
    dueToday()  # formeeeeeeeeeee
    card = mw.reviewer.card
    mw.col.sched.answerCard(card, ansa)
    mw.reviewer.nextCard()
    mw.update_undo_actions()


def add_time(time_string, nu):
    # Split the time string into hours, minutes, seconds, and milliseconds
    note = mw.reviewer.card.note()
    time_string2 = note[time_string]
    time_parts = time_string2.split('.')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = int(time_parts[2])
    milliseconds = int(time_parts[3])

    # Create a timedelta object with the current time
    current_time = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    # Add 500 milliseconds to the current time
    if nu == 1: new_time = current_time + timedelta(milliseconds=50)
    else: new_time = current_time - timedelta(milliseconds=50)

    # Format the new time into a string
    new_time_string = "{:01d}.{:02d}.{:02d}.{:03d}".format(new_time.seconds//3600, (new_time.seconds//60)%60, new_time.seconds%60, new_time.microseconds//1000)

    note[time_string] = new_time_string
    note.flush()

    if time_string == "mpvanki-start":
        if nu == 1: tooltip("-100ms →-----")
        else: tooltip("+100ms ←-----")
        run_command_field()
    if time_string == "mpvanki-end":
        if nu == 1:
            tooltip("+100ms -----→")
            new_time2 = current_time - timedelta(milliseconds=150)
        else:
            tooltip("-100ms -----←")
            new_time2 = current_time - timedelta(milliseconds=250)
        new_time_string2 = "{:01d}.{:02d}.{:02d}.{:03d}".format(new_time2.seconds//3600, (new_time2.seconds//60)%60, new_time2.seconds%60, new_time2.microseconds//1000)

        global mpv
        try: mpv.command("get_property", "stream-pos")
        except: mpv = MPV(start_mpv=True, ipc_socket=os.path.abspath("/tmp/mpv-socket"))

        if mw.reviewer.card.queue == 0: new = "yes"
        else: new = "no"
        mpvankii( note["mpvanki-filename"], new_time_string2, note["mpvanki-end"], note["mpvanki-number"], new, 0)


def _addShortcuts(shortcuts):
    """Add shortcuts on Anki 2.1.x"""
    additions = (
        (SHORTCUT_START1, lambda: add_time("mpvanki-start", 0)),
        (SHORTCUT_START2, lambda: add_time("mpvanki-start", 1)),
        (SHORTCUT_END1, lambda: add_time("mpvanki-end", 0)),
        (SHORTCUT_END2, lambda: add_time("mpvanki-end", 1)),
        (ANSWER, lambda: ansae(ansa)),
        (HALFSHOW, lambda: run_command_field()),
        (GOBACK, lambda: mw.form.actionUndo.trigger()),
        (SHOWER, lambda: run_command_field(1))
    )
    shortcuts += additions


gui_hooks.reviewer_did_show_question.append(run_command_field)
# Hooks and Patches
if ankiversion.startswith("2.0"): # 2.0.x
    Reviewer._keyHandler = wrap(
        Reviewer._keyHandler, _newKeyHandler, "around")
else: # 2.1.x
    addHook("reviewStateShortcuts", _addShortcuts)
    addHook("profileLoaded", on_anki_startup)
