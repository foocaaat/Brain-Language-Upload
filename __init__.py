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
import time
from anki import hooks
import anki
from anki.template import TemplateRenderContext
import subprocess
import os
from anki.hooks import wrap, addHook
from anki import version as ankiversion
import multiprocessing
from threading import Thread
from datetime import timedelta
from aqt.qt import QToolTip, QCursor
from anki.schedv2 import * 
import sys
class DevNull:
    def write(self, msg):
        pass

sys.stderr = DevNull()


####################
old_fillRev = anki.schedv2.Scheduler._fillRev
is_old_fillRev = True


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

import platform
script_dir = os.path.dirname(os.path.abspath(__file__))

operating_system = platform.system()

try:
    with open(os.path.abspath(os.path.join(script_dir, "ankivideo.log")), "r") as f:
        line = f.readline().strip()
        global ankivideo
        ankivideo = os.path.abspath(line.split()[0])
except:
        with open(os.path.abspath(os.path.join(script_dir, "ankivideo.log")), 'w') as f:
                f.write(f"{script_dir}/")
                f.close()

def videofilelocation():
    from PyQt5.QtWidgets import QApplication, QFileDialog
    directory = QFileDialog.getExistingDirectory(None, "Select Directory", "./")
    with open(os.path.abspath(os.path.join(script_dir, "ankivideo.log")), 'w') as f:
            f.write(f"{directory}/")
            f.close()
    with open(os.path.abspath(os.path.join(script_dir, "ankivideo.log")), "r") as f:
        line = f.readline().strip()
        global ankivideo
        ankivideo = line.split()[0]
    quit()

def created_order_on_off():
    if is_old_fillRev == True:
        anki.schedv2.Scheduler._fillRev = new_fillRev
        is_old_fillRev == False
    else:
        anki.schedv2.Scheduler._fillRev = old_fillRev
        is_old_fillRev == True

