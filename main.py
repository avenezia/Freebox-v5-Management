import argparse
from bs4 import BeautifulSoup
import getpass
import mechanize
import sys

kUsernameControlName = "login"
kPasswordControlName = "pass"

# Python 2.x doesn't offer Enums. Creating enum type using type method
# https://docs.python.org/2/library/functions.html#type
def enum(**enums):
    return type('Enum', (), enums)

WifiModuleAction = enum(ON = 1, OFF = 2, SWITCH = 3)

def changeWiFiModuleState(iDom, iAction):
    wifiModuleStateElement = getElementByName("input", "wifi_disable_radio", iDom)
    assert wifiModuleStateElement
    if iAction == WifiModuleAction.ON:
        if isWifiModuleActive(wifiModuleStateElement):
            print "Nothing to do, WiFi module is already ON"
        else:
            turnOnWiFiModule(wifiModuleStateElement)
    elif iAction == WifiModuleAction.OFF:
        if isWifiModuleActive(wifiModuleStateElement):
            turnOffWiFiModule(wifiModuleStateElement)
        else:
            print "Nothing to do, WiFi module is already OFF"
    elif iAction == WifiModuleAction.SWITCH:
        switchWiFiModule(wifiModuleStateElement)
    else:
        raise Exception("Unknown action for WiFi module")

def getElementByName(iElementType, iElementName, iDom):
    searchedElement = iDom.find(iElementType, {"name": iElementName})
    assert searchedElement is not None
    return searchedElement

def getLoginData():
    kUsageString = "Usage: " + sys.argv[0] + " username"
    if len(sys.argv) != 2:
        print "Wrong number of arguments"
        print kUsageString
        sys.exit(1)
    username = sys.argv[1]
    password = getpass.getpass()
    return username, password

def isSuccessfulLogin(iLoginResponseStr):
    # In case of failure in the login phase, a div with class loginalert is available
    responseDom = BeautifulSoup(iLoginResponseStr)
    loginAlertDiv = responseDom.find("div", attrs={"class": "loginalert"})
    return True if loginAlertDiv is None else False

def isWifiModuleActiveOld(iDom):
    # The wifi module is controlled by <input name="wifi_disable_radio" type="hidden" value="0">
    return getElementByName("input", "wifi_disable_radio", iDom)["value"] == "0"

def isWifiModuleActive(iWiFiStateElement):
    assert iWiFiStateElement
    # The wifi module is controlled by <input name="wifi_disable_radio" type="hidden" value="0">
    return iWiFiStateElement["value"] == "0"

def parseCommandLineArgs():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", help="Enable the WiFi module", action="store_true")
    group.add_argument("-d", help="Disable the WiFi module",  action="store_true")
    group.add_argument("-t", help="Switch the status of the WiFi module",  action="store_true")
    parser.add_argument("-r", help="Reboot the WiFi module to apply the changes", action="store_true")
    parser.add_argument("username", type=str, help="The username to login on Free site")
    parser.parse_args()

def parseInputsForPostRequest(iDom):
    requiredInputList = []
    for inputName in ["wifi_random", "wifi_disable_radio", "wifi_active",
                      "wifi_ssid", "wifi_channel_auto", "wifi_channel", 
                      "wifi_ssid_hide", "wifi_key_type", "wifi_key", "action", "tpl"]:
        inputValue = getElementByName("input", inputName, iDom)["value"]
        requiredInputList.append(inputName + ":" + inputValue)
    return requiredInputList

def switchWiFiModule(iWiFiStateElement):
    assert iWiFiStateElement
    aElementValue = iWiFiStateElement["value"]
    assert aElementValue == "0" or aElementValue == "1"
    logMessage = "Switching from "
    logMessage += "ON to OFF" if isWifiModuleActive(iWiFiStateElement) else "OFF to ON"
    print logMessage
    iWiFiStateElement["value"] = "1" if aElementValue == "0" else "0"

def turnOffWiFiModule(iWiFiStateElement):
    assert iWiFiStateElement
    print "Turning OFF WiFi module"
    iWiFiStateElement["value"] = "1"

def turnOnWiFiModule(iWiFiStateElement):
    assert iWiFiStateElement
    print "Turning ON WiFi module"
    iWiFiStateElement["value"] = "0"

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
        print isWifiModuleActiveOld(wifiDom)

if __name__ == '__main__':
    main()
