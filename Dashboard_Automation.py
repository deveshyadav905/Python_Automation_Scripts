import pandas as pd
from constant import *
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


class AutomateDashboard:
    """
    AutomateDashboard class for automating dashboard operations.
    """
    ADD_DOMAIN_PAGE = "add_domain"
    ADD_SOURCE_PAGE = "add_source"
    UPDATE_CATEGORY = "update_category"
    UPDATE_COUNTRY = "update_country"

    def __init__(self):
        """
        Initialize AutomateDashboard class with necessary attributes.
        """
        self.logger = self.setup_logger()
        self.driver = self.setup_driver()
        self.LOCAL_USERNAME = LOCAL_USERNAME
        self.LOCAL_PASSWORD = LOCAL_PASSWORD
        self.new_domain_page = DOMAIN_PAGE_URL
        self.new_source_page = SOURCE_PAGE_URL
        self.source_home_page = SOURCE_HOME_PAGE
        self.sheet_path = EXCEL_SHEET_PATH
        self.new_domain_list = self.read_domain_from_excel(domain_name=None, data_type='domain_name')
        self.user_agent = USER_AGENT
    def setup_logger(self):
        """
        Set up the logger for the application.
        """
        logger = logging.getLogger(__name__)
        if not logger.hasHandlers():
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def setup_driver(self):
        """
        Set up the WebDriver with necessary options and ensure it's automatically downloaded if not present.
        """
        options = Options()
        # options.add_argument('--headless')  # Uncomment to run headless
        options.add_argument(f'user-agent={self.user_agent}')
        try:
            # Use webdriver-manager to handle WebDriver binaries
            # service = Service(ChromeDriverManager().install())
            # driver = webdriver.Chrome(service=service, options=options)
            self.logger.info("WebDriver setup complete.")
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {e}")
            raise
        
        # return driver
    

