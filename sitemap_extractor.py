# -*- coding: utf-8 -*-
"""sitemap extractor.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17eusEI8CGL2Ku1wYH4s3Mw5P0FFiTa6_
"""

!pip install requests beautifulsoup4 ipywidgets
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import ipywidgets as widgets
from IPython.display import display

def scrape_website_and_cluster_urls(base_url):
    """Scrapes a website, extracts URLs, and clusters them based on the first path segment."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    url_clusters = defaultdict(set)

    for link in soup.find_all('a', href=True):
        url = urljoin(base_url, link['href'])
        if url.startswith(base_url) and not url.endswith('#'):
            parsed_url = urlparse(url)
            path_segments = parsed_url.path.strip('/').split('/')
            if path_segments:
                first_segment = path_segments[0]
                url_clusters[first_segment].add(url)

    return {cluster: list(urls) for cluster, urls in url_clusters.items()}

def display_clustered_urls(url_clusters):
    """Displays clustered URLs in an interactive widget."""
    output = widgets.Output()

    with output:
        for cluster, urls in url_clusters.items():
            print(f"Cluster: {cluster}")
            for url in urls:
                print(f"  - {url}")

    display(output)

# Create the URL input widget
url_input = widgets.Text(
    placeholder='Enter website URL',
    description='URL:',
    disabled=False
)

# Create the button to trigger scraping
scrape_button = widgets.Button(
    description='Scrape and Cluster',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click to scrape and cluster URLs',
    icon='search' # (FontAwesome names without the `fa-` prefix)
)

# Function to handle button click
def on_button_clicked(b):
    base_url = url_input.value
    url_clusters = scrape_website_and_cluster_urls(base_url)
    display_clustered_urls(url_clusters)  # Call function to display results

scrape_button.on_click(on_button_clicked)

# Display the widgets
display(widgets.VBox([url_input, scrape_button]))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import re

# Function to crawl the website and collect internal URLs
def crawl_website(base_url, max_urls=100, headers=None):
    visited_urls = set()  # Set to track visited URLs
    url_map = defaultdict(set)  # Dictionary to store which pages link to which others
    orphan_pages = set()  # To store orphan pages (no incoming links)

    def scrape_page(url):
        """Scrape a single page, extract all internal links, and track them."""
        nonlocal visited_urls, url_map, orphan_pages

        # If we have reached the max URL limit, stop
        if len(visited_urls) >= max_urls:
            return

        # Skip already visited URLs
        if url in visited_urls:
            return

        visited_urls.add(url)

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(f"An error occurred while scraping {url}: {err}")
            return

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all internal links
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)  # Convert relative URL to absolute

            # Only consider internal links (same domain)
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                # Add to the url_map for tracking which page links to which
                url_map[absolute_url].add(url)

        # Identify orphan pages by checking which pages have no incoming links
        for linked_page in url_map:
            if url not in url_map[linked_page]:
                orphan_pages.add(url)

    # Start scraping from the base URL
    scrape_page(base_url)

    # Return all visited URLs and orphan pages
    return visited_urls, orphan_pages, url_map

# Function to analyze the internal link structure
def analyze_internal_links(base_url, max_urls=100, headers=None):
    # Crawl the website to gather all URLs and the internal linking structure
    visited_urls, orphan_pages, url_map = crawl_website(base_url, max_urls, headers)

    print("\n--- All Visited URLs ---")
    for url in visited_urls:
        print(url)

    print("\n--- Orphan Pages (Pages not linked to by any other page) ---")
    for orphan in orphan_pages:
        print(orphan)

    print("\n--- Internal Links Structure (Who links to whom) ---")
    for url, links in url_map.items():
        print(f"Page: {url}")
        print("Links to:")
        for link in links:
            print(f"  - {link}")
        print()

# Main execution example
if __name__ == "__main__":
    base_url = "https://www.justdocumentz.com/"  # Replace with your site URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Call the analysis function
    analyze_internal_links(base_url, max_urls=100, headers=headers)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import re

# Function to normalize URLs by removing fragments
def normalize_url(url):
    # Parse the URL and strip the fragment part
    parsed_url = urlparse(url)
    return parsed_url._replace(fragment='').geturl()

# Function to crawl the website and collect internal URLs
def crawl_website(base_url, max_urls=100, headers=None):
    visited_urls = set()  # Set to track visited URLs
    url_map = defaultdict(set)  # Dictionary to store which pages link to which others
    orphan_pages = set()  # To store orphan pages (no incoming links)

    def scrape_page(url):
        """Scrape a single page, extract all internal links, and track them."""
        nonlocal visited_urls, url_map, orphan_pages

        # Normalize URL to handle fragment issues
        normalized_url = normalize_url(url)

        # If we have reached the max URL limit, stop
        if len(visited_urls) >= max_urls:
            return

        # Skip already visited URLs
        if normalized_url in visited_urls:
            return

        visited_urls.add(normalized_url)

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(f"An error occurred while scraping {url}: {err}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all internal links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)

            # Normalize the URL and add it to the map
            normalized_full_url = normalize_url(full_url)
            url_map[normalized_url].add(normalized_full_url)

    # Start scraping from the base URL
    scrape_page(base_url)

    # Now identify orphan pages (pages with no incoming links)
    # Create a copy of url_map keys for iteration to avoid modifying the dictionary during iteration
    for page in list(url_map.keys()):
        for link in url_map[page]:
            url_map[link].add(page)  # Add the current page as an incoming link to the linked page

    # Print all clusters (pages and their linked pages)
    for page, links in url_map.items():
        print(f"Cluster: {page}")
        for link in links:
            print(f"  - {link}")

# Example usage
base_url = "https://chicagoslaw.localseolab.com"
crawl_website(base_url, max_urls=50)