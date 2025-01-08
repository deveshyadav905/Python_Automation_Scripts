import pandas as pd
from constant import *
import logging,time,math
from selenium import webdriver
from spider_file_creator import spider_file_creator
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class AutomateDashboard:
    """
    AutomateDashboard class for automating dashboard operations.
    """
    # Initialize XPaths from domain_article_xpath dictionary
    # CLICK_ADD_XPATH = domain_article_xpath['fd_xpaths']['Click_add']
    # FD_XPATH_XPATH = domain_article_xpath['fd_xpaths']['Fd_xpath']
    # FD_PRIORITY_XPATH = domain_article_xpath['fd_xpaths']['Fd_priority']
    # CHECK_BOX_XPATH = domain_article_xpath['fd_xpaths']['Check_box']
    # USER_NAME_XPATH = domain_article_xpath['login_xpaths']['username']
    # PASS_XPATH = domain_article_xpath['login_xpaths']['password']
    # LOGIN_BUTTON = domain_article_xpath['login_xpaths']['login']
    # DOMAIN_SAVE_BUTTON = domain_article_xpath["save_buttons"]["domin_save+"]
    # SOURCE_SAVE_BUTTON = domain_article_xpath["save_buttons"]["source_save+"]

    ADD_DOMAIN_PAGE = "add_domain"
    ADD_SOURCE_PAGE = "add_source"
    UPDATE_CATEGORY = "update_category"
    UPDATE_COUNTRY = "update_country"
    

    def __init__(self):
        """domain
        Initialize AutomateDashboard class with necessary attributes.
        """
        self.logger = logging.getLogger(__name__)
        # Configure logger settings
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.LOCAL_USERNAME = LOCAL_USERNAME
        self.LOCAL_PASSWORD = LOCAL_PASSWORD
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless') 
        self.driver = webdriver.Chrome(options=self.options)
        self.new_domain_page = DOMAIN_PAGE_URL
        self.new_source_page = SOURCE_PAGE_URL
        self.source_home_page = SOURCE_HOME_PAGE
        self.sheet_path = EXCEL_SHEET_PATH
        self.new_domain_list = self.read_domain_from_excel(domain_name=None, data_type='domain_name')
        self.user_agent = USER_AGENT

    def read_domain_from_excel(self, domain_name=None, data_type=None):
        """
        Reads domain data from Excel file based on the provided domain name and data type.
        """
        try:
            if data_type == 'domain_name':
                df = pd.read_excel(self.sheet_path, sheet_name='Domains')
                domain_lists = df['Name'].to_list()
                return domain_lists
            elif data_type == 'domain_data':
                df2 = pd.read_excel(self.sheet_path, sheet_name='Domains')
                entry = df2[df2['Name'] == domain_name]
                if not entry.empty:
                    domain_data_dict = entry.to_dict(orient='records')[0]
                    return domain_data_dict
            elif data_type == 'xpath_data':
                df3 = pd.read_excel(self.sheet_path, sheet_name='Xpath')
                filtered_rows = df3[(df3['Name'] == domain_name)]
                return filtered_rows
            elif data_type == 'source_data':
                df4 = pd.read_excel(self.sheet_path, sheet_name='Sources')
                return df4
        except Exception as e:
            self.logger.error(f"Error reading Excel file: {e}")
            raise

    def click_element_by_xpath(self, xpath):
        """
        Clicks the element using the provided XPath.
        """
        try:
            element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
        except Exception as e:
            self.logger.error(f"Error clicking element with XPath '{xpath}': {e}")
            raise

    def send_keys_to_element_by_xpath(self, xpath, keys):
        """
        Sends keys to the element using the provided XPath.
        """
        try:
            element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            # if isinstance(keys, int):
            element.clear()
            if not keys =='nan':
                element.send_keys(keys)
            return element
        except Exception as e:
            self.logger.error(f"Error sending keys '{keys}' to element with XPath '{xpath}': {e}")
            raise
    def _select_options_and_enter_text(self, option_text=None, combobox_xpath=None, searchbox_xpath=None, 
                                        suggestion_xpath=None, staus_xpath=None, field_xpath=None, text=None):
        """
        Selects options such as languages, countries, or categories and enters text in a field.
        """
        suggestion_xpath2 = "/html/body/span/span/span[2]/ul/li[2]"
        try:
            if option_text is not None:
                options = [x.strip() for x in option_text.split(',')]
                for option in options:
                    self.click_element_by_xpath(combobox_xpath)
                    time.sleep(0.5)
                    self.send_keys_to_element_by_xpath(searchbox_xpath, option)
                    time.sleep(0.5)
                    suggestion_text = self.driver.find_element("xpath", suggestion_xpath).text
                    try:
                        suggestion_text2 = self.driver.find_element("xpath", suggestion_xpath2).text
                    except:
                        suggestion_text2=None
                    if suggestion_text == option:
                        self.click_element_by_xpath(suggestion_xpath)
                    elif suggestion_text2 == option:
                        self.click_element_by_xpath(suggestion_xpath2)
                    else:
                        self.logger.error(f" ======  {option} not match in search list {suggestion_text}")
                        return False
                    
            if text and field_xpath:
                self.send_keys_to_element_by_xpath(field_xpath, text)
                return True
            else:
                return True    
                
        except Exception as e:
            if combobox_xpath:
                option_name = combobox_xpath.split("[")[1].split("]")[0]
                self.logger.error(f"Error selecting {option_name} and entering text: {e}")
                raise
    def fill_login_credentials(self):
        """
        Fills the login credentials.
        """
        if not self.LOCAL_PASSWORD =="" and self.LOCAL_USERNAME == "":
            self.logger.info(f"Login credentials not aviable")
            return False
        try:
            self.send_keys_to_element_by_xpath(domain_article_xpath['login_xpaths']['username'], self.LOCAL_USERNAME)
            self.send_keys_to_element_by_xpath(domain_article_xpath['login_xpaths']['password'], self.LOCAL_PASSWORD)
            self.click_element_by_xpath(domain_article_xpath['login_xpaths']['login'])
            return True
        except Exception as e:
            self.logger.error(f"Failed in filling login credentials: {e}")
            raise

    def add_new_domain(self, domain_name):
        """
        Adds a new domain.
        """
        try:
            # Create spider file for the News domains
            spider_file_creator(spider_name=domain_name, logger=self.logger)
            
            domains_data = self.read_domain_from_excel(domain_name=domain_name, data_type='domain_data')
                
            # Ensure required columns are not empty
            required_columns = ['Name', 'Domain', 'Display_Name', 'Priority', 'Description']
            if any(pd.isna(domains_data[col]) for col in required_columns):
                self.logger.error(f"Incomplete data for domain: {domains_data}")
                return False
            self.logger.info(f"Adding domain: {domain_name} with details: {domains_data}")
            for field_key, xpath in domain_fields_xpath.items():
                if field_key == "Conection":
                    self.click_element_by_xpath(xpath["show"])
                    time.sleep(0.5)
                    self.click_element_by_xpath(xpath["select"])
                elif field_key == "UserAgent" and str(domains_data[field_key]) == "UserAgent":
                    self.send_keys_to_element_by_xpath(xpath, self.user_agent)
                elif field_key == "Is_fd_active":
                    self.click_element_by_xpath(xpath)
                elif field_key == 'is_proxy':
                    self.click_element_by_xpath(xpath)
                else:
                    self.send_keys_to_element_by_xpath(xpath, str(domains_data[field_key]))
            # Save the domain
            if self.save_domains_xpath(domain_name):
                    return self.save_new_domain()
            else:
                return False
        except Exception as e:
            self.logger.error(f"An error occurred while adding domain {domain_name}: {e}")
            return False
    def save_new_domain(self):
        """
        Saves the new domain.
        """
        self.click_element_by_xpath(domain_article_xpath["save_buttons"]["domin_save+"])
        try:
            domain_error = self.driver.find_element("xpath", '//*[@id="content-main"]/form/div/p')
            domain_error = domain_error.text
            if domain_error:
                duplicate_error = self.driver.find_element("xpath", '//*[@id="domain_form"]/div/fieldset/div[1]/div').text
                if duplicate_error:
                    self.logger.error(str(duplicate_error))
                self.logger.error(domain_error)
                return False 
        except Exception as e:
           return True


    def save_domains_xpath(self, domain_name):
        """
        Saves domain XPaths.
        """
        try:
            xpath_dframe = self.read_domain_from_excel(domain_name=domain_name, data_type='xpath_data')
            if not xpath_dframe.empty:
                self.add_xpaths(xpath_dframe["Fd_Xpath"], xpath_dframe['Fd_priority'])
                self.add_xpaths(xpath_dframe["Image_Xpath"], xpath_dframe['Img_priority'])
                return True
            else:
                self.logger.error(f"No XPaths found for domain '{domain_name}'")
                return False
        except Exception as e:
            self.logger.error(f"Error in Xpath: {e}")
            return False

    def add_xpaths(self, xpaths, priorities):
        """
        Adds XPaths.
        """
        try:
            for xpath, priority in zip(xpaths, priorities):
                if isinstance(xpath, str) and not math.isnan(priority):
                    self.click_element_by_xpath(domain_article_xpath['fd_xpaths']['Click_add'])
                    time.sleep(0.5)
                    self.send_keys_to_element_by_xpath(domain_article_xpath['fd_xpaths']['Fd_xpath'],xpath)
                    for tag in ["img", "image", "@href"]:
                        if tag in xpath:
                            self.click_element_by_xpath(domain_article_xpath['fd_xpaths']['Check_box'])
                            break
                    self.send_keys_to_element_by_xpath(domain_article_xpath['fd_xpaths']['Fd_priority'], int(priority))
        except Exception as e:
            self.logger.error(f"Error adding XPaths: {e}")
            raise
    
    def add_country(self, source_row):
        # Extract and clean the list of new countries
        country_list = source_row['Country']
        new_countries = [x.strip() for x in country_list.split(',')]

        # Define XPaths for elements
        combobox_xpath = '//*[@id="source_form"]/div/fieldset/div[5]/div/div[1]/div/div/span/span[1]/span/ul'
        searchbox_xpath = '//*[@id="source_form"]/div/fieldset/div[5]/div/div[1]/div/div/span/span[1]/span/ul/li/input'
        suggestion_xpath = "//span[@class='select2-results']/ul/li[1]"
        suggestion_xpath2 = "//span[@class='select2-results']/ul/li[2]"

        # Update existing countries if in update mode
        if page == self.UPDATE_COUNTRY:
            old_countries = self.driver.find_elements(By.XPATH, "//div[@class='form-row field-country_id field-ai_country']//ul[@class='select2-selection__rendered']/li[@class='select2-selection__choice']")
            for country in old_countries:
                country = country.text.lstrip('×')
                if country not in new_countries:
                    time.sleep(0.4)
                    self.click_element_by_xpath(".//span[@class='select2-selection__choice__remove']")
                else:
                    new_countries.remove(country)

        # Add new countries
        if new_countries:
            self.click_element_by_xpath(combobox_xpath)
            self.send_keys_to_element_by_xpath(searchbox_xpath, Keys.CONTROL + "a")  # Select all
            self.send_keys_to_element_by_xpath(searchbox_xpath, Keys.DELETE)  # Clear the field
            for option in new_countries:
                self.send_keys_to_element_by_xpath(searchbox_xpath, option)
                time.sleep(1.5)
                suggestion_text = self.driver.find_element("xpath", suggestion_xpath).text
                try:
                    suggestion_text2 = self.driver.find_element("xpath", suggestion_xpath2).text
                except:
                    suggestion_text2 = ''

                if not suggestion_text and not suggestion_text2:
                    break
                
                if suggestion_text == option:
                    self.click_element_by_xpath(suggestion_xpath)
                elif suggestion_text2 == option:
                    suggestion_text = suggestion_text2
                    self.click_element_by_xpath(suggestion_xpath2)
                else:
                    self.logger.error(f"Country doesn't match {option} in database {suggestion_text}")
                    return False
        return True

    def add_category(self, source_row):
        # Extract and clean the list of new categories
        category_list = source_row['Category']
        new_categories = [x.strip() for x in category_list.split(',')]
        
        # Define XPaths for elements
        combobox_xpath = '//*[@id="source_form"]/div/fieldset/div[6]/div/div[1]/div/div/span/span[1]/span/ul'
        searchbox_xpath = '//*[@id="source_form"]/div/fieldset/div[6]/div/div[1]/div/div/span/span[1]/span/ul/li/input'
        suggestion_xpath = "//span[@class='select2-results']/ul/li[1]"
        # Update existing categories if in update mode
        if page == self.UPDATE_CATEGORY:
            old_categories = self.driver.find_elements(By.XPATH, "//div[@class='form-row field-category_id field-ai_category']//ul[@class='select2-selection__rendered']/li[@class='select2-selection__choice']")

            for category in old_categories:
                category = category.text.lstrip('×')
                if category not in new_categories:
                    time.sleep(0.4)
                    # Log the new and existing categories
                    self.logger.info(f"{'*'*8} New Verified Category is - {new_categories}\n Already Added Category - {category}{'*'*8} --- category updated")
                    self.click_element_by_xpath("//div[@class='form-row field-category_id field-ai_category']//span[@class='select2-selection__choice__remove']")
                else:
                    new_categories.remove(category)
        # Add new categories
        if new_categories:
            self.click_element_by_xpath(combobox_xpath)
            self.send_keys_to_element_by_xpath(searchbox_xpath, Keys.CONTROL + "a")  # Select all
            self.send_keys_to_element_by_xpath(searchbox_xpath, Keys.DELETE)  # Clear the field
            for option in new_categories:
                self.send_keys_to_element_by_xpath(searchbox_xpath, option)
                time.sleep(0.5)
                suggestion_text = self.driver.find_element("xpath", suggestion_xpath).text
                if suggestion_text == option:
                    self.click_element_by_xpath(suggestion_xpath)
                    self.send_keys_to_element_by_xpath(searchbox_xpath, Keys.RETURN)
                else:
                    self.logger.error(f"Category doesn't match {option} in database {suggestion_text}")
                    return False
        return True

    def _add_single_source(self, source_row):
        """
        Adds a single source.
        """
        try:
            if any(pd.isna(source_row[column]) for column in ['Name', 'Source_Link', 'Language', 'Country', 'Category']):
                self.logger.error(f"Incomplete data for source: {source_row}")
                return False

            self.logger.info(f"Adding source: {source_row}")

            # For selecting Domain name and entering Source Link
            if not self._select_options_and_enter_text(
                option_text=source_row['Name'],
                combobox_xpath="(//span[@role='combobox'])[1]",
                searchbox_xpath='/html/body/span/span/span[1]/input',
                suggestion_xpath="//span[@class='select2-results']/ul/li[1]",
                field_xpath="//input[@id='id_url']",
                text=source_row['Source_Link']
            ):
                raise ValueError("Failed to select options and enter text for source link")

            # Selects the status option.
            status_xpath = '//*[@id="id_feed_status"]/option[1]'
            self.click_element_by_xpath(status_xpath)

            if not self._select_options_and_enter_text(
                option_text=source_row['Language'],
                combobox_xpath="(//span[@role='combobox'])[2]",
                searchbox_xpath="(//input[@role='searchbox'])[3]",
                suggestion_xpath="//span[@class='select2-results']/ul/li[1]"
            ):
                raise ValueError("Failed to select options and enter text for language")

            if not self.add_country(source_row):
                return False
            time.sleep(0.3)
            if not self.add_category(source_row):
                return False
            # Click save button after filling source details
            self.click_element_by_xpath(domain_article_xpath['save_buttons']['source_save+'])

            # Handling error on save if duplicate or any missing fields
            try:
                source_error = self.driver.find_element("xpath", "//*[@id='source_form']/div/p").text
                if source_error:
                    duplicate_error = self.driver.find_element("xpath", '/html/body/div/div[2]/div/div[1]/div/form/div/fieldset/div[2]').text
                    self.logger.error(str(duplicate_error))
                    self.logger.error(source_error)
                    return False
            except NoSuchElementException:
                return True
        
        except Exception as e:
            self.logger.error(f"Error adding source {source_row}: {e}")
            return False

    def update_category_country(self,source_row,page):
        try:
            # if any(pd.isna(source_row[column]) for column in ['Name', 'Source_Link']):
            #     self.logger.error(f"Incomplete data for source: {source_row}")
            #     return False
            self.logger.info(f"Updating category of source: {source_row}")
            self.send_keys_to_element_by_xpath("//input[@id='searchbar']",keys=source_row['Source_Link']) # send url to search box
            time.sleep(0.1)
            self.click_element_by_xpath("//input[@value='Search']") # click on search button 
            time.sleep(0.3)
            self.click_element_by_xpath('//*[@id="result_list"]/tbody/tr/th/a')  # Click on search result to open url 
            if page == self.UPDATE_CATEGORY:
                if any(pd.isna(source_row[column]) for column in ['Source_Link','Category']):
                    self.logger.error(f"Incomplete data for source: {source_row}")
                    return False
                time.sleep(0.3)
                
                if not self.add_category(source_row):
                    return False
            if page == self.UPDATE_COUNTRY:
                if any(pd.isna(source_row[column]) for column in ['Source_Link','Country']):
                    self.logger.error(f"Incomplete data for source: {source_row}")
                    return False 
                if not self.add_country(source_row):
                    return False
            # Click save button after filling source details
            time.sleep(0.3)
            self.click_element_by_xpath(domain_article_xpath['save_buttons']['source_save'])
            # Handling error on save if duplicate or any missing fields
            try:
                source_error = self.driver.find_element("xpath", "//*[@id='source_form']/div/p").text
                if source_error:
                    duplicate_error = self.driver.find_element("xpath", '/html/body/div/div[2]/div/div[1]/div/form/div/fieldset/div[2]').text
                    self.logger.error(str(duplicate_error))
                    self.logger.error(source_error)
                    return False
            except NoSuchElementException:
                return True
        except Exception as e:
            self.logger.error(f"Error While Updating  Source {source_row}: {e}")
            return False

    def update_country(self,source_row):
        pass
        
    def login_to_dashboard(self, page):
        """
        Login to the dashboard.
        """
        try:
            if page == self.ADD_DOMAIN_PAGE:
                self.driver.get(self.new_domain_page)
            elif page == self.ADD_SOURCE_PAGE:
                self.driver.get(self.new_source_page)
            else: 
                self.driver.get(self.source_home_page)
            if self.fill_login_credentials():
                self.logger.info("------- LOGIN SUCCESSFULY -------")        
            if page == self.ADD_DOMAIN_PAGE:
                for domain_name in self.new_domain_list if self.new_domain_list else self.logger.error("Domain list is empty"):
                    if not  self.add_new_domain(domain_name=domain_name):
                        self.logger.error("--- Domain add proccess has stoped please check error in log")
                        break
                    self.logger.info("--- Domain added successfully") 
                self.driver.close()
            else:
                source_dataframe = self.read_domain_from_excel(domain_name=None, data_type='source_data')
                if source_dataframe.empty:
                    return self.logger.error("No source data found in Excel file")
                for index, source_row in source_dataframe.iterrows():
                    if page == self.ADD_SOURCE_PAGE:
                        if not self._add_single_source(source_row):
                            self.logger.error("--- Source add proccess has stoped please check error in log")
                            break
                        self.logger.info("--- Source added successfully")
                    elif page == self.UPDATE_CATEGORY:
                        if not self.update_category_country(source_row,page):
                            self.logger.error("--- Source Category Update proccess has stoped please check error in log")
                            break
                        self.logger.info("--- Source Category Update successfully")
                    else: 
                        self.logger.info("Dashboard page not found")
                self.driver.close()
                
        except Exception as e:
            self.logger.error(f'Error while trying to fill login credentials: {str(e)}')
            raise
    


obj = AutomateDashboard()
action_input = int(input(" ===== ENTER 1 FOR Domain | 2 FOR SOURCE | 3 FOR UPDATE_COUNTRY, 4 FOR UPDATE_CATEGORY"))

if action_input == 1:
    page = AutomateDashboard.ADD_DOMAIN_PAGE
elif action_input == 2: 
    page = AutomateDashboard.ADD_SOURCE_PAGE
elif action_input == 3: 
    page = AutomateDashboard.UPDATE_COUNTRY
elif action_input == 4: 
    page = AutomateDashboard.UPDATE_CATEGORY
else:
    obj.logger.info("Choose one from  [1,2,3,4]")
obj.login_to_dashboard(page=page)