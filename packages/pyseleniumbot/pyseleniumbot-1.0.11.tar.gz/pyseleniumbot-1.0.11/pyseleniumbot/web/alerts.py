from select import select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome import service
from pyseleniumbot.web.webWaits import customwebDriverwait
class browserAlerts(customwebDriverwait):

    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser



    #alerts
    # Use this class to interact with alert prompts. 
    # It contains methods for dismissing, accepting, inputting, and getting text from alert prompts.   
    def acceptAlert(self):
        alertPresence= super().WaitForAlert_is_present()
        if(alertPresence):
            Alert(self.browser).accept()
    def dismissAlert(self):
        alertPresence= super().WaitForAlert_is_present()
        if(alertPresence):
            Alert(self.browser).dismiss() 
    def getAlertText(self):
        alertPresence= super().WaitForAlert_is_present()
        if(alertPresence):
            alertText=Alert(self.browser).text
            return alertText
    def sendKeystoAlert(self,keysToSend):
        alertPresence= super().WaitForAlert_is_present()
        name_prompt = Alert(self.browser)
        name_prompt.send_keys(keysToSend)
    # Special Keys
    #The Keys implementation.
    ''' yet to complete'''
    #Touch Actions
    ''' yet to complete'''