created_order_on_off()
# create a new menu item, "test"
action = QAction("On - Off Review Created Order", mw)
action2 = QAction("Select videos location", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(created_order_on_off)
action2.triggered.connect(videofilelocation)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
mw.form.menuTools.addAction(action2)


######################
######################
######################
######################
######################
######################


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
        if dueCount == 0:
            dueMessage = "No cards left"
            os.system("echo " + str(dueCount) + " > " + os.path.join("$HOME/.cache", "ankileft") + " &" )
        elif dueCount == 1:
            dueMessage = "(" + str(dueCount) + " card left)"
            os.system("echo " + str(dueCount) + " > " + os.path.join("$HOME/.cache", "ankileft") + " &" )
        else:
            dueMessage = "(" + str(dueCount) + " cards left)"        
            os.system("echo " + str(dueCount) + " > " + os.path.join("$HOME/.cache", "ankileft") + " &" )
        return dueMessage


def answer():
    Reviewer._answerCard(1)

########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
####python-mpv-module###

import threading
import socket
import json
import os
import time
import subprocess
import random
import queue
import logging

log = logging.getLogger('mpv-jsonipc')

if os.name == "nt":
    import _winapi
    from multiprocessing.connection import PipeConnection

TIMEOUT = 120

# Older MPV versions do not allow us to dynamically retrieve the command list.
FALLBACK_COMMAND_LIST = [
    'ignore', 'seek', 'revert-seek', 'quit', 'quit-watch-later', 'stop', 'frame-step', 'frame-back-step',
    'playlist-next', 'playlist-prev', 'playlist-shuffle', 'playlist-unshuffle', 'sub-step', 'sub-seek',
    'print-text', 'show-text', 'expand-text', 'expand-path', 'show-progress', 'sub-add', 'audio-add',
    'video-add', 'sub-remove', 'audio-remove', 'video-remove', 'sub-reload', 'audio-reload', 'video-reload',
    'rescan-external-files', 'screenshot', 'screenshot-to-file', 'screenshot-raw', 'loadfile', 'loadlist',
    'playlist-clear', 'playlist-remove', 'playlist-move', 'run', 'subprocess', 'set', 'change-list', 'add',
    'cycle', 'multiply', 'cycle-values', 'enable-section', 'disable-section', 'define-section', 'ab-loop',
    'drop-buffers', 'af', 'vf', 'af-command', 'vf-command', 'ao-reload', 'script-binding', 'script-message',
    'script-message-to', 'overlay-add', 'overlay-remove', 'osd-overlay', 'write-watch-later-config',
    'hook-add', 'hook-ack', 'mouse', 'keybind', 'keypress', 'keydown', 'keyup', 'apply-profile',
    'load-script', 'dump-cache', 'ab-loop-dump-cache', 'ab-loop-align-cache']

class MPVError(Exception):
    """An error originating from MPV or due to a problem with MPV."""
    def __init__(self, *args, **kwargs):
        super(MPVError, self).__init__(*args, **kwargs)

class WindowsSocket(threading.Thread):
    """
    Wraps a Windows named pipe in a high-level interface. (Internal)
    
    Data is automatically encoded and decoded as JSON. The callback
    function will be called for each inbound message.
    """
    def __init__(self, ipc_socket, callback=None, quit_callback=None):
        """Create the wrapper.

        *ipc_socket* is the pipe name. (Not including \\\\.\\pipe\\)
        *callback(json_data)* is the function for recieving events.
        *quit_callback* is called when the socket connection dies.
        """
        ipc_socket = "\\\\.\\pipe\\" + ipc_socket
        self.callback = callback
        self.quit_callback = quit_callback
        
        access = _winapi.GENERIC_READ | _winapi.GENERIC_WRITE
        limit = 5 # Connection may fail at first. Try 5 times.
        for _ in range(limit):
            try:
                pipe_handle = _winapi.CreateFile(
                    ipc_socket, access, 0, _winapi.NULL, _winapi.OPEN_EXISTING,
                    _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL
                    )
                break
            except OSError:
                time.sleep(1)
        else:
            raise MPVError("Cannot connect to pipe.")
        self.socket = PipeConnection(pipe_handle)

        if self.callback is None:
            self.callback = lambda data: None

        threading.Thread.__init__(self)

    def stop(self, join=True):
        """Terminate the thread."""
        if self.socket is not None:
            try:
                self.socket.close()
            except OSError:
                pass # Ignore socket close failure.
        if join:
            self.join()

    def send(self, data):
        """Send *data* to the pipe, encoded as JSON."""
        try:
            self.socket.send_bytes(json.dumps(data).encode('utf-8') + b'\n')
        except OSError as ex:
            if len(ex.args) == 1 and ex.args[0] == "handle is closed":
                raise BrokenPipeError("handle is closed")
            raise ex

    def run(self):
        """Process pipe events. Do not run this directly. Use *start*."""
        data = b''
        try:
            while True:
                current_data = self.socket.recv_bytes(2048)
                if current_data == b'':
                    break

                data += current_data
                if data[-1] != 10:
                    continue

                data = data.decode('utf-8', 'ignore').encode('utf-8')
                for item in data.split(b'\n'):
                    if item == b'':
                        continue
                    json_data = json.loads(item)
                    self.callback(json_data)
                data = b''
        except EOFError:
            if self.quit_callback:
                self.quit_callback()
        except Exception as ex:
            log.error("Pipe connection died.", exc_info=1)
            if self.quit_callback:
                self.quit_callback()

class UnixSocket(threading.Thread):
    """
    Wraps a Unix/Linux socket in a high-level interface. (Internal)
    
    Data is automatically encoded and decoded as JSON. The callback
    function will be called for each inbound message.
    """
    def __init__(self, ipc_socket, callback=None, quit_callback=None):
        """Create the wrapper.

        *ipc_socket* is the path to the socket.
        *callback(json_data)* is the function for recieving events.
        *quit_callback* is called when the socket connection dies.
        """
        self.ipc_socket = ipc_socket
        self.callback = callback
        self.quit_callback = quit_callback
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.connect(self.ipc_socket)

        if self.callback is None:
            self.callback = lambda data: None

        threading.Thread.__init__(self)

    def stop(self, join=True):
        """Terminate the thread."""
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_WR)
                self.socket.close()
                self.socket = None
            except OSError:
                pass # Ignore socket close failure.
        if join:
            self.join()

    def send(self, data):
        """Send *data* to the socket, encoded as JSON."""
        if self.socket is None:
            raise BrokenPipeError("socket is closed")
        self.socket.send(json.dumps(data).encode('utf-8') + b'\n')

    def run(self):
        """Process socket events. Do not run this directly. Use *start*."""
        data = b''
        try:
            while True:
                current_data = self.socket.recv(1024)
                if current_data == b'':
                    break

                data += current_data
                if data[-1] != 10:
                    continue

                data = data.decode('utf-8', 'ignore').encode('utf-8')
                for item in data.split(b'\n'):
                    if item == b'':
                        continue
                    json_data = json.loads(item)
                    self.callback(json_data)
                data = b''
        except Exception as ex:
            log.error("Socket connection died.", exc_info=1)
        if self.quit_callback:
            self.quit_callback()

