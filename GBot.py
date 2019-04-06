import os
import random
import re
import sys
import time
from enum import Enum

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, \
    StaleElementReferenceException, ElementNotVisibleException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GBot():

    def __init__(self):
        self.website = "https://en.gladiatus.gameforge.com/"
        self.chromePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver.exe")
        self.adblockPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "adblock")

        #character
        self.minHealthThreshold = 8.0
        self.backpackWithFoodNumber = 1

        #exp
        self.expeditionEnabled = True
        self.dunegonEnabled = True
        self.dungeonType = self.DungeonType.NORMAL;

        #arenas
        self.circusTurmaEnabled = False
        self.circusProvinciarumEnabled = True
        self.arenaEnabled = False
        self.arenaProvinciarumEnabled = False

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
        print("Assigning default values!")
        expLocations = self.__getExpLocations()
        if(len(expLocations) > 1):
            self.expeditionLocation = expLocations[1].text
            self.dungeonLocation = expLocations[1].text
            expLocations[1].click();
            self.monsterName = self.browser.find_element_by_xpath("//*[@id='expedition_info1']").get_attribute("data-tooltip").split("\"")[1]
            self.__menuOption("Overview")
            print("Assigning default values finished!")

            # Hardcoded just for now, will be located in a .txt file
            self.expeditionLocation = "Death Hill"
            self.dungeonLocation = "Cave Temple"
            self.monsterName = "Skeleton Warrior"
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

        self.browser.find_element_by_id("login_username").send_keys(self.logInfo.getUsername())
        self.browser.find_element_by_id("login_password").send_keys(self.logInfo.getPassword())
        self.browser.find_element_by_id("loginsubmit").click()

    # current page must be a desired location's page
    def __performExpedition(self):
        for monsterCount in range(1, 5):
            delay = 3  # seconds
            try:
                monster = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='expedition_info" + str(monsterCount) + "']")))
                if monster.get_attribute("data-tooltip").split("\"")[1] == self.monsterName:
                    # print(monster.get_attribute("data-tooltip").split("\"")[1])
                    button = self.browser.find_element_by_xpath("//*[@id='expedition_list']/div[1]/div[2]/button")
                    button.click()
                    self.__menuOption("Overview")
                    break
            except TimeoutException:
                print("Loading took too much time!")
            except StaleElementReferenceException:
                print("Element is not attached to the page document!")
            except NoSuchElementException:
                print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

    #current page must be a desired location's page
    def __performDungeon(self):
        self.__switchToDungeon()
        delay = 3
        try:
            dungeonAreas = WebDriverWait(self.browser, delay).until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//*[@id='content']/div[2]/div/map/area")))
            if len(dungeonAreas) > 0:
                dungeonAreas[0].click()
            self.__menuOption("Overview")
        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

    def __performArena(self):
        self.__menuOption("Arena")
        delay = 3;
        try:
            #possible table rows
            tableRows = WebDriverWait(self.browser, delay).until(EC.presence_of_all_elements_located(
                (By.XPATH, "//*[@id='content']/article/aside[2]/section/table/tbody/tr/td[2]/div")))

            opponentNumber = random.randint(0, len(tableRows) - 1)
            opponent = tableRows[opponentNumber]
            opponent.click()
            opponentName = tableRows[opponentNumber].text.split(" ")[0]
            print("Arena: You just fought " + opponentName)
            self.__displayFightResult()
            self.__menuOption("Overview")
        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

    def __performProvinciarumArena(self):
        self.__menuOption("Arena")
        self.__switchToArenaTab("Provinciarum Arena")

        delay = 3;
        try:
            tableRows = WebDriverWait(self.browser, delay).until(EC.presence_of_all_elements_located(
                (By.XPATH, "//*[@id='own2']/table/tbody/tr/td[4]/div")))

            opponentNumber = random.randint(0, len(tableRows) - 1)
            opponent = tableRows[opponentNumber]
            opponent.click()
            opponentName = tableRows[opponentNumber].text.split(" ")[0]
            print("Provinciarum Arena: You just fought " + opponentName)
            self.__displayFightResult()
            self.__menuOption("Overview")
        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

    def __performCircusTurma(self):
        self.__menuOption("Arena")
        self.__switchToArenaTab("Circus Turma")
        delay = 3;
        try:
            # possible table rows
            tableRows = WebDriverWait(self.browser, delay).until(EC.presence_of_all_elements_located(
                (By.XPATH, "//*[@id='content']/article/aside[2]/section/table/tbody/tr/td[2]/div")))

            opponentNumber = random.randint(0, len(tableRows) - 1)
            opponent = tableRows[opponentNumber]
            opponent.click()
            opponentName = tableRows[opponentNumber].text.split(" ")[0]
            print("Circus Turma: You just fought " + opponentName)
            self.__displayFightResult()
            self.__menuOption("Overview")
        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

        self.__menuOption("Overview")

    def __performCircusProvinciarum(self):
        self.__menuOption("Arena")
        self.__switchToArenaTab("Circus Provinciarum")

        delay = 3;
        try:
            tableRows = WebDriverWait(self.browser, delay).until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//*[@id='own3']/table/tbody/tr/td[4]/div")))

            opponentNumber = random.randint(0, len(tableRows) - 1)
            opponent = tableRows[opponentNumber]
            opponent.click()
            opponentName = tableRows[opponentNumber].text.split(" ")[0]
            print("Circus Provinciarum: You just fought " + opponentName)
            self.__displayFightResult()
            self.__menuOption("Overview")
        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

    def __switchToArenaTab(self, arenaType):
        # There is 4 tabs in arena(Arena, Provinciarum Arena, Circus Turma and Circus Provinciarum
        for i in range(1, 5):
            try:
                tab = self.browser.find_element_by_xpath("//*[@id='mainnav']/li/table/tbody/tr/td[" + str(i) +"]/a")
                if tab.text == arenaType:
                    tab.click()
                    break
            except TimeoutException:
                print("Loading took too much time!")
            except StaleElementReferenceException:
                print("Element is not attached to the page document!")
            except NoSuchElementException:
                print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

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
        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

    def __displayFightResult(self):
        delay = 3  # seconds
        try:
            result = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located(
                                    (By.XPATH, "//*[@id='reportHeader']/table/tbody/tr/td[2]")))
            print(result.text)
        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

    def __menuOption(self, menuOption):
        self.__isChestFound()
        self.__cancelNotification()
        self.browser.execute_script("return switchMenu(1)")
        delay = 3
        try:
            mainmenu = WebDriverWait(self.browser, delay).until(EC.presence_of_all_elements_located(
                                    (By.XPATH, "//*[@id='mainmenu']//a")))
            for x in mainmenu:
                if x.text == menuOption and "active" not in x.get_attribute("class"):
                    x.click()
                    break
        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

