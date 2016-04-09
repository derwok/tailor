#!/usr/bin/env python3

# (C) 2016-04-08 Wolfram M. Esser (DerWOK)

import os
import sys
import os.path
from os.path import expanduser
import tty
import termios
import shutil

VERSION = "0.1"
CONFIGFILE = expanduser("~")+"/.tailor"
TAILCMD = "tail -F"
KEYS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
HISTORY = []
HISTORYMAX = len(KEYS)


if os.name == "nt":
    print("Sorry, no Win support.")
    exit(1)


def _getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def read_history_from_file():
    global HISTORY
    if not os.path.isfile(CONFIGFILE):
        return
    with open(CONFIGFILE) as infile:
        HISTORY = infile.readlines()
    for i in range(0, len(HISTORY)):
        HISTORY[i] = HISTORY[i].rstrip('\n')


def save_history_to_file():
    outfile = open(CONFIGFILE, 'w')
    outfile.write("\n".join(HISTORY))
    outfile.close()


def add_to_history(logfile):
    global HISTORY
    for i in range(len(HISTORY)-1, -1, -1):   # remove duplicates
        if HISTORY[i] == logfile:
            del HISTORY[i]
            print("DEL:"+str(i+1))
    HISTORY.insert(0, logfile)
    if len(HISTORY) > HISTORYMAX:           # remove last
        HISTORY = HISTORY[0:HISTORYMAX]
    print(HISTORY)
    print(len(HISTORY))


def tail_file(logfile):
    add_to_history(logfile)
    save_history_to_file()
    os.system(TAILCMD+" "+logfile)


#########################################
def mode_help():
    print("Help")
    pass


def mode_history():
    (terminal_col, terminal_lines) = shutil.get_terminal_size(fallback=(80, 25))
    maxlines = min(len(HISTORY), terminal_lines-1)
    if maxlines <= 0:
        print("Error: No files in history yet or your terminal has too few lines.")
        mode_help()
        exit(0)

    for i in range(0, maxlines):      # print numbered menu
        print("["+KEYS[i]+"] "+HISTORY[i])

    while True:                             # read user choice
        choice = _getch()
        if choice == '\x03':                # CTRL+C ^C
            exit(0)
        choiceindex = KEYS.find(choice)
        if 0 <= choiceindex < len(HISTORY):
            logfile = HISTORY[choiceindex]
            tail_file(logfile)
            break


def mode_files():
    logfile = sys.argv[1]
    if os.path.isfile(logfile):
        logfile = os.path.abspath(logfile)
        tail_file(logfile)


# -------- MAIN ---------------
read_history_from_file()

if len(sys.argv) == 1:
    mode_history()
    exit(0)

if len(sys.argv) == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
    mode_help()
    exit(0)

mode_files()
