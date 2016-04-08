#!/usr/bin/env python3

# (C) 2016-04-08 Wolfram M. Esser (DerWOK)

import os
import sys
import os.path
from os.path import expanduser
import sys, tty
import termios


CONFIGFILE = expanduser("~")+"/.tailor"
TAILCMD = "tail"
TAILPARAMS = "-F"
HISTORY = []

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


def read_history():
    global HISTORY
    if not os.path.isfile(CONFIGFILE):
        return
    with open(CONFIGFILE) as infile:
        HISTORY = infile.readlines()
    for i in range(0, len(HISTORY)):
        HISTORY[i] = HISTORY[i].rstrip('\n')


def save_history():
    outfile = open(CONFIGFILE, 'w')
    outfile.write("\n".join(HISTORY))
    outfile.close()


def add_to_history(logfile):
    global HISTORY
    print(HISTORY)
    for i in range(len(HISTORY)-1,-1,-1):
        if HISTORY[i] == logfile:
            del HISTORY[i]
            print("DEL:"+str(i+1))
    HISTORY.insert(0, logfile)


def tail_file(logfile):
    add_to_history(logfile)
    save_history()
    # print(TAILCOMMAND+" "+logfile)
    # call([TAILCMD, TAILPARAMS+" "+logfile])
    os.system(TAILCMD+" "+TAILPARAMS+" "+logfile)


#########################################
def mode_history():
    for i in range(0, len(HISTORY)):
        print("["+str(i)+"] "+HISTORY[i])

    while True:
        choice = _getch()
        choice = int(choice)
        if (choice >= 0 and choice < len(HISTORY)):
            logfile = HISTORY[choice]
            tail_file(logfile)
            break


def mode_files():
    logfile = sys.argv[1]
    if os.path.isfile(logfile):
        logfile = os.path.abspath(logfile)
        tail_file(logfile)


# -------- MAIN ---------------
read_history()

if len(sys.argv) == 1:
    mode_history()
    exit (0)

if len(sys.argv) == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
    print("Help!")
    exit(0)

mode_files()
