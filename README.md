# Business Contact Finder

Extracts contact details (email, phone, website, Instagram, Facebook) for businesses using Google Custom Search API.

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
Create `businesses.csv` with columns:
```
Business Name,City,Country
Costa Coffee,London,UK
```

### 4. Install & Run
```bash
pip install -r requirements.txt
python finder.py
```

It will prompt for your API Key and Search Engine ID, then output `results.xlsx`.

## Environment Variables (optional)
Instead of entering credentials each time:
```bash
export GOOGLE_API_KEY=your_key_here
export GOOGLE_CX=your_search_engine_id
```

## Limits
- Google Custom Search API: **100 free queries/day** (3,000/month)
- Each business uses 1 API call
- Rate limited to 1 request/second to be safe

## Output
`results.xlsx` with columns:
| Business Name | City | Country | Website | Email | Phone | Instagram | Facebook |
