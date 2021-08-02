#!/usr/bin/python3
import sys, re
if len(sys.argv) < 2:
    targetfile = input("enter file to analyze: ")
else:
    targetfile = sys.argv[1]
print("analyzing file: " + targetfile)

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

extractIP = re.compile("from \[(.*?)]")

entrys = []

class User:
    def __init__(self, username):
        self.sessions = []
        self.username = username

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

try:
    logfile = open(targetfile, "r")
    logfile = logfile.read()
except:
    print("error loading file")
    exit()

logs = logfile.split("\n")
workingline = 0

for line in logs:
    workingline = workingline + 1
    if "sftp-server[" in line:
        entrys.append(Entry(line))
    print("processing log entries...", workingline, "/", len(logs), "     found", len(entrys), "sftp entries", end='\r')

workingline = 0
print()
print("analyzing valid entries")
for entry in entrys:
    workingline = workingline + 1
    print("analyzing line: ", workingline, "/", len(logs), "   ", "users detected: ", len(users), "    ", "sessions:", len(sessions), end="\r")  
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
print()
for entry in entrys:
    workingline = workingline + 1
    print ("populating sessions...", workingline, "/", len(entrys), end='\r')
    for session in sessions:
        if entry.sessionID == session.id:
            session.entrys.append(entry)
workingline = 0
for user in users:
    workingline = workingline + 1
    print("attributing sessions to users", workingline, '/', len(users), end="\r")
    if user.username != "notalogin":
        for session in sessions:
            if session.entrys[0].username == user.username:
                user.sessions.append(session)

while True:
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
            print(str(count) + ". " + str(session.id) + " at " + str(session.entrys[0].timestamp) + " with " + str(len(session.entrys)) + " entrys from", session.address)
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

           
        
