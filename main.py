import argparse
from bs4 import BeautifulSoup
import cookielib
import getpass
import mechanize
import sys
import urllib

# Python 2.x doesn't offer Enums. Creating enum type using type method
# https://docs.python.org/2/library/functions.html#type
def enum(**enums):
    return type('Enum', (), enums)

WifiModuleAction = enum(ON = 1, OFF = 2, SWITCH = 3)

class FreeboxSettingsManager:
    kLoginPage = "https://subscribe.free.fr/login/login.pl"
    kPasswordControlName = "pass"
    kUsernameControlName = "login"

    def __init__(self):
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.browser.set_cookiejar(cookielib.CookieJar())
        self.dom = None
        self.wifiModuleStateElement = None

        self.username = None
        self.password = None

    def changeWiFiModuleState(self, iAction):
        assert self.wifiModuleStateElement
        if iAction == WifiModuleAction.ON:
            if self.isWifiModuleActive():
                print "Nothing to do, WiFi module is already ON"
            else:
                self.turnOnWiFiModule()
        elif iAction == WifiModuleAction.OFF:
            if isWifiModuleActive():
                self.turnOffWiFiModule()
            else:
                print "Nothing to do, WiFi module is already OFF"
        elif iAction == WifiModuleAction.SWITCH:
            self.switchWiFiModule()
        else:
            raise Exception("Unknown action for WiFi module")

    def execute(self):
        self.parseCommandLineArgs()
        if self.performLogin():
            wifiPageResponse = self.browser.follow_link(text_regex=r"Param\xe9trer mon r\xe9seau WiFi")
            self.dom = BeautifulSoup(wifiPageResponse.read())
            self.wifiModuleStateElement = self.getElementByName("input", "wifi_disable_radio")
            print self.isWifiModuleActive()
            print self.getFormInputsForPostRequest()
        else:
            print "Unable to login"

    def getElementByName(self, iElementType, iElementName):
        searchedElement = self.dom.find(iElementType, {"name": iElementName})
        assert searchedElement is not None
        return searchedElement

    def getFormInputsForPostRequest(self):
        requiredInputDict = {}
        for inputName in ["wifi_random", "wifi_disable_radio", "wifi_active",
                          "wifi_ssid", "wifi_channel_auto", "wifi_channel",
                          "wifi_ssid_hide", "wifi_key_type", "wifi_key", "action", "tpl"]:
            inputValue = self.getElementByName("input", inputName)["value"]
            requiredInputDict[inputName] = inputValue
        return requiredInputDict

    def isSuccessfulLogin(self, iLoginResponseStr):
        # In case of failure in the login phase, a div with class loginalert is available
        loginResponseDom = BeautifulSoup(iLoginResponseStr)
        loginAlertDiv = loginResponseDom.find("div", attrs={"class": "loginalert"})
        return True if loginAlertDiv is None else False

    def isWifiModuleActive(self):
        # The wifi module is controlled by <input name="wifi_disable_radio" type="hidden" value="0">
        return self.wifiModuleStateElement["value"] == "0"

    def parseCommandLineArgs(self):
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-e", help="Enable the WiFi module", action="store_true")
        group.add_argument("-d", help="Disable the WiFi module",  action="store_true")
        group.add_argument("-t", help="Switch the status of the WiFi module",  action="store_true")
        parser.add_argument("-r", help="Reboot the WiFi module to apply the changes", action="store_true")
        parser.add_argument("username", type=str, help="The username to login on Free site")
        args = parser.parse_args()
        self.username = args.username

    def performLogin(self):
        self.password = getpass.getpass("Please insert password: ")
        loginPageRequest = self.browser.open(FreeboxSettingsManager.kLoginPage)
        # The page usually has only one unnamed form, the login one
        self.browser.select_form(nr = 0)
        self.browser.form[FreeboxSettingsManager.kUsernameControlName] = self.username
        self.browser.form[FreeboxSettingsManager.kPasswordControlName] = self.password
        loginResponse = self.browser.submit()
        return self.isSuccessfulLogin(loginResponse.read())

    def switchWiFiModule(self):
        elementValue = self.wifiModuleStateElement["value"]
        assert elementValue == "0" or elementValue == "1"
        logMessage = "Switching from "
        logMessage += "ON to OFF" if self.isWifiModuleActive() else "OFF to ON"
        print logMessage
        self.wifiModuleStateElement["value"] = "1" if elementValue == "0" else "0"

    def turnOffWiFiModule(self):
        print "Turning OFF WiFi module"
        self.wifiModuleStateElement["value"] = "1"

    def turnOnWiFiModule(self):
        print "Turning ON WiFi module"
        self.wifiModuleStateElement["value"] = "0"

    def testPost(self):
        data = urllib.urlencode(self.getFormInputsForPostRequest())
        request = mechanize.Request( "https://adsl.free.fr/fbxcfg.pl?id=12264612&idt=be2d0acc8fe84193")
        response = mechanize.urlopen(request, data=data)
        print response.info()
        print response.read()

def main():
    manager = FreeboxSettingsManager()
    manager.execute()

if __name__ == '__main__':
    main()