class MPVProcess:
    """
    Manages an MPV process, ensuring the socket or pipe is available. (Internal)
    """
    def __init__(self, ipc_socket, mpv_location=None, **kwargs):
        """
        Create and start the MPV process. Will block until socket/pipe is available.

        *ipc_socket* is the path to the Unix/Linux socket or name of the Windows pipe.
        *mpv_location* is the path to mpv. If left unset it tries the one in the PATH.

        All other arguments are forwarded to MPV as command-line arguments.
        """
        if mpv_location is None:
            if os.name == 'nt':
                mpv_location = "mpv.exe"
            else:
                mpv_location = "mpv"
        
        log.debug("Staring MPV from {0}.".format(mpv_location))
        ipc_socket_name = ipc_socket
        if os.name == 'nt':
            ipc_socket = "\\\\.\\pipe\\" + ipc_socket

        if os.name != 'nt' and os.path.exists(ipc_socket):
            os.remove(ipc_socket)

        log.debug("Using IPC socket {0} for MPV.".format(ipc_socket))
        self.ipc_socket = ipc_socket
        args = [mpv_location]
        self._set_default(kwargs, "idle", True)
        self._set_default(kwargs, "input_ipc_server", ipc_socket_name)
        self._set_default(kwargs, "input_terminal", False)
        self._set_default(kwargs, "terminal", False)
        args.extend("--{0}={1}".format(v[0].replace("_", "-"), self._mpv_fmt(v[1]))
                    for v in kwargs.items())
        self.process = subprocess.Popen(args)
        ipc_exists = False
        for _ in range(100): # Give MPV 10 seconds to start.
            time.sleep(0.1)
            self.process.poll()
            if os.path.exists(ipc_socket):
                ipc_exists = True
                log.debug("Found MPV socket.")
                break
            if self.process.returncode is not None:
                log.error("MPV failed with returncode {0}.".format(self.process.returncode))
                break
        else:
            self.process.terminate()
            raise MPVError("MPV start timed out.")
        
        if not ipc_exists or self.process.returncode is not None:
            self.process.terminate()
            raise MPVError("MPV not started.")

    def _set_default(self, prop_dict, key, value):
        if key not in prop_dict:
            prop_dict[key] = value

    def _mpv_fmt(self, data):
        if data == True:
            return "yes"
        elif data == False:
            return "no"
        else:
            return data

    def stop(self):
        """Terminate the process."""
        self.process.terminate()
        if os.name != 'nt' and os.path.exists(self.ipc_socket):
            os.remove(self.ipc_socket)

class MPVInter:
    """
    Low-level interface to MPV. Does NOT manage an mpv process. (Internal)
    """
    def __init__(self, ipc_socket, callback=None, quit_callback=None):
        """Create the wrapper.

        *ipc_socket* is the path to the Unix/Linux socket or name of the Windows pipe.
        *callback(event_name, data)* is the function for recieving events.
        *quit_callback* is called when the socket connection to MPV dies.
        """
        Socket = UnixSocket
        if os.name == 'nt':
            Socket = WindowsSocket

        self.callback = callback
        self.quit_callback = quit_callback
        if self.callback is None:
            self.callback = lambda event, data: None
        
        self.socket = Socket(ipc_socket, self.event_callback, self.quit_callback)
        self.socket.start()
        self.command_id = 1
        self.rid_lock = threading.Lock()
        self.socket_lock = threading.Lock()
        self.cid_result = {}
        self.cid_wait = {}
    
    def stop(self, join=True):
        """Terminate the underlying connection."""
        self.socket.stop(join)

    def event_callback(self, data):
        """Internal callback for recieving events from MPV."""
        if "request_id" in data:
            self.cid_result[data["request_id"]] = data
            self.cid_wait[data["request_id"]].set()
        elif "event" in data:
            self.callback(data["event"], data)
    
    def command(self, command, *args):
        """
        Issue a command to MPV. Will block until completed or timeout is reached.
        
        *command* is the name of the MPV command

        All further arguments are forwarded to the MPV command.
        Throws TimeoutError if timeout of 120 seconds is reached.
        """
        self.rid_lock.acquire()
        command_id = self.command_id
        self.command_id += 1
        self.rid_lock.release()

        event = threading.Event()
        self.cid_wait[command_id] = event

        command_list = [command]
        command_list.extend(args)
        try:
            self.socket_lock.acquire()
            self.socket.send({"command":command_list, "request_id": command_id})
        finally:
            self.socket_lock.release()

        has_event = event.wait(timeout=TIMEOUT)
        if has_event:
            data = self.cid_result[command_id]
            del self.cid_result[command_id]
            del self.cid_wait[command_id]
            if data["error"] != "success":
                if data["error"] == "property unavailable":
                    return None
                raise MPVError(data["error"])
            else:
                return data.get("data")
        else:
            raise TimeoutError("No response from MPV.")

