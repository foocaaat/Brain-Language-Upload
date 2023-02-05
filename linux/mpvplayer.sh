#!/bin/bash

mpv --alang=jpn,kor --idle --slang=en,eng --no-input-cursor --no-input-default-bindings --no-cache --input-ipc-server=/tmp/mpv-socket --no-config --script-opts=osc-timems=yes --keep-open=yes --keep-open-pause=no
