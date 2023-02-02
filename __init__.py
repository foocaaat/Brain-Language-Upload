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
SHORTCUT_INCREMENTAL = "R"
SHORTCUT_START1 = "Z"
SHORTCUT_START2 = "X"
SHOWER = "Down"
ANSWER = "Right"
# Shortcut that will reveal all hint fields at once:
ansa = 0
SHORTCUT_END1 = ","
SHORTCUT_END2 = "."

##############  USER CONFIGURATION END  ##############

from aqt.qt import *
from aqt import mw
from aqt.reviewer import Reviewer
import time
from anki import hooks
from anki.template import TemplateRenderContext
import subprocess
import os
from anki.hooks import wrap, addHook
from anki import version as ankiversion

script_dir = os.path.dirname(os.path.abspath(__file__))

def dueToday(): # formeeeeeeeeeee
    # Globals and reset variables
    global dueMessage
    dueCount = 0

    # Loop through deckDueTree to find cards due
    for i in mw.col.sched.deckDueTree():
        name, did, due, lrn, new, children = i
        dueCount += due + lrn + new

    # Correct for single or no cards
    if dueCount == 0:
        dueMessage = "No cards left"
        os.system("echo " + str(dueCount) + " > .cache/ankileft &" )
    elif dueCount == 1:
        dueMessage = "(" + str(dueCount) + " card left)"
        os.system("echo " + str(dueCount) + " > .cache/ankileft &" )
    else:
        dueMessage = "(" + str(dueCount) + " cards left)"        
        os.system("echo " + str(dueCount) + " > .cache/ankileft &" )
    return dueMessage


def answer():
    Reviewer._answerCard(1)


def run_mpv_commandunix():
    # Check if the command is already running
    result = subprocess.run(["pgrep", "-f", "mpvplayer.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stdout == b'':
        os.system("$(" + script_dir +  "/linux/mpvplayer.sh ) &")
        time.sleep(1)
        os.system("$(" + script_dir +  "/linux/mpvanki.sh black.png) &")
        time.sleep(1)

from datetime import timedelta
from aqt.qt import QToolTip, QCursor

def run_command_field(num=0):
    global ansa
    ansa = 3
    current_card = mw.reviewer.card

    # Check if the card is new
    if current_card.queue == 0:
        new = "yes"
    else:
        new = "no"
        if num == 1:
            ansa = 1

    # Get the current note
    sub = "0"
    if num == 1:
        sub = "1"
        _showHint()
    note = mw.reviewer.card.note()
    # Check if a field called "Command" exists
    if "mpvanki-filename" in note:
        os.system("pkill mpvanki")
        dueToday()  # formeeeeeeeeeee
#        if num == 1:
#            os.system("mpvanki " + command + " e &")
#        else:
        run_mpv_commandunix()
        os.system("$(" + script_dir +  "/linux/mpvanki.sh " + note["mpvanki-filename"] + " " + note["mpvanki-start"] + " " + note["mpvanki-end"] + " " + note["mpvanki-number"] + " " + new + " " + sub + ") &")

def ansae(ansa):
    card = mw.reviewer.card
    mw.col.sched.answerCard(card, ansa)
    mw.reviewer.nextCard()

def add_time(time_string):
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
    new_time = current_time + timedelta(milliseconds=500)

    # Format the new time into a string
    new_time_string = "{:01d}.{:02d}.{:02d}.{:03d}".format(new_time.seconds//3600, (new_time.seconds//60)%60, new_time.seconds%60, new_time.microseconds//1000)

    note[time_string] = new_time_string
    note.flush()
    QToolTip.showText(QCursor.pos(), "Added 500 milliseconds from {} to become: {}".format(time_string, new_time_string))
    run_command_field()


def remove_time(time_string):
    # Get the current note
    note = mw.reviewer.card.note()
    # Get the time string from the note
    time_string2 = note[time_string]
    # Split the time string into hours, minutes, seconds, and milliseconds
    time_parts = time_string2.split('.')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = int(time_parts[2])
    milliseconds = int(time_parts[3])

    # Create a timedelta object with the current time
    current_time = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    # Remove 500 milliseconds from the current time
    new_time = current_time - timedelta(milliseconds=500)

    # Format the new time into a string
    new_time_string = "{:01d}.{:02d}.{:02d}.{:03d}".format(new_time.seconds//3600, (new_time.seconds//60)%60, new_time.seconds%60, new_time.microseconds//1000)

    # Update the note field with the new time
    note[time_string] = new_time_string
    note.flush()
    QToolTip.showText(QCursor.pos(), "Removed 500 milliseconds from {} to become: {}".format(time_string, new_time_string))
    run_command_field()


addHook("showAnswer", run_command_field)



def _newKeyHandler(self, evt, _old):
    """Add shortcuts on Anki 2.0.x"""
    if evt.key() == QKeySequence(SHORTCUT_INCREMENTAL)[0]:
        _showHint(incremental=True)
    elif evt.key() == QKeySequence(SHOWER)[0]:
        _showHint()
    return _old(self, evt)


def _addShortcuts(shortcuts):
    """Add shortcuts on Anki 2.1.x"""
    additions = (
        (SHORTCUT_INCREMENTAL, lambda: run_command_field(1)),
        (SHORTCUT_START1, lambda: remove_time("mpvanki-start")),
        (SHORTCUT_START2, lambda: add_time("mpvanki-start")),
        (SHORTCUT_END1, lambda: remove_time("mpvanki-end")),
        (SHORTCUT_END2, lambda: add_time("mpvanki-end")),
        (ANSWER, lambda: ansae(ansa)),
        (SHOWER, lambda: run_command_field(1))
    )
    shortcuts += additions


def _showHint(incremental=False):
    """Show hint by activating corresponding links."""
    mw.web.eval("""
     var customEvent = document.createEvent('MouseEvents');
     customEvent.initEvent('click', false, true);
     var arr = document.getElementsByTagName('a');
     // Cloze Overlapper support
     if (typeof olToggle === "function") { 
         olToggle();
     }
     // Image Occlusion Enhanced support
     var ioBtn = document.getElementById("io-revl-btn");
     if (!(typeof ioBtn === 'undefined' || !ioBtn)) { 
         ioBtn.click();
     }
     for (var i=0; i<arr.length; i++) {
        var l=arr[i];
        if (l.style.display === 'none') {
          continue;
        }
        if (l.href.charAt(l.href.length-1) === '#') {
          l.dispatchEvent(customEvent);
          if ('%s' === 'True') {
            break;
          }
        }
     }
     """ % incremental)


# Hooks and Patches

if ankiversion.startswith("2.0"): # 2.0.x
    Reviewer._keyHandler = wrap(
        Reviewer._keyHandler, _newKeyHandler, "around")
else: # 2.1.x
    addHook("reviewStateShortcuts", _addShortcuts)
