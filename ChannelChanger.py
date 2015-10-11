import random
import re
import requests
import time

remoteControlCodeFile = "remoteControlCode"

def AskRemoteControlCode():
    isValid = False
    code = ""
    while not isValid:
        code = raw_input("Please provide the code of your remote control (8 digits): ")
        isValid = isValidCode(code)
    SaveCode(code)
    return code

def ChangeChannel(iCode):
    basicUrl = "http://hd1.freebox.fr/pub/remote_control?code=" + iCode + "&key="
    directions = ["left", "right"]
    random.seed()
    
    while True:
        time.sleep(10)
        index = random.randint(0, 1)
        # Change channel and come back to it, to watch (mainly hear) pay-per-view channels in the "mosaïque" of the FreeTv:
        # usually you can hear just 10 seconds and then the channel is muted.
        requests.get(basicUrl + directions[index])
        requests.get(basicUrl + directions[(index + 1) % len(directions)])


def GetRemoteControlCode():
    code = ""
    try:
        fileWithCode = open(remoteControlCodeFile,"r")
        code = fileWithCode.read()
        if not isValidCode(code):
            raise Exception("The remote control code is not valid, please modify or delete " + remoteControlCodeFile + " file.")
    except IOError, e:
        code = AskRemoteControlCode()
    return code

def isValidCode(iCode):
    return re.match("^[0-9]{8}$", iCode) is not None

def SaveCode(iCode):
    fileWithCode = open(remoteControlCodeFile, "w")
    fileWithCode.write(iCode)
    fileWithCode.close()

def main():
    code = GetRemoteControlCode()
    ChangeChannel(code)

if __name__ == '__main__':
    main()