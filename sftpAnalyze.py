#!/usr/bin/python3

import sys, re, curses, datetime
from curses import wrapper
from curses.textpad import Textbox, rectangle

USER_MODE = 0
SESSION_MODE = 1
ENTRY_MODE = 3
ACTION_LOGIN = 0
ACTION_READ = 1
ACTION_WRITE = 2
ACTION_OPENDIR = 3
ACTION_CLOSEDIR = 4
ACTION_LOGOUT = 5
ACTION_OPEN = 6
ACTION_CLOSE = 7
ACTION_DELETE = 8

ACTION_CLOSE_PATH = 1
ACTION_CLOSE_BYTESREAD = 2
ACTION_CLOSE_BYTESWRITTEN = 3

extractIP = re.compile("from \[(.*?)]")
extractPath = re.compile("\"(.*?)\"")
closeParse = re.compile("close \"(.*?)\" bytes read (.*?).written (.*?)$")
deleteParse = re.compile("remove name \"(.*?)\"")

class Entry:
    def __init__(self, unparsed):
        self.unparsed = unparsed
        self.sessionID = unparsed.split("[")[1].split("]")[0]
        if "session opened for local user" in unparsed:
            self.username = unparsed.split(" ")[10]
            self.action = ACTION_LOGIN
        else:
            self.username = "notalogin"
            self.action = ACTION_READ #doesn't matter which action goes here as long as it isn't ACTION_LOGIN
        words = self.unparsed.split(" ")
        self.timestamp = words[0] + " " + words[1] + " " + words[2]
        if self.action != ACTION_LOGIN:
            if words[5] == "opendir":
                self.action = ACTION_OPENDIR
            elif words[5] == "closedir":
                self.action = ACTION_CLOSEDIR
            elif "session closed for local user" in unparsed:
                self.action = ACTION_LOGOUT
            elif closeParse.search(self.unparsed) != None:
                self.action = ACTION_CLOSE
            elif deleteParse.search(self.unparsed) != None:
                self.action = ACTION_DELETE
            else:
                self.action = ACTION_READ

class User:
    def __init__(self, username):
        self.sessions = []
        self.username = username

class Session:
    uuid = 0
    def __init__(self, id):
        self.uuid = Session.uuid
        Session.uuid = Session.uuid + 1
        self.id = id
        self.entries = []
        self.address = ''
        self.username = ''
        self.user = ''

def concat(*args):
    tout = str(args[0])
    for arg in args[1:]:
        tout = tout + " " + str(arg)
    return tout;

def isaNumber(string):
    try:
        int(string)
    except:
        return False
    return True

def duplist(list):
    temparray = []
    for i in list:
        temparray.append(i)
    return temparray

def surround(outside, *strings):
    tout = outside
    for string in strings:
        tout = tout + string
    return tout + outside

def interpret(entry):
    if type(entry) == type(str()):
        return entry
    if entry.action == ACTION_LOGIN:
        return concat(entry.timestamp, "-", "User", entry.username, "logged in")
    elif entry.action == ACTION_LOGOUT:
        return concat(entry.timestamp, '-', "User logged out")
    elif entry.action == ACTION_OPENDIR:
        return concat(entry.timestamp, '-', 'Opened directory', surround('"', extractPath.search(entry.unparsed).group(1)))
    elif entry.action == ACTION_CLOSEDIR:
        return concat(entry.timestamp, '-', 'Closed directory', surround('"', extractPath.search(entry.unparsed).group(1)))
    elif entry.action == ACTION_CLOSE:
        match = closeParse.search(entry.unparsed)
        return concat(entry.timestamp, '-', 'Closed file', surround('"', match.group(ACTION_CLOSE_PATH)), 'Read', match.group(ACTION_CLOSE_BYTESREAD), 'bytes | Wrote', match.group(ACTION_CLOSE_BYTESWRITTEN), 'bytes')
    elif entry.action == ACTION_DELETE:
        match = deleteParse.search(entry.unparsed)
        return concat(entry.timestamp, '-', 'Deleted file', surround('"', match.group(1)))
    else:
        return entry.unparsed #catch any unimplemented cases and print the raw entry

