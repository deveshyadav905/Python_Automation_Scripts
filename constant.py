import os
from os import getenv
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '..', '.env'),override=True)


domain_fields_xpath = {
                        "Name":"//input[@id='id_name']",
                        "Domain":"//input[@id='id_domain']",
                        "Display_Name":'//*[@id="id_display_name"]',
                        "Conection":{"show":"//span[@role='combobox']","select":"//span[@class='select2-results']/ul/li[4]"},
                        "UserAgent":"//textarea[@id='id_user_agent']",
                        "Priority":"//input[@id='id_priority']",
                        "Description":"//textarea[@id='id_description']",
                        "Is_fd_active":"//select[@id='id_is_full_description']/option[@value='1']",
                        "is_proxy":"//select[@id='id_is_proxy']/option[@value='0']" 
                        }

domain_article_xpath = {
                        'fd_xpaths':{"Click_add":"(//tbody)[4]/tr[last()]//a",
                                    "Fd_xpath":"(//tbody)[4]/tr[last()-2]/td[2]/textarea",
                                    "Fd_priority":"(//tbody)[4]/tr[last()-2]/td[6]/input[@type='number']",
                                    "Check_box":"(//tbody)[4]/tr[last()-2]/td[5]/input[@type='checkbox']"},
                        
                        'login_xpaths':{'username':'//*[@id="id_username"]',
                                        'password':'//*[@id="id_password"]',
                                        'login':'//*[@id="login-form"]/div[3]/input'},
                        "save_buttons":{"domin_save+":"(//input[@name='_addanother'])[1]",
                                        "source_save+":"(//input[@name='_addanother'])[1]",
                                        "source_save":"(//input[@name='_save'])[1]"}
                        }

USER_AGENT= "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

LOCAL_USERNAME = getenv('DASH_USERNAME')
LOCAL_PASSWORD = getenv('DASH_PASSWORD')


DOMAIN_PAGE_URL = getenv('DOMAIN_PAGE_URL')
SOURCE_PAGE_URL = getenv('SOURCE_PAGE_URL')
EXCEL_SHEET_PATH = getenv('EXCEL_SHEET_PATH')
SOURCE_HOME_PAGE = getenv('SOURCE_HOME_PAGE','http://dashboard.newsdata.remote/newsdata_feeds/source/')
