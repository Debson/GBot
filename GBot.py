import time
from enum import Enum

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os



class GBot():

    def __init__(self):
        self.website = "https://en.gladiatus.gameforge.com/"
        self.chromePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver.exe")
        self.adblockPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "adblock")

        self.expeditionEnabled = True
        self.dunegonEnabled = False
        self.dungeonType = self.DungeonType.NORMAL;
        self.circusTurmaEnabled = False

    def setBrowser(self, browser):
        self.browser = browser

    def setWebsite(self, website):
        self.website = website

    def setLoginInformation(self, logInfo):
        self.logInfo = logInfo

    def setExpeditionLocation(self, location):
        self.expeditionLocation = location

    def setMonsterName(self, monsterName):
        self.monsterName = monsterName

    def setDungeonLocation(self, location):
        self.dungeonLocation = location

    def setExpeditionEnabled(self, enabled):
        self.expeditionEnabled = enabled

    def setCircusTurmaEnabled(self, enabled):
        self.circusTurmaEnabled = enabled

    def setDungeonEnabled(self, enabled):
        self.dunegonEnabled = enabled

    def __getExpLocations(self):
        self.__menuOption("Overview")
        self.browser.execute_script("return switchMenu(2)")
        countryMenu = self.browser.find_elements_by_xpath("//*[@id='submenu2']/a")

        return countryMenu

    def __setDefaultLocations(self):
        expLocations = self.__getExpLocations()
        if(len(expLocations) > 1):
            self.expeditionLocation = expLocations[1].text
            self.dungeonLocation = expLocations[1].text
            expLocations[1].click();
            self.monsterName = self.browser.find_element_by_xpath("//*[@id='expedition_info1']").get_attribute("data-tooltip").split("\"")[1]
        else:
            print("ERROR: You don't have any locations enabled!")

    # current page must be a login's page
    def __performLogin(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('load-extension=' + self.adblockPath)
        self.browser = webdriver.Chrome(self.chromePath, options=self.chrome_options)

        tabs = self.browser.window_handles
        if len(tabs) > 1:
            self.browser.switch_to_window(tabs[1])
            self.browser.close()
            self.browser.switch_to_window(tabs[0])

        self.browser.get(self.website)
        self.browser.refresh()
        self.browser.refresh()

        self.provinces = Select(self.browser.find_element_by_id('login_server'))

        for x in self.provinces.options:
            if self.logInfo.getProvince() in x.text:
                self.provinces.select_by_visible_text(x.text)
                print(x.get_attribute("value"))

        self.browser.find_element_by_id("login_username").send_keys(self.logInfo.getUsername())
        self.browser.find_element_by_id("login_password").send_keys(self.logInfo.getPassword())
        self.browser.find_element_by_id("loginsubmit").click()

    # current page must be a desired location's page
    def __performExpedition(self):
        for monsterCount in range(1, 5):
            monster = self.browser.find_element_by_xpath("//*[@id='expedition_info" + str(monsterCount) + "']")
            if monster.get_attribute("data-tooltip").split("\"")[1] == self.monsterName:
                print(monster.get_attribute("data-tooltip").split("\"")[1])
                button = self.browser.find_element_by_xpath("//*[@id='expedition_list']/div[1]/div[2]/button")
                button.click()
                break
        self.__menuOption("Overview")

    #current page must be a desired location's page
    def __performDungeon(self):
        self.__switchToDungeon()
        dungeonAreas = self.browser.find_elements_by_xpath("//*[@id='content']/div[2]/div/map/area")
        if len(dungeonAreas) > 0:
            dungeonAreas[0].click()
        self.__menuOption("Overview")

    def __performCircusTurma(self):
        self.__menuOption("Arena")
        self.__switchToArenaTab("Circus Turma")
        time.sleep(2)

        self.__menuOption("Overview")

    def __switchToArenaTab(self, arenaType):

        # There is 4 tabs in arena(Arena, Provinciarum Arena, Circus Turma and Circus Provinciarum
        for i in range(1, 5):
            try:
                tab = self.browser.find_element_by_xpath("//*[@id='mainnav']/li/table/tbody/tr/td[" + str(i) +"]/a")
                if tab.text == arenaType:
                    tab.click()
                    break
            except NoSuchElementException:
                print("ERROR: You are on a wrong page!")

    #always call this function before "performExpedition" and "performDungeon"
    def __goToLocation(self, location):
        expLocations = self.__getExpLocations()
        for loc in expLocations:
            if loc.text == location:
                loc.click()
                break

    # current page must be a desired location's page
    def __switchToDungeon(self):
        dungeonTab = self.browser.find_element_by_xpath("//*[@id='mainnav']/li/table/tbody/tr/td[2]/a")
        dungeonTab.click()

        try:
            if self.dungeonType == self.DungeonType.NORMAL:
                dungeonTypeButton = self.browser.find_element_by_xpath("//*[@id='content']/div[2]/div/form/table/tbody/tr/td[1]/input")
            if self.dungeonType == self.DungeonType.ADVANCED:
                dungeonTypeButton = self.browser.find_element_by_xpath("//*[@id='content']/div[2]/div/form/table/tbody/tr/td[2]/input")

            dungeonTypeButton.click()
            print("Dungeon " + self.dungeonLocation + " entered successfully!")
        except NoSuchElementException:
            print("Already in dungeons!")


    def __menuOption(self, menuOption):
        self.browser.execute_script("return switchMenu(1)")
        mainmenu = self.browser.find_elements_by_xpath("//*[@id='mainmenu']//a")
        for x in mainmenu:
            if x.text == menuOption:
                print(x.text)
                x.click()
                break

    def __isReadyForExpedition(self):
        cooldown = self.browser.find_element_by_xpath("//*[@id='cooldown_bar_text_expedition']")
        if cooldown.text == "Go to expedition":
            return True
        return False

    def __isReadyForDungeon(self):
        cooldown = self.browser.find_element_by_xpath("//*[@id='cooldown_bar_text_dungeon']")
        if cooldown.text == "Go to dungeon":
            return True
        return False

    def __isReadyForCircusTurma(self):
        cooldown = self.browser.find_element_by_xpath("//*[@id='cooldown_bar_text_ct']")
        if cooldown.text == "To Circus Turma":
            return True
        return False

    def __isMaintenancePerformed(self):
        try:
            maintance = self.browser.find_element_by_xpath("//*[@id='content_infobox']/section/input")
            maintance.click()
        except NoSuchElementException:
            #print("There is no maintenance performed! :)")
            return False
        return True


    def run(self):
        self.__performLogin()

        self.__setDefaultLocations()

        while True:
            time.sleep(1)

            if self.__isMaintenancePerformed():
                continue

            if self.__isReadyForExpedition():
                self.__goToLocation(self.expeditionLocation)
                self.__performExpedition()

            if self.__isReadyForDungeon():
                self.__goToLocation(self.dungeonLocation)
                self.__performDungeon()

            if self.__isReadyForCircusTurma():
                self.__performCircusTurma()


    class DungeonType(Enum):
        NORMAL = 1
        ADVANCED = 2

class GLogin:
    def __init__(self, username, password, province):
        self.username = username
        self.password = password
        self.province = province

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def getProvince(self):
        return self.province

