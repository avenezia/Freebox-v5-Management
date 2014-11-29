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

WifiModuleAction = enum(ENABLE = 1, DISABLE = 2, SWITCH = 3)

class FreeboxWiFiManager:
    kDisabledValue = "1"
    kEnabledValue = "0"
    kLoginPage = "https://subscribe.free.fr/login/login.pl"
    kPasswordControlName = "pass"
    kUsernameControlName = "login"
    kWiFiSettingsFormName = "frm"
    kWifiModuleStateInputName = "wifi_disable_radio"

    def __init__(self):
        self.action = None
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.browser.set_cookiejar(cookielib.CookieJar())
        self.dom = None
        self.wifiModuleStateInputElement = None

        self.username = None
        self.password = None

    def changeWiFiModuleState(self):
        assert self.wifiModuleStateInputElement
        changeIsNeeded = False
        if self.action == WifiModuleAction.ENABLE:
            if self.isWifiModuleActive():
                print "Nothing to do, WiFi module is already enabled"
            else:
                self.enableWiFiModule()
                changeIsNeeded = True
        elif self.action == WifiModuleAction.DISABLE:
            if self.isWifiModuleActive():
                self.disableWiFiModule()
                changeIsNeeded = True
            else:
                print "Nothing to do, WiFi module is already disabled"
        elif self.action == WifiModuleAction.SWITCH:
            self.switchWiFiModule()
            changeIsNeeded = True
        else:
            raise Exception("Unknown action for WiFi module")
        return changeIsNeeded

    def commitChange(self):
        """It sends the form to perform the change of the WiFi status"""
        changeResponse = self.browser.submit()
        if changeResponse.code == 200:
            print "Modification performed correctly"
        else:
            print "Problem while performing modification"

    def disableWiFiModule(self):
        print "Disabling WiFi module"
        self.wifiModuleStateInputElement.value = self.kDisabledValue

    def enableWiFiModule(self):
        print "Enabling WiFi module"
        self.wifiModuleStateInputElement.value = self.kEnabledValue

    def execute(self):
        """It opens the page with the WiFi configuration and then performs the changes"""
        self.parseCommandLineArgs()
        if self.performLogin():
            wifiPageResponse = self.browser.follow_link(text_regex=r"Param\xe9trer mon r\xe9seau WiFi")
            if wifiPageResponse.code == 200:
                self.findWiFiController()
                if self.changeWiFiModuleState():
                    self.commitChange()
            else:
                print "Error while getting the page with the WiFi configuration"
        else:
            print "Unable to login"

    def findWiFiController(self):
        """It selects the form and the input element controlling the WiFi module"""
        self.browser.select_form(name = self.kWiFiSettingsFormName)
        self.wifiModuleStateInputElement = self.browser.form.find_control(self.kWifiModuleStateInputName)
        assert self.wifiModuleStateInputElement
        self.wifiModuleStateInputElement.readonly = False

    def isSuccessfulLogin(self, iLoginResponseStr):
        # In case of failure in the login phase, a div with class loginalert is available
        loginResponseDom = BeautifulSoup(iLoginResponseStr)
        loginAlertDiv = loginResponseDom.find("div", attrs={"class": "loginalert"})
        return True if loginAlertDiv is None else False

    def isWifiModuleActive(self):
        # The wifi module is controlled by <input name="wifi_disable_radio" type="hidden" value=self.kEnabledValue>
        return self.wifiModuleStateInputElement.value == self.kEnabledValue

    def parseAction(self, args):
        if args.e:
            self.action = WifiModuleAction.ENABLE
        elif args.d:
            self.action = WifiModuleAction.DISABLE
        elif args.s:
            self.action = WifiModuleAction.SWITCH
        else:
            assert False, "Unknown action provided"

    def parseCommandLineArgs(self):
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group(required = True)
        group.add_argument("-e", help="Enable the WiFi module", action="store_true")
        group.add_argument("-d", help="Disable the WiFi module",  action="store_true")
        group.add_argument("-s", help="Switch the status of the WiFi module",  action="store_true")
        parser.add_argument("-r", help="Reboot the WiFi module to apply the changes", action="store_true")
        parser.add_argument("username", type=str, help="The username to login on Free site")
        args = parser.parse_args()
        self.parseAction(args)
        self.username = args.username

    def performLogin(self):
        self.password = getpass.getpass("Please insert password: ")
        loginPageRequest = self.browser.open(self.kLoginPage)
        # The page usually has only one unnamed form, the login one
        self.browser.select_form(nr = 0)
        self.browser.form[self.kUsernameControlName] = self.username
        self.browser.form[self.kPasswordControlName] = self.password
        loginResponse = self.browser.submit()
        return self.isSuccessfulLogin(loginResponse.read())

    def switchWiFiModule(self):
        wifiModuleStateValue = self.wifiModuleStateInputElement.value
        assert wifiModuleStateValue == self.kEnabledValue or wifiModuleStateValue == self.kDisabledValue
        logMessage = "Switching from "
        logMessage += "enabled to disabled" if self.isWifiModuleActive() else "disabled to enabled"
        print logMessage
        self.wifiModuleStateInputElement.value = \
            self.kDisabledValue if wifiModuleStateValue == self.kEnabledValue else self.kEnabledValue

def main():
    manager = FreeboxWiFiManager()
    manager.execute()

if __name__ == '__main__':
    main()
