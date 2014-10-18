import mechanize
import sys

kUsernameControlName = "login"
kPasswordControlName = "pass"

def getLoginData():
    kUsageString = "Usage: " + sys.argv[0] + " username password"
    if len(sys.argv) != 3:
        print "Wrong number of arguments"
        print kUsageString
        sys.exit(1)
    return sys.argv[1], sys.argv[2]


def isLoginForm(iForm):
    hasLoginControl = False
    hasPasswordControl = False
    for control in iForm.controls:
        if control.name == kUsernameControlName:
            hasLoginControl = True
        elif control.name == kPasswordControlName:
            hasPasswordControl = True
    return hasLoginControl and hasPasswordControl

def main():
    username, password = getLoginData()
    browser = mechanize.Browser()
    kLoginPage = "https://subscribe.free.fr/login/login.pl"
    loginPageRequest = browser.open(kLoginPage)
    # The page usually has only one unnamed form, the login one
    loginForm = list(browser.forms())[0]
    # Checking that this is true
    assert isLoginForm(loginForm)
    loginForm[kUsernameControlName] = username
    loginForm[kPasswordControlName] = password
    browser.submit()



if __name__ == '__main__':
    main()
