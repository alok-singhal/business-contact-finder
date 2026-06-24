# Business Contact Finder

Discovers businesses by category in a given city and extracts their contact details using DuckDuckGo search.

No API key needed. No setup. Just run.

## Install & Run
```bash
pip install requests beautifulsoup4
python finder.py
```

## Input
Edit `businesses.csv`:
```
Business Name,City,Country
Hair salon,Newcastle upon Tyne,United Kingdom
```

## Output
`results.csv` with columns:
Category, Business Name, City, Country, Website, Email, Phone, Instagram, Facebook
