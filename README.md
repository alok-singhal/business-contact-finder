# Business Contact Finder

Discovers and extracts contact details (email, phone, website, Instagram, Facebook) for businesses by niche and location.

## Setup

### Install
```bash
pip install -r requirements.txt
python finder.py
```

### Usage
The script will prompt you for:
1. **Business niche(s)** — comma separated (e.g. `Beauty Salon, Nail Spa, Hair Salon`)
2. **City/cities** — comma separated (e.g. `Newcastle Upon Tyne, London, Edinburgh`)
3. **Country** (e.g. `United Kingdom`)
4. **Search method** — Google API or DuckDuckGo

### Google API Setup (optional)
Only needed if you choose Google API as search method:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Custom Search JSON API**
3. Create an API Key
4. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/) → Create engine → Copy **Search Engine ID**

## Environment Variables (optional)
```bash
set GOOGLE_API_KEY=your_key_here
set GOOGLE_CX=your_search_engine_id
```

## Limits
- Google Custom Search API: **100 free queries/day**
- DuckDuckGo: No hard limit but rate-limited to avoid blocks
- Rate limited to 1 request/second

## Output
`results.csv` with columns:
| Niche | Business Name | City | Country | Website | Email | Phone | Instagram | Facebook |