class EventHandler(threading.Thread):
    """Event handling thread. (Internal)"""
    def __init__(self):
        """Create an instance of the thread."""
        self.queue = queue.Queue()
        threading.Thread.__init__(self)
    
    def put_task(self, func, *args):
        """
        Put a new task to the thread.
        
        *func* is the function to call
        
        All further arguments are forwarded to *func*.
        """
        self.queue.put((func, args))

    def stop(self, join=True):
        """Terminate the thread."""
        self.queue.put("quit")
        self.join(join)

    def run(self):
        """Process socket events. Do not run this directly. Use *start*."""
        while True:
            event = self.queue.get()
            if event == "quit":
                break
            try:
                event[0](*event[1])
            except Exception:
                log.error("EventHandler caught exception from {0}.".format(event), exc_info=1)

class MPV:
    """
    The main MPV interface class. Use this to control MPV.
    
    This will expose all mpv commands as callable methods and all properties.
    You can set properties and call the commands directly.
    
    Please note that if you are using a really old MPV version, a fallback command
    list is used. Not all commands may actually work when this fallback is used.
    """
    def __init__(self, start_mpv=True, ipc_socket=None, mpv_location=None,
                 log_handler=None, loglevel=None, quit_callback=None, **kwargs):
        """
        Create the interface to MPV and process instance.

        *start_mpv* will start an MPV process if true. (Default: True)
        *ipc_socket* is the path to the Unix/Linux socket or name of Windows pipe. (Default: Random Temp File)
        *mpv_location* is the location of MPV for *start_mpv*. (Default: Use MPV in PATH)
        *log_handler(level, prefix, text)* is an optional handler for log events. (Default: Disabled)
        *loglevel* is the level for log messages. Levels are fatal, error, warn, info, v, debug, trace. (Default: Disabled)
        *quit_callback* is called when the socket connection to MPV dies.

        All other arguments are forwarded to MPV as command-line arguments if *start_mpv* is used.
        """
        self.properties = {}
        self.event_bindings = {}
        self.key_bindings = {}
        self.property_bindings = {}
        self.mpv_process = None
        self.mpv_inter = None
        self.quit_callback = quit_callback
        self.event_handler = EventHandler()
        self.event_handler.start()
        if ipc_socket is None:
            rand_file = "mpv{0}".format(random.randint(0, 2**48))
            if os.name == "nt":
                ipc_socket = rand_file
            else:
                ipc_socket = "/tmp/{0}".format(rand_file)

        if start_mpv:
            # Attempt to start MPV 3 times.
            for i in range(3):
                try:
                    self.mpv_process = MPVProcess(ipc_socket, mpv_location, **kwargs)
                    break
                except MPVError:
                    log.warning("MPV start failed.", exc_info=1)
                    continue
            else:
                raise MPVError("MPV process retry limit reached.")

        self.mpv_inter = MPVInter(ipc_socket, self._callback, self._quit_callback)
        self.properties = set(x.replace("-", "_") for x in self.command("get_property", "property-list"))
        try:
            command_list = [x["name"] for x in self.command("get_property", "command-list")]
        except MPVError:
            log.warning("Using fallback command list.")
            command_list = FALLBACK_COMMAND_LIST
        for command in command_list:
            object.__setattr__(self, command.replace("-", "_"), self._get_wrapper(command))

        self._dir = list(self.properties)
        self._dir.extend(object.__dir__(self))

        self.observer_id = 1
        self.observer_lock = threading.Lock()
        self.keybind_id = 1
        self.keybind_lock = threading.Lock()
        
        if log_handler is not None and loglevel is not None:
            self.command("request_log_messages", loglevel)
            @self.on_event("log-message")
            def log_handler_event(data):
                self.event_handler.put_task(log_handler, data["level"], data["prefix"], data["text"].strip())

        @self.on_event("property-change")
        def event_handler(data):
            if data.get("id") in self.property_bindings:
                self.event_handler.put_task(self.property_bindings[data["id"]], data["name"], data.get("data"))

        @self.on_event("client-message")
        def client_message_handler(data):
            args = data["args"]
            if len(args) == 2 and args[0] == "custom-bind":
                self.event_handler.put_task(self.key_bindings[args[1]])

    def _quit_callback(self):
        """
        Internal handler for quit events.
        """
        if self.quit_callback:
            self.quit_callback()
        self.terminate(join=False)

    def bind_event(self, name, callback):
        """
        Bind a callback to an MPV event.

        *name* is the MPV event name.
        *callback(event_data)* is the function to call.
        """
        if name not in self.event_bindings:
            self.event_bindings[name] = set()
        self.event_bindings[name].add(callback)

    def on_event(self, name):
        """
        Decorator to bind a callback to an MPV event.

        @on_event(name)
        def my_callback(event_data):
            pass
        """
        def wrapper(func):
            self.bind_event(name, func)
            return func
        return wrapper

    # Added for compatibility.
    def event_callback(self, name):
        """An alias for on_event to maintain compatibility with python-mpv."""
        return self.on_event(name)

    def on_key_press(self, name):
        """
        Decorator to bind a callback to an MPV keypress event.

        @on_key_press(key_name)
        def my_callback():
            pass
        """
        def wrapper(func):
            self.bind_key_press(name, func)
            return func
        return wrapper

    def bind_key_press(self, name, callback):
        """
        Bind a callback to an MPV keypress event.

        *name* is the key symbol.
        *callback()* is the function to call.
        """
        self.keybind_lock.acquire()
        keybind_id = self.keybind_id
        self.keybind_id += 1
        self.keybind_lock.release()

        bind_name = "bind{0}".format(keybind_id)
        self.key_bindings["bind{0}".format(keybind_id)] = callback
        try:
            self.keybind(name, "script-message custom-bind {0}".format(bind_name))
        except MPVError:
            self.define_section(bind_name, "{0} script-message custom-bind {1}".format(name, bind_name))
            self.enable_section(bind_name)

    def bind_property_observer(self, name, callback):
        """
        Bind a callback to an MPV property change.

        *name* is the property name.
        *callback(name, data)* is the function to call.

        Returns a unique observer ID needed to destroy the observer.
        """
        self.observer_lock.acquire()
        observer_id = self.observer_id
        self.observer_id += 1
        self.observer_lock.release()

        self.property_bindings[observer_id] = callback
        self.command("observe_property", observer_id, name)
        return observer_id

    def unbind_property_observer(self, observer_id):
        """
        Remove callback to an MPV property change.

        *observer_id* is the id returned by bind_property_observer.
        """
        self.command("unobserve_property", observer_id)
        del self.property_bindings[observer_id]

    def property_observer(self, name):
        """
        Decorator to bind a callback to an MPV property change.

        @property_observer(property_name)
        def my_callback(name, data):
            pass
        """
        def wrapper(func):
            self.bind_property_observer(name, func)
            return func
        return wrapper
    
    def wait_for_property(self, name):
        """
        Waits for the value of a property to change.

        *name* is the name of the property.
        """
        event = threading.Event()
        first_event = True
        def handler(*_):
            nonlocal first_event
            if first_event == True:
                first_event = False
            else:
                event.set()
        observer_id = self.bind_property_observer(name, handler)
        event.wait()
        self.unbind_property_observer(observer_id)

    def _get_wrapper(self, name):
        def wrapper(*args):
            return self.command(name, *args)
        return wrapper

    def _callback(self, event, data):
        if event in self.event_bindings:
            for callback in self.event_bindings[event]:
                self.event_handler.put_task(callback, data)

    def play(self, url):
        """Play the specified URL. An alias to loadfile()."""
        self.loadfile(url)

    def __del__(self):
        self.terminate()

    def terminate(self, join=True):
        """Terminate the connection to MPV and process (if *start_mpv* is used)."""
        if self.mpv_process:
            self.mpv_process.stop()
        if self.mpv_inter:
            self.mpv_inter.stop(join)
        self.event_handler.stop(join)

    def command(self, command, *args):
        """
        Send a command to MPV. All commands are bound to the class by default,
        except JSON IPC specific commands. This may also be useful to retain
        compatibility with python-mpv, as it does not bind all of the commands. 

        *command* is the command name.

        All further arguments are forwarded to the MPV command. 
        """
        return self.mpv_inter.command(command, *args)

    def __getattr__(self, name):
        if name in self.properties:
            return self.command("get_property", name.replace("_", "-"))
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name not in {"properties", "command"} and name in self.properties:
            return self.command("set_property", name.replace("_", "-"), value)
        return object.__setattr__(self, name, value)

    def __hasattr__(self, name):
        if object.__hasattr__(self, name):
            return True
        else:
            try:
                getattr(self, name)
                return True
            except MPVError:
                return False

    def __dir__(self):
        return self._dir

