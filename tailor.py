#!/usr/bin/env python3

# (C) 2016-04-08 Wolfram M. Esser (DerWOK)

import os
import sys
import os.path
from os.path import expanduser
import tty
import termios
import shutil
import signal
import time

VERSION = "0.4"
CONFIGFILE = expanduser("~")+"/.tailor"
TAILCMD = "tail -F"
KEYS = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
HISTORYMAX = len(KEYS)
HISTORY = []


if os.name == "nt":
    print("Sorry, no Win support.")
    exit(1)


# Read a single key from keyboard
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
    for i in range(len(HISTORY)-1, -1, -1):   # remove old duplicates
        if HISTORY[i] == logfile:
            del HISTORY[i]
    HISTORY.insert(0, logfile)
    if len(HISTORY) > HISTORYMAX:           # shorten list
        HISTORY = HISTORY[0:HISTORYMAX]


def trim_to_col(line, terminal_col):
    choice_width = 4+1        # [x]_ before every line plus 1 space at end
    if len(line)+choice_width < terminal_col:
        return line
    shortened = "..."+line[-(terminal_col-choice_width-3):]
    return shortened


def print_history_menu():
    (terminal_col, terminal_lines) = shutil.get_terminal_size(fallback=(80, 25))
    maxlines = min(len(HISTORY), terminal_lines-1)
    if maxlines <= 0:
        print("Error: No files in history yet or your terminal has too few lines.")
        mode_help()

    for i in range(0, maxlines):      # print numbered menu
        print("["+KEYS[i]+"] "+trim_to_col(HISTORY[i], terminal_col))


# Do actual work of calling TAILCMD
def tail_file(logfile):
    add_to_history(logfile)
    save_history_to_file()
    if os.access(logfile, os.R_OK):
        os.system(TAILCMD+" "+logfile)
    else:
        os.system("sudo "+TAILCMD+" "+logfile)



######################################### WORK MODES #############################
def mode_help():
    print("tailor "+VERSION+" (C) by Wolfram M. Esser (DerWOK)")
    print("Usage: tailor [file]")
    print("If called with file parameter, hands over this file to "+TAILCMD)
    print("If called without file parameter presents a last-recently-used menu.")
    print("Press menu letter to hand over this file to "+TAILCMD)
    print("Press BACKSPACE to toggle delete <=> tail mode")
    print("Press ESC or Ctrl+C to end menu")
    exit(0)


def mode_history_menu():
    print_history_menu()
    # signal.signal(signal.SIGWINCH, handle_terminal_resize)

    delete_mode = False
    currentPrompt = TAILCMD+"..."
    while True:                                     # read user choice
        print("\r"+currentPrompt, end="")
        sys.stdout.flush()
        choice = _getch()
        if choice == '\x03' or choice == '\x1b':                        # CTRL+C ^C  or ESC
            exit(0)

        if choice == '\x7f':                        # Backspace
            print('\x08'*(len(currentPrompt)+1), end="")
            delete_mode = not delete_mode
            if delete_mode:
                currentPrompt = 'Delete... '
            else:
                currentPrompt = TAILCMD+"..."
            continue
        mode_history_no_menu(choice, delete_mode)


def mode_history_no_menu(choice, delete_mode):
    choiceindex = KEYS.find(choice)
    if 0 <= choiceindex < len(HISTORY):
        logfile = HISTORY[choiceindex]
        print(">>> "+logfile)
        print("\n")
        if delete_mode:
            del HISTORY[choiceindex]
            save_history_to_file()
            print_history_menu()
        else:
            tail_file(logfile)
            exit(0)


def mode_new_file():
    logfile = sys.argv[1]
    if os.path.isfile(logfile):
        logfile = os.path.abspath(logfile)
        tail_file(logfile)
    else:
        print("File not found: "+logfile)
    exit(0)


############### SIGNAL HANDLERS ######################
# def handle_terminal_resize(param1, param2):
#     (terminal_col, terminal_lines) = shutil.get_terminal_size(fallback=(80, 25))
#     maxlines = min(len(HISTORY), terminal_lines-1)
#     print_history_menu(maxlines, terminal_col)


# -------- MAIN ---------------
read_history_from_file()

if len(sys.argv) == 1:  # no command line param
    mode_history_menu()

if len(sys.argv) == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
    mode_help()

if len(sys.argv) == 2 and (len(sys.argv[1]) == 1):      # one commandline param, exactly one char.
    mode_history_no_menu(sys.argv[1], False)    # exits, if valid index, drops to next command if not

mode_new_file()
