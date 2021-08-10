#!/usr/bin/python3

import sys, re, curses, datetime
from curses import wrapper
from curses.textpad import Textbox, rectangle

USER_MODE = 0
SESSION_MODE = 1
ENTRY_MODE = 3

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

class User:
    def __init__(self, username):
        self.sessions = []
        self.username = username

class Session:
    def __init__(self, id):
        self.id = id
        self.entrys = []
        self.address = ''
        self.username = ''
        self.user = '' #TEMPORARY ASSIGNMENT - var is changed later

def concat(*args):
    tout = str(args[0])
    for arg in args[1:]:
        tout = tout + " " + str(arg)
    return tout;

users = []
usernames = []
sessions = []
entrys = []

def isaNumber(string):
    try:
        int(string)
    except:
        return False
    return True




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

    datesplitted = entrys[0].timestamp.split(" ")
    timesplitted = datesplitted[2].split(":")
    firstdate = datetime.datetime(datetime.datetime.today().year, datetime.datetime.strptime(datesplitted[0], '%b').month, int(datesplitted[1]), hour=int(timesplitted[0]), minute=int(timesplitted[1]), second=int(timesplitted[2]))

    datesplitted = entrys[-1].timestamp.split(" ")
    timesplitted = datesplitted[2].split(":")
    lastdate = datetime.datetime(datetime.datetime.today().year, datetime.datetime.strptime(datesplitted[0], '%b').month, int(datesplitted[1]), hour=int(timesplitted[0]), minute=int(timesplitted[1]), second=int(timesplitted[2]))

    #if firstdate.timestamp() > lastdate.timestamp():
    #   entrys.reverse()
    #TODO - why does this cause doubling ^ ?


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
            tempsession.username = entry.username
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
                if session.username == user.username:
                    user.sessions.append(session)

    screen.nodelay(1)
    screen.clear()
    screen.refresh()

    leftpanel = curses.newwin(screen.getmaxyx()[0], int(screen.getmaxyx()[1] / 2), 0, 0)
    rightpanel = curses.newwin(screen.getmaxyx()[0], int(screen.getmaxyx()[1] / 2), 0, int(screen.getmaxyx()[1] / 2))



    menuindex = 0

    

    curses.curs_set(0)

    curses.start_color()

    viewmode = USER_MODE

    while True:
        if viewmode == USER_MODE:
            leftpanel.addstr(0, 0, "Users:")
            rightpanel.addstr(0, 0, concat("Sessions: ", "(" + str(len(users[menuindex].sessions)) + ")"))
            for i in range(screen.getmaxyx()[0] - 1):
                leftpanel.addstr(i, leftpanel.getmaxyx()[1] - 1, "|")
            lineindex = 1
            for user in users:
                lineindex = lineindex + 1
                leftpanel.addstr(lineindex, 2, user.username)
            leftpanel.addstr(menuindex + 2, 1, ">")
            
            lineindex = 1
            seluser = users[menuindex]
            for session in seluser.sessions:
                lineindex = lineindex + 1
                try:
                    rightpanel.addstr(lineindex, 2, concat(session.entrys[0].timestamp, "from", "[" + session.address + "]"))
                except curses.error:
                    pass        

            char = screen.getch()
            leftpanel.addstr(0, 10, str(char))
            if char == curses.KEY_UP:
                if menuindex > 0:
                    menuindex = menuindex - 1
                    leftpanel.clear()
                    rightpanel.clear()
            elif char == curses.KEY_DOWN:
                if menuindex < len(users) - 1:
                    menuindex = menuindex + 1
                    leftpanel.clear()
                    rightpanel.clear()
            elif char == curses.KEY_RIGHT:
                menuindex = 0
                viewmode = SESSION_MODE
                leftpanel.clear()
                rightpanel.clear()

        elif viewmode == SESSION_MODE:
            selsession = sessions[menuindex]
            leftpanel.addstr(0, 0, concat("Sessions: ", "(" + str(len(seluser.sessions)) + ")"))
            for i in range(screen.getmaxyx()[0] - 1):
                leftpanel.addstr(i, leftpanel.getmaxyx()[1] - 1, "|")
            lineindex = 1
            for session in seluser.sessions:
                lineindex = lineindex + 1
                try:
                    leftpanel.addstr(lineindex, 2, concat(session.entrys[0].timestamp, "from", "[" + session.address + "]"))
                except curses.error:
                    pass
            
            lineindex = 1
            for entry in selsession.entrys:
                rightpanel.addstr(lineindex, 2, entry.unparsed)

            leftpanel.addstr(menuindex + 2, 1, ">")


        
                    

            char = screen.getch()
            if char == curses.KEY_UP:
                if menuindex > 0:
                    menuindex = menuindex - 1
                    leftpanel.clear()
                    rightpanel.clear()
            elif char == curses.KEY_DOWN:
                if menuindex < len(seluser.sessions):
                    menuindex = menuindex + 1
                    leftpanel.clear()
                    rightpanel.clear() 
            elif char == curses.KEY_LEFT:
                leftpanel.clear()
                rightpanel.clear()
                viewmode = USER_MODE
                menuindex = 0


        #TODO - add quit by key instead of just kb interrupt


        

        leftpanel.refresh()
        rightpanel.refresh()
        

wrapper(main)
