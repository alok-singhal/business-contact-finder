import csv
import re
import time
import os
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
CX = os.environ.get("GOOGLE_CX", "")

def search_google(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": CX, "q": query, "num": 5}
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
    ignore = ['wixpress.com', 'sentry.io', 'example.com', 'domain.com', 'email.com']
    return [e for e in emails if not any(x in e for x in ignore)][:3]

def find_business(name, city, country):
    print(f"Searching: {name} in {city}, {country}")
    query = f"{name} {city} {country} contact"
    results = search_google(query)
    
    website = ""
    info = {"emails": [], "phones": [], "instagram": "", "facebook": ""}
    
    if results:
        website = results[0].get("link", "")
        extracted = extract_from_website(website)
        info["emails"] = clean_emails(extracted["emails"])
        info["phones"] = clean_phones(extracted["phones"])
        info["instagram"] = extracted["instagram"]
        info["facebook"] = extracted["facebook"]
    
    # Check other results for social links
    if not info["instagram"] or not info["facebook"]:
        for r in results[1:4]:
            link = r.get("link", "")
            if "instagram.com" in link and not info["instagram"]:
                info["instagram"] = link
            if "facebook.com" in link and not info["facebook"]:
                info["facebook"] = link
    
    time.sleep(1)
    return {
        "website": website,
        "email": "; ".join(info["emails"]),
        "phone": "; ".join(info["phones"]),
        "instagram": info["instagram"],
        "facebook": info["facebook"]
    }

def main():
    global API_KEY, CX
    
    if not API_KEY:
        API_KEY = input("Enter your Google API Key: ").strip()
    if not CX:
        CX = input("Enter your Search Engine ID (cx): ").strip()
    
    input_file = "businesses.csv"
    output_file = "results.xlsx"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Create it with columns: Business Name, City, Country")
        return
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"
    ws.append(["Business Name", "City", "Country", "Website", "Email", "Phone", "Instagram", "Facebook"])
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Business Name", "").strip()
            city = row.get("City", "").strip()
            country = row.get("Country", "").strip()
            
            if not name:
                continue
            
            result = find_business(name, city, country)
            ws.append([name, city, country, result["website"], result["email"], result["phone"], result["instagram"], result["facebook"]])
    
    wb.save(output_file)
    print(f"\nDone! Results saved to {output_file}")

if __name__ == "__main__":
    main()