###python-mpv-module####
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################


def time_in_seconds(time):
    global ankivideo
    h, m, s, ms = map(int, time.split('.'))
    total_seconds = (h * 3600) + (m * 60) + s
    return "{}.{}".format(total_seconds, ms)
def stoopu(when):
    mpv = MPV(start_mpv=False, ipc_socket=os.path.abspath("/tmp/mpv-socket"))
    while pao:
        position=str(mpv.command("get_property", "time-pos"))
        if float(position) >= float(when):
            mpv.command("set_property", "pause", True)
            break
        time.sleep(0.2)
    mpv.terminate()

global process2
global pao
pao = True
process2 = True
def mpvankii(v1, v2, v3, v4, v5, v6):
    global ankivideo
    mpv = MPV(start_mpv=False, ipc_socket=os.path.abspath("/tmp/mpv-socket"))
    if not v5:
        v5=0
    if not v6:
        v6=0

    file=os.path.abspath(os.path.join(script_dir, "mpvanki.log"))
    file2=os.path.abspath(os.path.join(script_dir, "savedata", os.path.basename(v1) + "mpvanki.log"))

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
    except:
        with open(file, 'w') as f:
                f.write(f"{v1} {START} {END} {number}")
                f.close()

    if v5 == "yes":
        try:
            with open(file2, "r") as f:
                line = f.readline().strip()
            if line:
                var5 = float(line.split()[0])
            else:
                var5 = float(0)
        except:
            var5 = float(0)

    if not os.path.exists(file):
        with open(file, 'w') as f:
                f.write(f"{v1} {START} {END} {number}")
                f.close()



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

    if v5 == "yes":
        with open(file2, 'w') as f:
                f.write(f"{END}")
                f.close()


    global process2
    global pao
    try:
        if process2 != 1:
            pao = False
            process2.join()
    except:
        pass
    try:
        process = Thread(target=stoopu, args=(str(END),))
        pao = True
        process2 = process
        process.start()
    except:
        pass







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
        dueToday()  # formeeeeeeeeeee
