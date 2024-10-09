#import sys,shutil
#import pandas as pd
#from prettytable import PrettyTable
#from selenium import webdriver
#from connections import get_mongo_conn, get_msq_conn, close_mysql_conn, close_mongo_conn, reddis_conn, reddis_conn_cache
#import manage
from config import *
# Define colors for output
Red = '\x1b[31m'
Green = '\x1b[32m'
Yellow = '\x1b[33m'
Blue = '\x1b[34m'
Magenta = '\x1b[35m'
Cyan = '\x1b[36m'
RESET = '\x1b[0m'

def print_colored(text, color):
    """Utility to print colored text."""
    print(f'{color}{text}{RESET}')
def print_colored_centered(text, color):
    """Utility to print colored text in the center of the terminal."""
    terminal_width = shutil.get_terminal_size().columns  # Get terminal width
    centered_text = text.center(terminal_width)  # Center the text based on terminal width
    print(f'{color}{centered_text}{RESET}')

class SpiderRunCheck:
    LOCAL_USERNAME = LOCAL_USERNAME
    LOCAL_PASSWORD = LOCAL_PASSWORD
    count = 1
    
    def __init__(self, spider_name=None, is_timeout=False):
        """Initializes the SpiderRunCheck class."""
        self.spider_name = spider_name
        self.is_timeout = is_timeout
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.db, self.cursor = get_msq_conn()
    
    def login_to_dashboard(self, credentials:tuple, domain_info:tuple):
        """Logs into the dashboard using provided credentials."""
        username, password = credentials
        domain_id, domain_name = domain_info
        try:
            # Open the login page
            self.driver.get(REMOTE_DASH_URL.format(domain_id))
            # Input credentials and log in
            self.driver.find_element('xpath', '//*[@id="id_username"]').send_keys(username)
            self.driver.find_element('xpath', '//*[@id="id_password"]').send_keys(password)
            self.driver.find_element('xpath', '//*[@id="login-form"]/div[3]/input').click()
            print_colored(f"Logged in successfully to domain: {domain_name}", Green)
        except Exception as e:
            print_colored(f"Login failed for domain: {domain_name}. Error: {str(e)}", Red)
            raise
    def close_all_tabs(self):
        """Closes all open tabs in the browser."""
        try:
            # Get all window handles
            window_handles = self.driver.window_handles

            # Iterate over all window handles and close each one
            for handle in window_handles:
                self.driver.switch_to.window(handle)  # Switch to the tab
                self.driver.close()  # Close the current tab

            # Switch back to the original window (if needed)
            self.driver.switch_to.window(window_handles[0])  # Switch back to the first tab, if there is one
            
            print_colored("All tabs closed successfully.", Green)
        except Exception as e:
            print_colored(f"Error closing tabs: {str(e)}", Red)
        finally:
            self.driver.close()
            self.driver.quit()
    def clear_pre_existing_data_from_sources(self):
        """Clears data from Redis, MongoDB, and cache."""
        try:
            reddis_conn.flushdb()
            reddis_conn_cache.flushdb()
            manage.delete_data_cache(delete_all=True)
            mongo_client, db, collection = get_mongo_conn(coll=self.spider_name)
            collection.drop()
            close_mongo_conn(mongo_client)
            print_colored("Pre-existing data cleared.", Green)
        except Exception as e:
            print_colored(f"Error clearing pre-existing data: {str(e)}", Red)
            raise
    
    def display_spider_stats(self):
        """Fetches and displays stats from MongoDB."""
        mongo_client, db, collection = get_mongo_conn(coll='elasticfeeds')
        try:
            total_docs = collection.count_documents({})
            if total_docs == 0:
                print_colored_centered("No documents found in the collection.", Red)
                # input("Press Enter to continue with another spider")
                if input("Enter 0 to close all browser Tabs | Enter to countinue") ==0:
                    self.close_all_tabs()
                raise
                
            # Document stats
            spider_stats = {
                'Total_docs': total_docs,
                'Image_extracted': collection.count_documents({"has_image": True}),
                'Image_not_extracted': collection.count_documents({"has_image": False}),
                'Fd_extracted': collection.count_documents({"full_description_status": 1}),
                'Fd_not_extracted': collection.count_documents({"full_description_status": 3})
            }

            # Display stats using PrettyTable
            table = PrettyTable()
            table.field_names = ['Stat Type', 'Count']
            for key, value in spider_stats.items():
                table.add_row([key, value])
                
            print_colored_centered(f" ********* Loading Doc  Details for spider - {self.spider_name} ********* ",Red)
            
            print(table)
            
            self.process_spider_documents(collection)
            if input("Enter 0 to close all browser Tabs") ==0:
                self.close_all_tabs()
        except Exception as e:
            print_colored(f"Error fetching spider stats: {str(e)}", Red)
        finally:
            close_mongo_conn(mongo_client)
    
    def process_spider_documents(self, collection):
        """Fetches and processes documents for further actions."""
        try:
            self.fetch_and_open_articles(collection, {"has_image": True}, "Articles with Images")
            self.fetch_and_open_articles(collection, {"has_image": False}, "Articles without Images")
            self.fetch_and_open_articles(collection, {"full_description_status": 1}, "Articles with Full Descriptions")
            self.fetch_and_open_articles(collection, {"full_description_status": 3}, "Articles missing Full Descriptions")        
        except Exception as e:
            print_colored(f"Error processing documents: {str(e)}", Red)
    
    def fetch_and_open_articles(self, collection, query, description):
        """Fetches articles based on a query and opens them in the browser."""
        
        print_colored_centered(f"Fetching {description}...", Blue)
        docs = collection.find(query).limit(5)
        urls_to_open = []
        
        for doc in docs:
            urls_to_open.append(doc.get('link'))
            
            if query == {"full_description_status": 1}:
                print_colored_centered(f"Article Num {self.count}",Red)
                print_colored(doc.get("full_description"),Green)
                self.count+=1
                
            elif doc.get('has_image'):
                print_colored(f"Image URL: {doc.get('image_url')}", Cyan)        
                
        self.open_links_in_browser(urls_to_open)
        input("Press Space | Enter to continue...")

        
    
    def open_links_in_browser(self, urls):
        """Opens the list of URLs in new tabs."""
        for url in urls:
            self.driver.execute_script(f"window.open('{url}');")    
            print(f"Opened: {url}")

    def start_spider_scraping(self):
        """Starts the spider using manage.start_scraping."""
        try:
            # Check if timeout is specified and start the spider accordingly
            if self.is_timeout:
                manage.start_scraping(spider_names=[self.spider_name], is_timeout=self.is_timeout)
            else:
                manage.start_scraping(spider_names=[self.spider_name])
            print_colored(f"Started spider: {self.spider_name}", Green)
        except Exception as e:
            print_colored(f"Error starting spider: {str(e)}", Red)

    def execute_spider_check(self):
        """Runs all checks for the spider."""
        try:
            # Fetch domain information from MySQL
            self.cursor.execute(f"SELECT id, name FROM domain WHERE name = '{self.spider_name}'")
            domains = self.cursor.fetchall()

            # Log in to each domain's dashboard and clear data
            for domain_id, domain_name in domains:
                self.login_to_dashboard((self.LOCAL_USERNAME, self.LOCAL_PASSWORD), (domain_id, domain_name))

            # Clear all MongoDB collections before running the spider
            print_colored("Dropping all MongoDB collections before starting the spider...", Yellow)
            mongo_client, db, _ = get_mongo_conn(coll='elasticfeeds') 
            collection_names = db.list_collection_names()  # Get all collections in the database

            for collection_name in collection_names:
                db[collection_name].drop()  # Drop each collection
                print_colored(f"Collection {collection_name} dropped.", Cyan)

            close_mongo_conn(mongo_client)
            print_colored("All MongoDB collections cleared successfully.", Green)

            # Clear Redis, cache, and other pre-existing data
            self.clear_pre_existing_data_from_sources()

            # Start spider scraping
            self.start_spider_scraping()

            # Fetch and display spider stats after scraping
            self.display_spider_stats()

        except Exception as e:
            print_colored(f"Error during spider check: {str(e)}", Red)
        finally:
            self.driver.quit()
            close_mysql_conn(self.db, self.cursor)
            
if __name__ == "__main__":
    def spider_tester():
        """Starts the scraping process for each spider."""
        try:
            # Check if spider names are passed as command-line arguments
            if len(sys.argv) > 1:
                # Spider names are passed as arguments
                spider_names = sys.argv[1:]  # Get all command-line arguments except the script name
                print_colored(f"Spider names provided as arguments: {spider_names}", Green)
            else:
                # No spider names provided as arguments, read from the Excel sheet
                print_colored("No spider names provided as arguments. Reading from the Excel sheet...", Yellow)
                spider_excel = pd.read_excel('/home/charanjeet/Documents/update.xlsx')
                spider_names = spider_excel['spider_name'].tolist()  # Get spider names from the Excel sheet

            # Start the spider for each name
            for spider_name in spider_names:
                print_colored(f"Starting spider: {spider_name}", Cyan)
                obj = SpiderRunCheck(spider_name=spider_name, is_timeout=False)
                obj.execute_spider_check()
                input("Enter to continue with next spider")
        except Exception as e:
            print_colored(f"Error in scraping: {str(e)}", Red)
    spider_tester()
