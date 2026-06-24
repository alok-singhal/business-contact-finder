# Business Contact Finder

Discovers businesses by category in a given city and extracts their contact details (email, phone, website, Instagram, Facebook).

## Setup

### 1. Get Google API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Custom Search JSON API**
4. Go to Credentials → Create API Key
5. Copy the key

### 2. Create Custom Search Engine
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click Add → Search the entire web
3. Copy the **Search Engine ID**

### 3. Prepare Your CSV
Edit `businesses.csv` with categories and locations:
```
Business Name,City,Country
Hair salon,Newcastle upon Tyne,United Kingdom
Nail salon,Newcastle upon Tyne,United Kingdom
```

### 4. Install & Run
```bash
pip install requests beautifulsoup4
python finder.py
```

It will prompt for your API Key, Search Engine ID, and pages per category, then output `results.csv`.

## Limits
- Google Custom Search API: **100 free queries/day**
- 1 page = 10 results = 1 API call
- 3 categories x 3 pages = 9 API calls

## Output
`results.csv` with columns:
Category, Business Name, City, Country, Website, Email, Phone, Instagram, Facebook
