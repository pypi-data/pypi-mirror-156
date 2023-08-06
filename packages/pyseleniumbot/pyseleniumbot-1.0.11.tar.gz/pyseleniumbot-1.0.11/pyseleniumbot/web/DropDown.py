from select import select
from xml.dom.minidom import Element
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from pyseleniumbot.web.webWaits import customwebDriverwait
# drop downs


class DropDownActions(customwebDriverwait):
    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser

    def selectDropDownByValue(self, xpath, valueToSelect):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            #if(elementVisibility):
                select = Select(self.browser.find_element(By.XPATH, xpath))
                select.select_by_value(valueToSelect)

    def selectDropDownByIndex(self, xpath, indexToSelect):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            #if(elementVisibility):
                select = Select(self.browser.find_element(By.XPATH, xpath))
                select.select_by_index(indexToSelect)

    def selectDropDownByVisibleText(self, xpath, textToSelect):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
                select = Select(self.browser.find_element(By.XPATH, xpath))
                select.select_by_visible_text(textToSelect)

    def deselectAllOptionsInDropDown(self, xpath):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            #if(elementVisibility):
                select = Select(self.browser.find_element(By.XPATH, xpath))
                select.deselect_all()

    def getDefaultSelectedDropDownOptions(self, xpath):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        selectedOptions=[]
        if(elementPresense):
            #if(elementVisibility):
                select = Select(self.browser.find_element(By.XPATH, xpath))
                all_selected_options = select.all_selected_options
                for i in all_selected_options:
                    if(i.text):
                        selectedOptions.append(i.text)
                    elif(i.get_attribute('value')):
                        selectedOptions.append(i.get_attribute('value'))
                return selectedOptions

    def getAllOptionInDropDown(self, xpath):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        allOptions=[]
        if(elementPresense):
            #if(elementVisibility):
                select = Select(self.browser.find_element(By.XPATH, xpath))
                options = select.options
                for i in options:
                    if(i.text):
                        allOptions.append(i.text)
                    elif(i.get_attribute('value')):
                        allOptions.append(i.get_attribute('value'))

                return allOptions

    def deselectByIndex(self, xpath, index):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            #if(elementVisibility):
                select = Select(self.browser.find_element(By.XPATH, xpath))
                select.deselect_by_index(index)

    def deselectByValue(self, xpath, value):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            #if(elementVisibility):
                select = Select(self.browser.find_element(By.XPATH, xpath))
                select.deselect_by_value(value)

    def deselectByVisibleText(self, xpath, text):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            #if(elementVisibility):        
                select = Select(self.browser.find_element(By.XPATH, xpath))
                select.deselect_by_visible_text(text)

    def getFirstSelecteOption(self, xpath):
        elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
        #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
        firstSelectedOption=[]
        if(elementPresense):
            #if(elementVisibility):        
                select = Select(self.browser.find_element(By.XPATH, xpath))
                selectedOption=select.first_selected_option
                #for i in selectedOption:
                if(selectedOption.text):
                        firstSelectedOption.append(selectedOption.text)
                elif(selectedOption.get_attribute('value')):
                        firstSelectedOption.append(selectedOption.get_attribute('value'))

                return firstSelectedOption 