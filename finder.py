import csv
import re
import time
import os
import requests
from bs4 import BeautifulSoup

def search_duckduckgo(query):
    """Search DuckDuckGo and return result URLs."""
    url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.post(url, data={"q": query}, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    for a in soup.find_all('a', class_='result__a'):
        href = a.get('href', '')
        title = a.get_text(strip=True)
        if href and title:
            results.append({"title": title, "url": href})
    return results[:15]

def extract_from_website(url):
    info = {"emails": set(), "phones": set(), "instagram": "", "facebook": ""}
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
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
    ignore = ['wixpress.com', 'sentry.io', 'example.com', 'domain.com', 'email.com', 'google.com', 'googleapis.com', 'gstatic.com', 'schema.org', 'duckduckgo.com']
    return [e for e in emails if not any(x in e for x in ignore)][:3]

def is_directory_site(url):
    directories = ['yelp.com', 'yell.com', 'tripadvisor', 'google.com/maps', 'facebook.com', 'instagram.com', 'twitter.com', 'trustpilot.com', 'bark.com', 'checkatrade.com', 'treatwell.co.uk', 'fresha.com', 'booksy.com', 'wahanda.com', 'duckduckgo.com', 'wikipedia.org']
    return any(d in url for d in directories)

def discover_businesses(category, city, country):
    """Search DuckDuckGo to discover individual businesses in a category."""
    print(f"\n{'='*50}")
    print(f"Discovering: {category} in {city}, {country}")
    print(f"{'='*50}")

    found = []
    seen_domains = set()

    query = f"{category} in {city} {country}"
    results = search_duckduckgo(query)

    for item in results:
        link = item["url"]
        title = item["title"]

        if is_directory_site(link):
            continue

        domain = re.sub(r'https?://(www\.)?', '', link).split('/')[0]
        if domain in seen_domains:
            continue
        seen_domains.add(domain)

        found.append({"name": title, "url": link})

    time.sleep(2)
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
    input_file = "businesses.csv"
    output_file = "results.csv"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Create it with columns: Business Name, City, Country")
        return

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

            businesses = discover_businesses(category, city, country)
            print(f"  Found {len(businesses)} businesses")

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
                time.sleep(1)

    out.close()
    print(f"\nDone! Results saved to {output_file}")

if __name__ == "__main__":
    main()