#Id for daily bonus
#"//*[@id='linkLoginBonus']"

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

    def __isReadyForArena(self):
        cooldown = self.browser.find_element_by_xpath("//*[@id='cooldown_bar_text_arena']")
        if cooldown.text == "Go to the arena":
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

    def __isChestFound(self):
        try:
            notification = self.browser.find_element_by_xpath("//*[@id='blackoutDialognotification']").get_attribute("display")
            if str(notification) != "None":
                chest = self.browser.find_element_by_xpath("//*[@id='linkcancelnotification']")
                chest.click()
        except NoSuchElementException:
            return False
        return True

    def __isHungry(self):
        delay = 3
        try:
            healthStr = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='header_values_hp_bar']"))).get_attribute("data-tooltip").split("\"")[3].split("\\/")

            self.currentHealth = float(healthStr[0])
            self.maxHealth = float(healthStr[1])
            healthPercentage = self.currentHealth / self.maxHealth * 100.0

            if(healthPercentage <= self.minHealthThreshold):
                print("Low health - " + str(healthPercentage) + ". I'm going to heal you now.")
                self.__performHealing()

        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")

    def __performHealing(self):
        self.__menuOption("Overview")
        delay = 3
        try:
            # Make sure that character doll is switched to Standard Battle
            standardBattle = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='char']/div/div[contains(@class, 'doll1')]")))

            button = standardBattle.find_element_by_xpath("./..");
            if "active" not in button.get_attribute("class"):
                button.click()
                self.__menuOption("Overview")

            # Drag food from backpack on the avatar
            # Get all items in a backpack page
            items = self.browser.find_elements_by_xpath("//*[@id='inv']/div")
            character = self.browser.find_element_by_xpath("//*[@id='avatar']/div[2]")

            #Extract the healing values from food and put them to the dictionary with corresponding index
            counter = 0
            itemsDict = {}
            for x in items:
                try:
                    data = str(x.get_attribute("data-tooltip")).split("\"")
                    if "Heal" in data[5]:
                        healValue = int(re.findall('\d+', data[5])[0])
                        itemsDict[counter] = healValue
                    counter+=1
                except NoSuchElementException:
                    print("Can't find data-tooltip for health?")


            healthDifference = self.maxHealth - self.currentHealth

            # Find food that healing value is the closest to the health difference
            if len(itemsDict) > 0:
                key = min(itemsDict, key=itemsDict.get)
                for x in sorted(itemsDict):
                    if itemsDict[x] < healthDifference:
                        key = x
                        break;

                # Perform drag&drop
                ActionChains(self.browser).drag_and_drop(items[key], character).perform()
            else:
                print("You have no food in backpack!")

        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")


        except TimeoutException:
            print("Can heal now!")
            print("Loading took too much time!")
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")


    def isBrowserActive(self):
        try:
            self.browser.title
            return True
        except  WebDriverException:
            return False

    # Find when notification is enabled, and then call the cancel button
    def __cancelNotification(self):
        delay = 3
        try:
            notification = WebDriverWait(self.browser, delay).until(EC.presence_of_all_elements_located(
                                    (By.XPATH, "//*[contains(@id, 'blackoutDialog')]//*[contains(@value, 'Cancel')]")))

            for x in notification:
                x.click()

        except TimeoutException:
            print("Loading took too much time!")
        except StaleElementReferenceException:
            print("Element is not attached to the page document!")
        except ElementNotVisibleException:
            return False
        except NoSuchElementException:
            print("Something went wrong! Report it to the DEVELOPER, PLEASE!")


    def run(self):
        self.__performLogin()

        self.__setDefaultLocations()

        while True:
            # No need to run the script any faster
            time.sleep(1)

            # Check if browser is still opened
            if self.isBrowserActive() == False:
                print("BOT SWITCHED OFF - cya later!")
                break

            # Check if maintenance is happening
            if self.__isMaintenancePerformed():
                continue

            # Perform expeditions & dungeons
            if self.__isReadyForExpedition() and self.expeditionEnabled:
                self.__goToLocation(self.expeditionLocation)
                self.__performExpedition()

            if self.__isReadyForDungeon() and self.dunegonEnabled:
                self.__goToLocation(self.dungeonLocation)
                self.__performDungeon()

            # Perform arenas
            if self.__isReadyForArena() and self.arenaEnabled:
                self.__performArena()

            if self.__isReadyForArena() and self.arenaProvinciarumEnabled:
                self.__performProvinciarumArena()

            if self.__isReadyForCircusTurma() and self.circusProvinciarumEnabled:
                self.__performCircusProvinciarum()

            if self.__isReadyForCircusTurma() and self.circusTurmaEnabled:
                self.__performCircusTurma()

            if self.__isHungry():
                print("Hungry")


# GBot class =============================================================================================

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

