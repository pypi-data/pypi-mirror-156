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
from selenium.webdriver.remote.webdriver import WebDriver
import cv2
import numpy as np
import easyocr
import matplotlib.pyplot as plt

class common(customwebDriverwait):

    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser

    def findElementsBy(self, xpath):
        # self.browser.presence_of_all_elements_located(xpath)
        # self.browser.visibility_of_element_located(xpath)
        return self.browser.find_elements(By.XPATH, xpath)

    def findElementBy(self, xpath):
        self.browser.presence_of_element_located(xpath)
        self.browser.visibility_of_element_located(xpath)
        self.browser.find_element(By.XPATH, xpath)

    def click(self, xpath):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                self.browser.find_element(By.XPATH, xpath).click()

    def clear(self, xpath):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                self.browser.find_element(By.XPATH, xpath).clear()    
    
    
    def isClickable(self, xpath, index=None):
        # self.browser.visibility_of_element_located(xpath)
        return WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((xpath)))
    
    '''
    Simulates typing into the element.

    Args:	
    value - A string for typing, or setting form fields. For setting file inputs, this could be a local file path.
    Use this to send simple key events or to fill out form fields:
    form_textfield = driver.find_element(By.NAME, 'username')
                    form_textfield.send_keys("admin")
    This can also be used to set file inputs.

    file_input = driver.find_element(By.NAME, 'profilePic')
    file_input.send_keys("path/to/profilepic.gif")
    # Generally it's better to wrap the file path in one of the methods
    # in os.path to return the actual path to support cross OS testing.
    # file_input.send_keys(os.path.abspath("path/to/profilepic.gif"))
    '''

    def fillField(self, xpath, text):
        elementPresence = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisibility = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresence):
            if(elementVisibility):
                self.browser.find_element(By.XPATH, xpath).send_keys(text)


    def navigateto(self, urlstring):
        self.browser.get(urlstring)

    '''
        Gets the given attribute or property of the element.

        This method will first try to return the value of a property with the given name. If a property with that name doesn’t exist, it returns the value of the attribute with the same name. If there’s no attribute with that name, None is returned.

        Values which are considered truthy, that is equals “true” or “false”, are returned as booleans. All other non-None values are returned as strings. For attributes or properties which do not exist, None is returned.

        To obtain the exact value of the attribute or property, use get_dom_attribute() or get_property() methods respectively.

        Args:	
        name - Name of the attribute/property to retrieve.
        Example:

        # Check if the "active" CSS class is applied to an element.
        is_active = "active" in target_element.get_attribute("class")
    '''
    def getAttribute(self, xpath,AttributeName):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                return self.browser.find_element(By.XPATH, xpath).get_attribute(AttributeName)      
    
    '''
        Gets the given attribute of the element. Unlike get_attribute(), this method only returns 
        attributes declared in the element’s HTML markup.

        Args:	
        name - Name of the attribute to retrieve.
        Usage:	
        text_length = target_element.get_dom_attribute("class")
    '''
    def getDomAttribute(self, xpath,AttributeName):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                return self.browser.find_element(By.XPATH, xpath).get_dom_attribute(AttributeName) 



    '''
        Gets the given property of the element.

        Args:	
        name - Name of the property to retrieve.
        Usage:	
        text_length = target_element.get_property("text_length")
    '''
    def getProperty(self, xpath,PropertyName):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                return self.browser.find_element(By.XPATH, xpath).get_property(PropertyName) 
    '''
        Whether the element is visible to a user.
    '''
    def isElementDisplayed(self, xpath):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                return self.browser.find_element(By.XPATH, xpath).is_displayed() 
    '''
        Returns whether the element is enabled.
    '''
    def isElementEnabled(self, xpath):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                return self.browser.find_element(By.XPATH, xpath).is_enabled()  

    '''
        Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.
    '''
    def isElementSelected(self, xpath):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                return self.browser.find_element(By.XPATH, xpath).is_selected() 
    
    '''
        Saves a screenshot of the current element to a PNG image file. Returns
        False if there is any IOError, else returns True. Use full paths in your filename.
    '''
    def currentElementScreenshot(self, xpath,screenShotSavingPath):
        elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
        elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
        if(elementPresense):
            if(elementVisible):
                return self.browser.find_element(By.XPATH, xpath).screenshot(screenShotSavingPath)
    # action class

    def actionClick(self, xpath):
        actions = ActionChains(self.browser)
        element = self.browser.find_element(By.XPATH, xpath)
        actions.click(element)

    def actionClickandHold(self, xpath=None):
        actions = ActionChains(self.browser)
        if(xpath != None):
            element = self.browser.find_element(By.XPATH, xpath)
        else:
            element = None
        if(element != None):
            actions.click_and_hold(element)
        else:
            actions.click_and_hold()

    def moveToElement(self, xpath):
        actions = ActionChains(self.browser)
        element = self.browser.find_element(By.XPATH, xpath)
        actions.move_to_element(element).perform()

    def moveToElementWithOffset(self, xpath, xoffset, yoffset):
        actions = ActionChains(self.browser)
        element = self.browser.find_element(By.XPATH, xpath)
        actions.move_to_element_with_offset(element, xoffset, yoffset)

    def moveByOffsett(self, xoffset, yoffset):
        actions = ActionChains(self.browser)
        actions.move_by_offset(xoffset, yoffset)

    def actionRelease(self, xpath=None):
        actions = ActionChains(self.browser)
        if(xpath != None):
            element = self.browser.find_element(By.XPATH, xpath)
        else:
            element = None
        if(element != None):
            actions.release(element)
        else:
            actions.release()

    def keyDown(self, ModifierKey, key, xpath=None):
        actions = ActionChains(self.browser)
        if(xpath != None):
            element = self.browser.find_element(By.XPATH, xpath)
        else:
            element = None
        if(element != None):
            actions.key_down(ModifierKey, element).send_keys(key)
        else:
            actions.key_down(ModifierKey).send_keys(key)

    def keyUp(self, ModifierKey, key, xpath=None):
        actions = ActionChains(self.browser)
        if(xpath != None):
            element = self.browser.find_element(By.XPATH, xpath)
        else:
            element = None
        if(element != None):
            actions.key_up(ModifierKey, element).perform()
        else:
            actions.key_up(ModifierKey).perform()

    def double_click(self, xpath: None):
        actions = ActionChains(self.browser)
        if(xpath != None):
            element = self.browser.find_element(By.XPATH, xpath)
        else:
            element = None
        if(element != None):
            actions.double_click(element)
        else:
            actions.double_click()

    def righttClick(self, xpath=None):
        actions = ActionChains(self.browser)
        if(xpath != None):
            element = self.browser.find_element(By.XPATH, xpath)
        else:
            element = None
        if(element != None):
            actions.context_click(element)
        else:
            actions.context_click()

    def resetActions(self):
        actions = ActionChains(self.browser)
        actions.reset_actions()

    def sendKeys(self, *keys_to_send):
        actions = ActionChains(self.browser)
        actions.send_keys(keys_to_send)

    def sendKeysToElement(self, xpath, *keys_to_send):
        actions = ActionChains(self.browser)
        element = common.webdriverWait(self, xpath)
        actions.send_keys_to_element(element, keys_to_send)
        '''
        Gets the full document screenshot of the current window as a base64 encoded string
        which is useful in embedded images in HTML.

        Usage:	
        driver.get_full_page_screenshot_as_base64()
        '''
    def get_screenshot_ofcurrentActive_page_in_base64(self):
        return self.browser.get_full_page_screenshot_as_base64()

        '''
        Saves a full document screenshot of the current window to a PNG image file. Returns
        False if there is any IOError, else returns True. Use full paths in your filename.
        Args:	
        filename: The full path you wish to save your screenshot to. This should end with a .png extension.
        Usage:	
        driver.get_full_page_screenshot_as_file('/Screenshots/foo.png')
        '''
    def get_screenshot_ofcurrentActive_page_asFile(self,filename:str):
        return self.browser.get_full_page_screenshot_as_file(filename)    
        '''get_full_page_screenshot_as_png() → str
        Gets the full document screenshot of the current window as a binary data.

        Usage:	
        driver.get_full_page_screenshot_as_png()
        '''
    def get_screenshot_ofcurrentActive_page_asPNG(self):
        return self.browser.get_full_page_screenshot_as_png()

        ''' 
        Saves a screenshot of the current window to a PNG image file. Returns
        False if there is any IOError, else returns True. Use full paths in your filename.
        Args:	
        filename: The full path you wish to save your screenshot to. This should end with a .png extension.
        Usage:	
        driver.save_screenshot('/Screenshots/foo.png')
        '''
    def screenshot_save_full_page_screenshot(self,filename):
        return self.browser.save_screenshot(filename)

    '''
    returns the embedded text in the image.
    It returns a list of detected text, with each text element containing three types of information. 
    Which are: the text, its bounding box vertices, and the confidence level of the text detection
    '''    
    def get_embeddedText_from_image(self,path:str):
         reader= easyocr.Reader(['en'])
         return reader.readtext(path)    
    