def main(screen):
    users = []
    usernames = []
    sessions = []
    entries = []

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
            entries.append(Entry(line))
        screen.addstr(1, 0, concat("processing log entries...", workingline, "/", len(logs), "     found", len(entries), "sftp entries"))
        screen.refresh()

    datesplitted = entries[0].timestamp.split(" ")
    timesplitted = datesplitted[2].split(":")
    firstdate = datetime.datetime(datetime.datetime.today().year, datetime.datetime.strptime(datesplitted[0], '%b').month, int(datesplitted[1]), hour=int(timesplitted[0]), minute=int(timesplitted[1]), second=int(timesplitted[2]))

    datesplitted = entries[-1].timestamp.split(" ")
    timesplitted = datesplitted[2].split(":")
    lastdate = datetime.datetime(datetime.datetime.today().year, datetime.datetime.strptime(datesplitted[0], '%b').month, int(datesplitted[1]), hour=int(timesplitted[0]), minute=int(timesplitted[1]), second=int(timesplitted[2]))

    #if firstdate.timestamp() > lastdate.timestamp():
    #   entrys.reverse()
    #TODO - why does this cause doubling ^ ?

    workingline = 0
    screen.addstr("\nanalyzing valid entries")
    screen.refresh()
    for entry in entries:
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
    for entry in entries:
        workingline = workingline + 1
        screen.addstr(4, 0, concat("populating sessions...", workingline, "/", len(entries)))
        screen.refresh()
        for session in sessions:
            if entry.sessionID == session.id:
                session.entries.append(entry)
    workingline = 0
    for user in users:
        workingline = workingline + 1
        screen.addstr(5, 0, concat("attributing sessions to users", workingline, '/', len(users)))
        screen.refresh()
        if user.username != "notalogin":
            for session in sessions:
                if session.username == user.username:
                    notinsessions = True
                    for i in user.sessions:
                        if i.uuid == session.uuid:
                            notinsessions = False
                    if notinsessions:
                        user.sessions.append(session)

    screen.addstr(7, 0, "Analysis Complete")
    screen.addstr(8, 0, "PRESS ENTER TO CONTINUE")
    screen.getstr()

    screen.nodelay(1)
    screen.clear()
    screen.refresh()

    leftpanel = curses.newwin(screen.getmaxyx()[0], 56, 0, 0)
    rightpanel = curses.newwin(screen.getmaxyx()[0], screen.getmaxyx()[1] - 56, 0, 56)

    screensize = screen.getmaxyx()

    curses.curs_set(0)
    curses.start_color()

    menuindex = 0
    viewmode = USER_MODE
    left_scrollpoint = 0

    while True:
        if screensize != screen.getmaxyx():
            screensize = screen.getmaxyx()
            leftpanel = curses.newwin(screen.getmaxyx()[0], 56, 0, 0)
            rightpanel = curses.newwin(screen.getmaxyx()[0], screen.getmaxyx()[1] - 56, 0, 56)
        if viewmode == USER_MODE:
            leftpanel.addstr(0, 0, concat("Users:","(" + str(len(users)) + ")"))
            rightpanel.addstr(0, 0, concat("Sessions: ", "(" + str(len(users[menuindex].sessions)) + " sessions)"))
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
                    rightpanel.addstr(lineindex, 2, concat(session.entries[0].timestamp, "from", "[" + session.address + "]", "--- ID", session.id))
                except curses.error:
                    pass    

            try:
                char = screen.getkey()
                if char == "KEY_UP":
                    if menuindex > 0:
                        menuindex = menuindex - 1
                        leftpanel.clear()
                        rightpanel.clear()
                elif char == "KEY_DOWN":
                    if menuindex < len(users) - 1:
                        menuindex = menuindex + 1
                        leftpanel.clear()
                        rightpanel.clear()
                elif char == "KEY_RIGHT":
                    menuindex = 0
                    viewmode = SESSION_MODE
                    leftpanel.clear()
                    rightpanel.clear()
                elif char.lower() == 'q':
                    exit()
            except curses.error:
                pass

        elif viewmode == SESSION_MODE or ENTRY_MODE:
            if viewmode == SESSION_MODE:
                right_scrollpoint = 0
            selsession = seluser.sessions[menuindex]
            leftpanel.addstr(0, 0, concat("Sessions for user", seluser.username + ":", "(" + str(len(seluser.sessions)) + " sessions)"))
            rightpanel.addstr(0, 0, concat(len(seluser.sessions), "entries in session", selsession.id))
            for i in range(screen.getmaxyx()[0] - 1):
                leftpanel.addstr(i, leftpanel.getmaxyx()[1] - 1, "|")
                if viewmode == ENTRY_MODE:
                    leftpanel.addstr(i, leftpanel.getmaxyx()[1] - 2, ">")
            lineindex = 1
            for session in seluser.sessions:
                lineindex = lineindex + 1
                try:
                    leftpanel.addstr(lineindex, 2, concat(session.entries[0].timestamp, "from", "[" + session.address + "]", "--- ID", session.id))
                    if session.uuid == selsession.uuid:
                        leftpanel.addstr(lineindex, 1, ">")
                except curses.error:
                    pass
            
            rightpanel.move(1, 2)
            entries = ["-------LOGS END-------"] + duplist(selsession.entries) + ["-------LOGS START-------"]
            entries.reverse()
            for entry in entries[right_scrollpoint:]:
                try:
                    rightpanel.addstr("\n" + interpret(entry))
                except curses.error:
                    pass

            try:
                char = screen.getkey()
                if char == "KEY_UP":
                    if viewmode == SESSION_MODE:
                        if menuindex > 0:
                            menuindex = menuindex - 1
                            leftpanel.clear()
                            rightpanel.clear()
                    elif right_scrollpoint != 0:
                        right_scrollpoint = right_scrollpoint - 1
                        rightpanel.clear()
                elif char == "KEY_DOWN":
                    if viewmode == SESSION_MODE:
                        if menuindex < len(seluser.sessions) - 1:
                            menuindex = menuindex + 1
                            leftpanel.clear()
                            rightpanel.clear()
                    elif right_scrollpoint < len(entries) - 1:
                        right_scrollpoint = right_scrollpoint + 1
                        rightpanel.clear()
                elif char == "KEY_LEFT":
                    if viewmode == SESSION_MODE:
                        leftpanel.clear()
                        rightpanel.clear()
                        viewmode = USER_MODE
                        menuindex = 0
                    else:
                        viewmode = SESSION_MODE
                        leftpanel.clear()
                        rightpanel.clear()
                elif char == "KEY_RIGHT":
                    viewmode = ENTRY_MODE
                elif char.lower() == 'q':
                    exit()
            except curses.error:
                pass

        leftpanel.refresh()
        rightpanel.refresh()
        
wrapper(main)
