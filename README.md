# Automation & Web Scraping with Python, Selenium, and Scrapy
## Overview
This repository contains a collection of Python-based automation scripts focused on web scraping, data extraction, and browser automation. Built using Selenium, Scrapy, and various database management systems, these scripts demonstrate my expertise in:

Automating web interactions using Selenium.
Efficient web scraping with Scrapy.
Database management using MongoDB, Redis, and MySQL.
Data handling and caching for large-scale web scraping.
These scripts are part of a custom internal framework and are tailored to specific use cases, demonstrating proficiency in handling dynamic content, scraping workflows, and automating repetitive tasks.

## Key Technologies
 Python 3.x: Core language for all scripts. 
 Selenium: Automates browser actions such as login, form submission, and tab management.
 Scrapy: Used for large-scale web scraping, capable of handling complex data extraction scenarios.
 MongoDB, Redis, MySQL: For data storage, caching, and efficient data management.
 Pandas: For handling Excel files and data processing.
 PrettyTable: For presenting results in a clean, readable format.
 Core Features
## Web Automation with Selenium:

  Automates tasks such as logging into dashboards, interacting with dynamic content, and managing browser tabs.
  Uses Selenium to open multiple URLs, extract images, and process content in real-time.
  Efficient Web Scraping with Scrapy:

  Advanced web scraping setup using Scrapy for fast, scalable scraping of websites.
  Handles dynamic websites and processes data efficiently using a custom MongoDB storage setup.
## Data Management:

  Utilizes MongoDB, Redis, and MySQL to store, cache, and manage data scraped from the web.
  Automatically clears pre-existing data from MongoDB and Redis to ensure clean, fresh results.
  Document and Article Processing:

  Fetches articles and images, processes them, and opens them in a browser for further review.
  Displays detailed stats for scraped documents (e.g., total docs, images extracted, descriptions processed) using PrettyTable.
## How It Works
  The main script automates web scraping processes and performs the following actions:

  Logs into a dashboard using provided credentials.
  Clears existing data from databases and caches.
  Runs the web scraper to collect data.
  Processes the scraped data and displays relevant statistics.
  Opens articles in a browser and allows for review of images and full descriptions.
  Custom exception handling and logging are implemented to ensure smooth execution and easy debugging.

## Terminal Commands:
  bash
  Copy code
## Clone the repository
  $ git clone https://github.com/your-username/automation-webscraping

## Install dependencies
  $ pip install -r requirements.txt

## Run the main script for a specific spider
  $ python main_script.py spider_name

## Example: Running for multiple spiders
  $ python main_script.py spider_1 spider_2 spider_3
  The script will automatically log into the required dashboard, clear data, start the web scraping process, and display stats in the terminal.
  Terminal Output Example:
  bash
  Copy code  
  $ python main_script.py example_spider

## Starting spider: example_spider

  Dropping all MongoDB collections before starting the spider...
  Collection elasticfeeds dropped.
  All MongoDB collections cleared successfully.
  Pre-existing data cleared.

##  Fetching document details for spider - example_spider

            +-------------------+-------+
            | Stat Type         | Count |
            +-------------------+-------+
            | Total_docs        | 500   |
            | Image_extracted   | 350   |
            | Image_not_extracted| 150   |
            | FD_extracted      | 400   |
            | FD_not_extracted  | 100   |
            +-------------------+-------+

# Skills Demonstrated
  Advanced Python Programming: Leveraging Python’s powerful libraries for automation, data processing, and error handling.
  Web Scraping Expertise: Extracting complex data using Scrapy, managing browser automation with Selenium, and handling large datasets.
  Database Management: Integrating multiple databases for caching, data storage, and retrieval.
  Automation: Building scripts that automate repetitive tasks, improving efficiency and scalability in data collection processes.
  Handling Dynamic Content: Managing dynamic web pages and content using Selenium to interact with forms, AJAX calls, and JavaScript-rendered elements.
# Contact
  This repository is part of my portfolio to demonstrate my skills in automation, web scraping, and data management. For any inquiries or potential collaborations, feel free to reach out!

