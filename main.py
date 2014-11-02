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

def isWifiModuleActive(iDom):
    # The wifi module is controlled by <input name="wifi_disable_radio" type="hidden" value="0">
    return getValueForElement("input", "wifi_disable_radio", iDom) == "0"

def parseCommandLineArgs():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", help="Enable the WiFi module", action="store_true")
    group.add_argument("-d", help="Disable the WiFi module",  action="store_true")
    group.add_argument("-t", help="Switch the status of the WiFi module",  action="store_true")
    parser.add_argument("-r", help="Reboot the WiFi module to apply the changes", action="store_true")
    parser.add_argument("username", type=str, help="The username to login on Free site")
    parser.parse_args()

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
        print isWifiModuleActive(wifiDom)
        


if __name__ == '__main__':
    main()
