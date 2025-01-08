import os
import requests
from pytz import UTC
from dateutil import parser
from openpyxl import Workbook
import openpyxl
from lxml import etree
from datetime import datetime
import xml.etree.ElementTree as ET
from requests.exceptions import RequestException
from connections import get_msq_conn, close_mysql_conn
from concurrent.futures import ThreadPoolExecutor, as_completed


class Check_Feed_Last_Update:
    
    def __init__(self):
        self.report_data = [] # To store feed details for reporting
        self.domain_ids = []
        
    
    def parse_date(self, date_str):
        """ Parse a date string into a datetime object. """
        try:
            # Try using dateutil.parser first
            return parser.parse(date_str)
        except (ValueError, TypeError):
            pass  # Fallback to manual parsing
        
        # Custom known formats
        known_formats = [
            "%a, %d %b %Y %H:%M:%S %Z",  # Example: "Mon, 13 Mar 2023 09:00:00 GMT"
            "%Y-%m-%dT%H:%M:%SZ",        # Example: "2023-03-13T09:00:00Z"
            "%d-%m-%Y %H:%M:%S",         # Example: "13-03-2023 09:00:00"
            "%Y/%m/%d %H:%M:%S",         # Example: "2023/03/13 09:00:00"
        ]
        for fmt in known_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue  # Try the next format
            
        return None  # Return None if no format matches

    def calculate_time(self, pub_date):
        """Calculate the age of the publication date in various units."""
        if not pub_date:
            return None

        # Standardize to UTC
        now = datetime.now(UTC)
        if pub_date.tzinfo is None:  # If naive, make it aware
            pub_date = pub_date.replace(tzinfo=UTC)

        diff = now - pub_date
        days_old = diff.days
        months_old = days_old // 30  # Approximate months
        years_old = days_old // 365  # Approximate years
        hours_old = diff.total_seconds() // 3600

        return {"days_old": days_old, "months_old": months_old, 
                "years_old": years_old, "hours_old": hours_old}

    def parse_feed(self, root):
        """Parse XML feed and extract the latest article link and publication date."""
        if root:
            pub_dates = root.findall('.//item//pubDate') or root.findall('.//item//pubdate') or root.findall('.//entry//updated') or root.findall('.//entry//published') or root.findall('.//published') or root.findall('.//updated')
            link =  root.findall('.//item//link') or root.findall('.//entry//link') or root.findall('.//link')
            if len(pub_dates) == 0:
                return None, None,None
            pub_date_tag = pub_dates[0]
            link_tag = link[0]
            link = link_tag.text
            if not link:
                link = link_tag.attrib['href'] if link_tag is not None else None
            pub_date_str = pub_date_tag.text if pub_date_tag is not None else None
            pub_date = self.parse_date(pub_date_str)
            return link, pub_date,pub_date_str
        
            
    def request_feed(self, feed_url):
        """Fetch and parse the feed, returning relevant data."""
        try:
            header = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"}
            response = requests.get(feed_url, timeout=10)
    
            if response.status_code in (403, 429):
                response = requests.get(feed_url, headers=header, timeout=10)
            
            if response.status_code == 200:
                # Parse XML content
                content = response.text  # Get the response text
                parser = etree.XMLParser(remove_blank_text=True, recover=True)
                root = etree.fromstring(content.encode('utf-8'), parser=parser)
                
                # Remove namespaces if needed
                for elem in root.getiterator():
                    if elem.tag.startswith('{'):
                        elem.tag = elem.tag.split('}', 1)[1]  # Remove namespace
                
                # Pass content to the feed parser
                link, pub_date, pub_date_str = self.parse_feed(root)
                age_info = self.calculate_time(pub_date) if pub_date else None
                status = "Success"
                message = "Feed processed successfully"
            else:
                link, pub_date_str, age_info = None, None, None
                status = "Failure"
                message = f"HTTP {response.status_code}"

            # Append details to the report
            self.report_data.append({
                "feed_url": feed_url,
                "link": link,
                "pub_date": pub_date_str,
                "days_old": age_info.get("days_old") if age_info else "N/A",
                "months_old": age_info.get("months_old") if age_info else "N/A",
                "years_old": age_info.get("years_old") if age_info else "N/A",
                "hours_old": age_info.get("hours_old") if age_info else "N/A",
                "status": status,
                "message": message,
            })

        except RequestException as e:
            print(f"Error occurred in GET request: {str(e)}")
            # Append error details to the report
            self.report_data.append({
                "feed_url": feed_url,
                "link": None,
                "pub_date": None,
                "days_old": "N/A",
                "months_old": "N/A",
                "years_old": "N/A",
                "hours_old": "N/A",
                "status": "Error",
                "message": str(e),
            })

    def generate_report(self, output_file):
        """Generate a CSV report from the collected feed data."""
        try:
            if os.path.exists(output_file):
                workbook = openpyxl.load_workbook(output_file)
                sheet = workbook.active
            else:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Feed Report"
                # Write headers if the file is new
                fieldnames = [
                    "feed_url", "link", "pub_date", "days_old", "months_old",
                    "years_old", "hours_old", "status", "message"
                ]
                sheet.append(fieldnames)
        
        except Exception as e:
            print(f"Error opening or creating the Excel file: {str(e)}")
            return

        # Write data rows
        for row in self.report_data:
            sheet.append([
                row.get("feed_url", ""),
                row.get("link", ""),
                row.get("pub_date", ""),
                row.get("days_old", "N/A"),
                row.get("months_old", "N/A"),
                row.get("years_old", "N/A"),
                row.get("hours_old", "N/A"),
                row.get("status", ""),
                row.get("message", "")
            ])
        
        # Save the workbook to the specified file
        workbook.save(output_file)
        print(f"Report generated: {output_file}")

    def start_check(self, domain_ids: list,type=None, max_workers=10):
        """
        Efficiently fetch and process feeds using threading.
        """
        feed_urls = []

        # Fetch all feed URLs for the given domain IDs
        conn, cursor = get_msq_conn()
        try:
            for domain_id in domain_ids:
                feeds_query = f"SELECT url FROM source WHERE source.domain_id = {domain_id} AND is_deleted=0"
                cursor.execute(feeds_query)
                feed_urls.extend([url[0] for url in cursor.fetchall()])
        finally:
            close_mysql_conn(db=conn, cursor=cursor)

        # Process feeds in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.request_feed, url): url for url in feed_urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    future.result()  # Wait for the thread to finish
                except Exception as e:
                    print(f"Error processing {url}: {e}")
        if type:
            # Generate the report after all feeds are processed
            self.generate_report("Multi_feed_report.xlsx")
        else: self.generate_report("feed_report.xlsx")