import argparse
from bs4 import BeautifulSoup
import getpass
import mechanize
import sys

kUsernameControlName = "login"
kPasswordControlName = "pass"

def parseInputsForPostRequest(iDom):
    requiredInputList = []
    for inputName in ["wifi_random", "wifi_disable_radio", "wifi_active",
                      "wifi_ssid", "wifi_channel_auto", "wifi_channel", 
                      "wifi_ssid_hide", "wifi_key_type", "wifi_key", "action", "tpl"]:
        inputValue = getValueForElement("input", inputName, iDom)
        requiredInputList.append(inputName + ":" + inputValue)
    return requiredInputList

def getLoginData():
    kUsageString = "Usage: " + sys.argv[0] + " username"
    if len(sys.argv) != 2:
        print "Wrong number of arguments"
        print kUsageString
        sys.exit(1)
    username = sys.argv[1]
    password = getpass.getpass()
    return username, password

def getValueForElement(iElementType, iElementName, iDom):
    searchedElement = iDom.find(iElementType, {"name": iElementName})
    assert searchedElement is not None
    return searchedElement["value"]

def isSuccessfulLogin(iLoginResponseStr):
    # In case of failure in the login phase, a div with class loginalert is available
    responseDom = BeautifulSoup(iLoginResponseStr)
    loginAlertDiv = responseDom.find("div", attrs={"class": "loginalert"})
    return True if loginAlertDiv is None else False

def parseCommandLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', help='enable the Wifi module')

def main():
    parseCommandLineArgs()
    username, password = getLoginData()
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    kLoginPage = "https://subscribe.free.fr/login/login.pl"
    loginPageRequest = browser.open(kLoginPage)
    # The page usually has only one unnamed form, the login one
    browser.select_form(nr = 0)
    browser.form[kUsernameControlName] = username
    browser.form[kPasswordControlName] = password
    loginResponse = browser.submit()
    if isSuccessfulLogin(loginResponse.read()):
        wifiPageResponse = browser.follow_link(text_regex=r"Param\xe9trer mon r\xe9seau WiFi")
        wifiDom = BeautifulSoup(wifiPageResponse.read())
        print parseInputsForPostRequest(wifiDom)
        


if __name__ == '__main__':
    main()
