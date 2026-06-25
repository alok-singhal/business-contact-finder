import re
import time
import os
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def search_duckduckgo(query):
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


def search_google_api(query, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": 10}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    results = []
    for item in data.get("items", []):
        results.append({"title": item.get("title", ""), "url": item.get("link", "")})
    return results


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


def discover_businesses(category, city, country, search_method, api_key=None, cx=None):
    print(f"\n{'='*50}")
    print(f"Discovering: {category} in {city}, {country}")
    print(f"{'='*50}")

    query = f"{category} in {city} {country}"

    if search_method == "google":
        results = search_google_api(query, api_key, cx)
    else:
        results = search_duckduckgo(query)

    found = []
    seen_domains = set()
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
    print(f"  Extracting contacts: {business['name']}")
    extracted = extract_from_website(business["url"])
    return {
        "name": business["name"],
        "website": business["url"],
        "email": "; ".join(clean_emails(extracted["emails"])),
        "phone": "; ".join(clean_phones(extracted["phones"])),
        "instagram": extracted["instagram"],
        "facebook": extracted["facebook"]
    }


def main():
    print("\n=== Business Contact Finder ===\n")

    niches = input("Enter business niche(s) (comma separated, e.g. Beauty Salon, Nail Spa): ").strip()
    cities = input("Enter city/cities (comma separated, e.g. Newcastle Upon Tyne, London): ").strip()
    country = input("Enter country (e.g. United Kingdom): ").strip()

    niches = [n.strip() for n in niches.split(",") if n.strip()]
    cities = [c.strip() for c in cities.split(",") if c.strip()]

    if not niches or not cities or not country:
        print("Error: Please provide at least one niche, one city, and a country.")
        return

    print("\nSearch method:")
    print("  1. Google API")
    print("  2. DuckDuckGo (no API key needed)")
    choice = input("Choose (1 or 2): ").strip()

    api_key, cx = None, None
    if choice == "1":
        search_method = "google"
        api_key = os.environ.get("GOOGLE_API_KEY") or input("Enter Google API Key: ").strip()
        cx = os.environ.get("GOOGLE_CX") or input("Enter Google Search Engine ID: ").strip()
    else:
        search_method = "duckduckgo"

    date_stamp = datetime.now().strftime("%d%m")

    for niche in niches:
        for city in cities:
            output_file = f"{niche}_{city}_{date_stamp}.csv".replace(" ", "_")
            out = open(output_file, 'w', newline='', encoding='utf-8')
            writer = csv.writer(out)
            writer.writerow(["Niche", "Business Name", "City", "Country", "Website", "Email", "Phone", "Instagram", "Facebook"])

            businesses = discover_businesses(niche, city, country, search_method, api_key, cx)
            print(f"  Found {len(businesses)} businesses")
            for biz in businesses:
                details = get_contact_details(biz)
                writer.writerow([niche, details["name"], city, country, details["website"], details["email"], details["phone"], details["instagram"], details["facebook"]])
                time.sleep(1)

            out.close()
            print(f"  Saved: {output_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()