#        if num == 1:
#            os.system("mpvanki " + command + " e &")
#        else:
        global mpv
        try:
            mpv = MPV(start_mpv=False, ipc_socket=os.path.abspath("/tmp/mpv-socket"))
            mpv.command("get_property", "stream-pos")
        except:
            mpv = MPV(start_mpv=True, ipc_socket=os.path.abspath("/tmp/mpv-socket"))

        mpvankii( note["mpvanki-filename"], note["mpvanki-start"], note["mpvanki-end"], note["mpvanki-number"], new, sub)



def ansae(ansa):
    card = mw.reviewer.card
    mw.col.sched.answerCard(card, ansa)
    mw.reviewer.nextCard()





from aqt.utils import tooltip
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
    if time_string == "mpvanki-start":
        tooltip("-500ms →-----")
    if time_string == "mpvanki-end":
        tooltip("+500ms -----→")
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
    if time_string == "mpvanki-start":
        tooltip("+500ms ←-----")
    if time_string == "mpvanki-end":
        tooltip("-500ms -----←")
    run_command_field()



def _addShortcuts(shortcuts):
    """Add shortcuts on Anki 2.1.x"""
    additions = (
        (SHORTCUT_INCREMENTAL, lambda: run_command_field(1)),
        (SHORTCUT_START1, lambda: remove_time("mpvanki-start")),
        (SHORTCUT_START2, lambda: add_time("mpvanki-start")),
        (SHORTCUT_END1, lambda: remove_time("mpvanki-end")),
        (SHORTCUT_END2, lambda: add_time("mpvanki-end")),
        (ANSWER, lambda: ansae(ansa)),
        (HALFSHOW, lambda: run_command_field()),
        (GOBACK, lambda: mw.form.actionUndo.trigger()),
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
    addHook("showAnswer", run_command_field)
