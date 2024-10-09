# Automaton-Sripts
Automation & Web Scraping with Python, Selenium, and Scrapy
Overview
This repository contains a collection of Python-based automation scripts focused on web scraping, data extraction, and browser automation. Built using Selenium, Scrapy, and various database management systems, these scripts demonstrate my expertise in:

Automating web interactions using Selenium.
Efficient web scraping with Scrapy.
Database management using MongoDB, Redis, and MySQL.
Data handling and caching for large-scale web scraping.
These scripts are part of a custom internal framework and are tailored to specific use cases, demonstrating proficiency in handling dynamic content, scraping workflows, and automating repetitive tasks.

Key Technologies
Python 3.x: Core language for all scripts.
Selenium: Automates browser actions such as login, form submission, and tab management.
Scrapy: Used for large-scale web scraping, capable of handling complex data extraction scenarios.
MongoDB, Redis, MySQL: For data storage, caching, and efficient data management.
Pandas: For handling Excel files and data processing.
PrettyTable: For presenting results in a clean, readable format.
Core Features
Web Automation with Selenium:

Automates tasks such as logging into dashboards, interacting with dynamic content, and managing browser tabs.
Uses Selenium to open multiple URLs, extract images, and process content in real-time.
Efficient Web Scraping with Scrapy:

Advanced web scraping setup using Scrapy for fast, scalable scraping of websites.
Handles dynamic websites and processes data efficiently using a custom MongoDB storage setup.
Data Management:

Utilizes MongoDB, Redis, and MySQL to store, cache, and manage data scraped from the web.
Automatically clears pre-existing data from MongoDB and Redis to ensure clean, fresh results.
Document and Article Processing:

Fetches articles and images, processes them, and opens them in a browser for further review.
Displays detailed stats for scraped documents (e.g., total docs, images extracted, descriptions processed) using PrettyTable.
How It Works
The main script automates web scraping processes and performs the following actions:
Logs into a dashboard using provided credentials.
Clears existing data from databases and caches.
Runs the web scraper to collect data.
Processes the scraped data and displays relevant statistics.
Opens articles in a browser and allows for review of images and full descriptions.
Custom exception handling and logging are implemented to ensure smooth execution and easy debugging.
Usage
Note: These scripts are part of a custom framework and may not be directly reusable without modifications. However, the core automation techniques demonstrated here can be adapted to a wide range of web scraping and browser automation tasks.
