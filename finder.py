import csv
import re
import time
import os
import requests
from bs4 import BeautifulSoup

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
CX = os.environ.get("GOOGLE_CX", "")

def search_google(query, start=1):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": CX, "q": query, "num": 10, "start": start}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json().get("items", [])
    print(f"  API error {resp.status_code}: {resp.text[:100]}")
    return []

def extract_from_website(url):
    info = {"emails": set(), "phones": set(), "instagram": "", "facebook": ""}
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        text = resp.text
        info["emails"] = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
        info["phones"] = set(re.findall(r'[\+]?[\d\s\-\(\)]{10,15}', text))
        soup = BeautifulSoup(text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'instagram.com/' in href and not info["instagram"]:
                info["instagram"] = href
            if 'facebook.com/' in href and not info["facebook"]:
                info["facebook"] = href
    except Exception as e:
        print(f"  Could not scrape {url}: {e}")
    return info

def clean_phones(phones):
    cleaned = []
    for p in phones:
        p = p.strip()
        digits = re.sub(r'\D', '', p)
        if 10 <= len(digits) <= 15:
            cleaned.append(p)
    return list(set(cleaned))[:3]

def clean_emails(emails):
    ignore = ['wixpress.com', 'sentry.io', 'example.com', 'domain.com', 'email.com', 'google.com', 'googleapis.com', 'gstatic.com', 'schema.org']
    return [e for e in emails if not any(x in e for x in ignore)][:3]

def is_directory_site(url):
    directories = ['yelp.com', 'yell.com', 'tripadvisor', 'google.com/maps', 'facebook.com', 'instagram.com', 'twitter.com', 'trustpilot.com', 'bark.com', 'checkatrade.com', 'treatwell.co.uk', 'fresha.com', 'booksy.com', 'wahanda.com']
    return any(d in url for d in directories)

def discover_businesses(category, city, country, pages=3):
    """Search Google to discover individual businesses in a category."""
    print(f"\n{'='*50}")
    print(f"Discovering: {category} in {city}, {country}")
    print(f"{'='*50}")

    found = []
    seen_domains = set()

    for page in range(pages):
        start = page * 10 + 1
        query = f"{category} in {city} {country}"
        results = search_google(query, start)

        if not results:
            break

        for item in results:
            link = item.get("link", "")
            title = item.get("title", "")

            # Skip directory/aggregator sites
            if is_directory_site(link):
                continue

            # Skip duplicate domains
            domain = re.sub(r'https?://(www\.)?', '', link).split('/')[0]
            if domain in seen_domains:
                continue
            seen_domains.add(domain)

            found.append({"name": title, "url": link})

        time.sleep(1)

    return found

def get_contact_details(business):
    """Visit a business website and extract contact info."""
    name = business["name"]
    url = business["url"]
    print(f"  Extracting contacts: {name}")

    extracted = extract_from_website(url)

    return {
        "name": name,
        "website": url,
        "email": "; ".join(clean_emails(extracted["emails"])),
        "phone": "; ".join(clean_phones(extracted["phones"])),
        "instagram": extracted["instagram"],
        "facebook": extracted["facebook"]
    }

def main():
    global API_KEY, CX

    if not API_KEY:
        API_KEY = input("Enter your Google API Key: ").strip()
    if not CX:
        CX = input("Enter your Search Engine ID (cx): ").strip()

    input_file = "businesses.csv"
    output_file = "results.csv"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Create it with columns: Business Name, City, Country")
        return

    # Read how many pages to search per category
    pages = int(input("How many pages per category? (1 page = 10 results, uses 1 API call): ") or "3")

    out = open(output_file, 'w', newline='', encoding='utf-8')
    writer = csv.writer(out)
    writer.writerow(["Category", "Business Name", "City", "Country", "Website", "Email", "Phone", "Instagram", "Facebook"])

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row.get("Business Name", "").strip()
            city = row.get("City", "").strip()
            country = row.get("Country", "").strip()

            if not category:
                continue

            # Discover businesses in this category
            businesses = discover_businesses(category, city, country, pages)
            print(f"  Found {len(businesses)} businesses")

            # Get contact details for each
            for biz in businesses:
                details = get_contact_details(biz)
                writer.writerow([
                    category,
                    details["name"],
                    city,
                    country,
                    details["website"],
                    details["email"],
                    details["phone"],
                    details["instagram"],
                    details["facebook"]
                ])
                time.sleep(0.5)

    out.close()
    print(f"\nDone! Results saved to {output_file}")

if __name__ == "__main__":
    main()
