"""
Python script for scraping the league scouting report from Hashtag Basketball into a csv file.

Title: Hashtag Basketball League Scouting Report Scraper
Author: Jackie Lu
Date: 2021, Mar. 23

Instructions:
Edit the login_info.json fields to your emails/passwords.
Change the chromedriver path to wherever your chromdriver is located.
The program assumes that you have the json file in the same directory
where you're running this python file.
Remember to activate your conda environment.

References:
I modified the amazon-bot.py file from here: https://github.com/SebaLG/amazon-python-bot
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import json
from time import sleep

class HTBB_Bot():
    def __init__(self):
        # Change chromedriver path if needed
        self.driver = webdriver.Chrome("./chromedriver")

    def go_to_homepage(self):
        self.driver.get('https://hashtagbasketball.com/')
    
    def go_to_login_page(self):
        # Wait until the login page button appears
        wait = WebDriverWait(self.driver, 5)
        login_button = wait.until(EC.element_to_be_clickable(
            (By.ID, 'nav1_LoginStatus2')
            ))
        login_button.click()
    
    # Logs into hashtag basketball
    def log_in(self):
        # Wait until the login button appears
        wait = WebDriverWait(self.driver, 5)
        login_button = wait.until(EC.element_to_be_clickable(
            (By.ID, 'ContentPlaceHolder1_login2_loginbutton')
            ))
        # Find the username and password fields
        username = self.driver.find_element_by_id(
            'ContentPlaceHolder1_login2_username')
        password = self.driver.find_element_by_id(
            'ContentPlaceHolder1_login2_password')
        
        login_info = json.load(open("./login_info.json"))
        # Add username to field
        username.clear()
        username.send_keys(login_info["hashtag_basketball"]["email"])

        # Add password to field
        password.clear()
        password.send_keys(login_info["hashtag_basketball"]["password"])

        # Click the login
        login_button.click()
    
    # Scrolling down on the hashtag basketball league page to see the relevant
    # buttons
    def scroll_down(self, distance):
        self.driver.execute_script("window.scrollTo(0, {})".format(distance)) 
    
    # Create a method for refreshing the yahoo data
    def refresh_league_data(self):
        # This function assumes you only have one league
        # Click the button when it's available
        wait = WebDriverWait(self.driver, 10)
        refresh_button = wait.until(EC.element_to_be_clickable(
            (By.LINK_TEXT, 'Refresh League Data')
            ))
        refresh_button.click()
        
        # Wait for login-signin button
        try:
            yahoo_login_button = wait.until(EC.element_to_be_clickable(
                (By.ID, 'login-signin')
                ))
        except:
            refresh_button.click()
            yahoo_login_button = wait.until(EC.element_to_be_clickable(
                (By.ID, 'login-signin')
                ))
        
        login_info = json.load(open("./login_info.json"))
        
        # Fill in the username field
        username = self.driver.find_element_by_id('login-username')
        username.clear()
        username.send_keys(login_info["yahoo_sports"]["email"])
        
        # Press the 'Next' button
        yahoo_login_button.click()
        
        # Fill in the password
        password = wait.until(EC.element_to_be_clickable(
            (By.ID, 'login-passwd')
            ))
        password.clear()
        password.send_keys(login_info["yahoo_sports"]["password"])
        
        # Press the 'Next' button
        yahoo_login_button = wait.until(EC.element_to_be_clickable(
            (By.ID, 'login-signin')
            ))
        yahoo_login_button.click()
        
        # Click the OAuth button
        yahoo_oauth_button = wait.until(EC.element_to_be_clickable(
            (By.ID, 'oauth2-agree')
            ))
        yahoo_oauth_button.click()
        
        
    def download_league_scouting_report(self):
        # Click the league scouting report button when available
        wait = WebDriverWait(self.driver, 10)
        report_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[@id=\"ContentPlaceHolder1_Panel1\"]/div/div[2]/div/div/p[8]/a")
                )
            )
        
        report_button.click()
        try:
            while (report_button):
                sleep(1)
                report_button.click()
        except:
            pass
        
        wait.until(EC.element_to_be_clickable(
            (By.ID, 'ContentPlaceHolder1_DropDownList5')
            ))
        
        select_1 = Select(
            self.driver.find_element_by_id('ContentPlaceHolder1_DropDownList5')
            )
        # select by visible text
        select_1.select_by_visible_text('Base rankings on top 13 players on each team')
        
        sleep(3)
        select_2 = Select(
            self.driver.find_element_by_id('ContentPlaceHolder1_DropDownList6')
            )
        # select by visible text
        select_2.select_by_visible_text('Included injured players in rankings')
        
        # JavaScript code
        sleep(3)
        self.driver.execute_script(
            """
            // Select all the black squares
            kbds = document.getElementsByTagName('kbd');
            // Make them invisible
            for (let i = 0, max = kbds.length; i < max; i++) {
                kbds[i].style.display = 'none';
                }
            """)
        
        # Scrape the table into a csv file
        # Find the table
        report = self.driver.find_element_by_id(
            'ContentPlaceHolder1_GridView4'
            ).find_element_by_tag_name("tbody")
        
        # Create the csv file
        with open('rankings.csv', 'w', newline='') as csvfile:
            wr = csv.writer(csvfile)
            for i, row in enumerate(
                # Find the table rows
                report.find_elements_by_css_selector('tr')
                ):
                # Write header row
                if i == 0:
                    wr.writerow(["team name", "total score", "fgp",
                                 "ftp", "tpm", "pts", "reb", "ast",
                                 "stl", "blk", "to"])
                # Ignore the repeated header rows from the table
                elif i % 5 != 0:
                    # If it's not the fifth row (headers repeat every 5 rows)
                    # then write the row
                    wr.writerow([d.text for d in row.find_elements_by_css_selector('td')][1:])
        
        
# Bot commands
bot = HTBB_Bot()
bot.go_to_homepage()
bot.go_to_login_page()
bot.log_in()
bot.scroll_down(distance = 250)
bot.refresh_league_data()
bot.download_league_scouting_report()