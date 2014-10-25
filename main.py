from bs4 import BeautifulSoup
import getpass
import mechanize
import sys

kUsernameControlName = "login"
kPasswordControlName = "pass"

def getLoginData():
    kUsageString = "Usage: " + sys.argv[0] + " username"
    if len(sys.argv) != 2:
        print "Wrong number of arguments"
        print kUsageString
        sys.exit(1)
    username = sys.argv[1]
    password = getpass.getpass()
    return username, password

def isLoginForm(iForm):
    hasLoginControl = False
    hasPasswordControl = False
    for control in iForm.controls:
        if control.name == kUsernameControlName:
            hasLoginControl = True
        elif control.name == kPasswordControlName:
            hasPasswordControl = True
    return hasLoginControl and hasPasswordControl

def isSuccessfullLogin(iLoginResponseStr):
    # In case of failure in the login phase, a div with class loginalert is available
    responseDom = BeautifulSoup(iLoginResponseStr)
    loginAlertDiv = responseDom.find("div", attrs={"class": "loginalert"})
    return True if loginAlertDiv is None else False

def main():
    username, password = getLoginData()
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    kLoginPage = "https://subscribe.free.fr/login/login.pl"
    loginPageRequest = browser.open(kLoginPage)
    # The page usually has only one unnamed form, the login one
    browser.select_form(nr=0)
    browser.form[kUsernameControlName] = username
    browser.form[kPasswordControlName] = password
    loginResponse = browser.submit()
    if isSuccessfullLogin(loginResponse.read()):
        browser.follow_link(text_regex=r".*&tpl=wifi").read()


if __name__ == '__main__':
    main()
