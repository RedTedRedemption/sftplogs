#!/usr/bin/python3

import sys, re, curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

extractIP = re.compile("from \[(.*?)]")

class Entry:
    def __init__(self, unparsed):
        self.unparsed = unparsed
        self.sessionID = unparsed.split("[")[1].split("]")[0]
        if "session opened for local user" in unparsed:
            self.username = unparsed.split(" ")[10]
        else:
            self.username = "notalogin"
        words = self.unparsed.split(" ")
        self.timestamp = words[0] + " " + words[1] + " " + words[2]
        self.action = words[5:]

entrys = []

class User:
    def __init__(self, username):
        self.sessions = []
        self.username = username
    
def concat(*args):
    tout = str(args[0])
    for arg in args[1:]:
        tout = tout + " " + str(arg)
    return tout;

users = []
usernames = []
sessions = []
sessionnames = []

def isaNumber(string):
    try:
        int(string)
    except:
        return False
    return True

class Session:
    def __init__(self, id):
        self.id = id
        self.entrys = []
        self.address = ''
def main(screen):
    screen.clear()
    if len(sys.argv) < 2:
        targetWin = curses.newwin(1, screen.getmaxyx()[1], int(screen.getmaxyx()[0] / 2), 0)
        screen.addstr(int(screen.getmaxyx()[0] / 2) - 1, 0, "enter file to analyze: ")
        screen.refresh()
        editbox = Textbox(targetWin)
        targetWin.refresh()
        editbox.edit()
        targetfile = editbox.gather().strip()
        targetWin.clear()
        targetWin.refresh()
        
    else:
        targetfile = sys.argv[1]
    screen.clear()
    screen.addstr("analyzing file: " + targetfile)
    screen.refresh()

    try:
        logfile = open(targetfile, "r")
        logfile = logfile.read()
    except IOError as err:
        print(targetfile)
        screen.clear()
        screen.addstr(concat("error loading file:"), err) #TODO - make more graceful
        screen.getkey()
        exit()

    logs = logfile.split("\n")
    workingline = 0


    for line in logs:
        workingline = workingline + 1
        if "sftp-server[" in line:
            entrys.append(Entry(line))
        screen.addstr(1, 0, concat("processing log entries...", workingline, "/", len(logs), "     found", len(entrys), "sftp entries"))
        screen.refresh()

    workingline = 0
    screen.addstr("\nanalyzing valid entries")
    screen.refresh()
    for entry in entrys:
        workingline = workingline + 1
        screen.addstr(3, 0, concat("analyzing line: ", workingline, "/", len(logs), "   ", "users detected: ", len(users), "    ", "sessions:", len(sessions)))
        screen.refresh()
        if entry.username not in usernames:
            if entry.username != "notalogin":
                usernames.append(entry.username)
                users.append(User(entry.username))

        if "session opened for" in entry.unparsed:
            tempsession = Session(entry.sessionID)
            tempsession.address = extractIP.search(entry.unparsed).group(1)
            sessions.append(tempsession)
            for user in users:
                if user.username == entry.username:
                    user.sessions.append(tempsession)

    workingline = 0
    for entry in entrys:
        workingline = workingline + 1
        screen.addstr(4, 0, concat("populating sessions...", workingline, "/", len(entrys)))
        screen.refresh()
        for session in sessions:
            if entry.sessionID == session.id:
                session.entrys.append(entry)
    workingline = 0
    for user in users:
        workingline = workingline + 1
        screen.addstr(5, 0, concat("attributing sessions to users", workingline, '/', len(users)))
        screen.refresh()
        if user.username != "notalogin":
            for session in sessions:
                if session.entrys[0].username == user.username:
                    user.sessions.append(session)

    screen.getkey()

    while True:
        try:
            count = 0
            print()
            print("---------------------------")
            print("Select a user:")
            for user in users:
                print(str(count) + ". " + user.username, "-", len(user.sessions), 'sessions')
                count = count + 1
            while True:
                menusel = input("> ")
                if "exit" in menusel.lower():
                    exit()
                if not isaNumber(menusel):
                    print(menusel + " is not a number")
                elif int(menusel) >= len(users):
                    print(menusel + " is not in range")
                else:
                    user = users[int(menusel)]
                    break
            print("please select a session for " + user.username + " or 'back' to go back")
            
            while True:
                count = 0
                for session in user.sessions:
                    if count < 10:
                        print(str(count) + ".  " + str(session.id) + " at " + str(session.entrys[0].timestamp) + " with " + str(len(session.entrys)) + " entrys from", "[" + session.address + "]")
                    else:
                        print(str(count) + ". " + str(session.id) + " at " + str(session.entrys[0].timestamp) + " with " + str(len(session.entrys)) + " entrys from", "[" + session.address + "]")
                    count = count + 1
                print ("select a session by number or enter 'back' to return to the previous menu")
                menusel = input("> ").lower()
                if "back" in menusel:
                    break
                if "exit" in menusel:
                    exit()
                if not isaNumber(menusel):
                    print(menusel + " is not a number")
                elif int(menusel) >= len(user.sessions):
                    print(menusel + " is not in range")
                else:
                    session = user.sessions[int(menusel)]
                    print("-----------------------------------------")
                    entries = session.entrys[:]
                    entries.reverse()
                    for entry in entries:
                        print(entry.unparsed)
                    print("-----------------------------------------")
                    input("press enter to return to sessions for user " + user.username)
                    print("-----")
        except KeyboardInterrupt:
            print()
            print("exiting by keyboard interrupt")
            exit()
    
wrapper(main)
           
        
