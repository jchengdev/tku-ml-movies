import csv
import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

COLUMNS = [
    "Release Date",
    "Title",
    "Production",
    "Distributor",
    "Theaters",
    "Director",
    "Country",
    "Genre",
    "Duration (min)",
    "Budget (USD)",
    "Re-release",
    "Sequel/Prequel/Remake",
    "Rating",
    "Metacritic Score",
    "Domestic (%)",
    "International (%)",
    "Opening (USD)",
    "Box Office (USD)",
]

OMDB_API_KEY = "1b7be36e"
TMDB_API_KEY = "53e8c9056a2bc53c91f359d222e86f06"
START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2026, 7, 31)

COUNTRY_CODES = {
    # North America
    "United States": "US",
    "Canada": "CA",
    "Mexico": "MX",
    # Europe
    "France": "FR",
    "Germany": "DE",
    "Italy": "IT",
    "Spain": "ES",
    "United Kingdom": "UK",
    "Ireland": "IE",
    "Sweden": "SE",
    "Denmark": "DK",
    "Norway": "NO",
    "Finland": "FI",
    "Iceland": "IS",
    "Belgium": "BE",
    "Netherlands": "NL",
    "Switzerland": "CH",
    "Austria": "AT",
    "Poland": "PL",
    "Hungary": "HU",
    "Czech Republic": "CZ",
    "Greece": "GR",
    "Portugal": "PT",
    "Turkey": "TR",
    # Asia-Pacific
    "Japan": "JP",
    "India": "IN",
    "South Korea": "KR",
    "China": "CN",
    "Taiwan": "TW",
    "Hong Kong": "HK",
    "Singapore": "SG",
    "Thailand": "TH",
    "Indonesia": "ID",
    "Philippines": "PH",
    "Malaysia": "MY",
    "Vietnam": "VN",
    "Australia": "AU",
    "New Zealand": "NZ",
    # Middle East & Africa
    "United Arab Emirates": "AE",
    "Jordan": "JO",
    "Egypt": "EG",
    "South Africa": "ZA",
    "Israel": "IL",
    # Latin America
    "Argentina": "AR",
    "Brazil": "BR",
    "Chile": "CL",
    "Colombia": "CO",
    "Peru": "PE",
}


def clean_val(val):
    """Returns empty string if value is N/A, dash, or empty."""
    if not val or str(val).strip().lower() in ["n/a", "-"]:
        return ""
    return str(val).strip()


def format_countries(country_str):
    """Converts comma-separated country names to country codes."""
    cleaned = clean_val(country_str)
    if not cleaned:
        return ""
    countries = [c.strip() for c in cleaned.split(",")]
    codes = [COUNTRY_CODES.get(c, c) for c in countries]
    return ", ".join(codes)


def fetch_omdb_data(title, year=None):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    if year:
        url += f"&y={year}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching OMDb data for {title}: {e}")
    return {}


def fetch_tmdb(title, year=None):
    """Fetches production companies from TMDB API to replace broken IMDb scraping."""
    search_url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title}
    if year:
        params["year"] = year
    try:
        resp = requests.get(search_url, params=params)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                movie_id = results[0]["id"]
                detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
                detail_resp = requests.get(detail_url, params={"api_key": TMDB_API_KEY})
                if detail_resp.status_code == 200:
                    comps = detail_resp.json().get("production_companies", [])
                    return ", ".join([c["name"] for c in comps])
    except Exception as e:
        print(f"Error fetching TMDB production for {title}: {e}")
    return ""


def generate_numbers_slug(title, year):
    """Dynamically creates The Numbers URL slug from title and year."""
    base_slug = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    base_slug = re.sub(r"\s+", "-", base_slug.strip())
    return f"{base_slug}-({year})"


def scrape_financials_with_playwright(numbers_slug, mojo_id):
    data = {
        "budget": "-",
        "theaters": "-",
        "opening": "-",
        "dom_pct": "-",
        "intl_pct": "-",
        "box_office": "-",
        "distributor": "-",
        "production": "",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Scrape The Numbers (Budget & Theaters)
        if numbers_slug:
            try:
                numbers_url = f"https://www.the-numbers.com/movie/{numbers_slug}"
                page.goto(numbers_url, timeout=60000)
                page.wait_for_selector("table", timeout=5000)

                soup_num = BeautifulSoup(page.content(), "html.parser")

                for row in soup_num.find_all("tr"):
                    row_text = row.get_text().replace("\xa0", " ")

                    if "Production Budget" in row_text:
                        cells = row.find_all("td")
                        if len(cells) >= 2:
                            raw_text = cells[1].get_text().strip()
                            match = re.search(r"\$[\d,]+", raw_text)
                            if match:
                                data["budget"] = match.group(0)
                            else:
                                data["budget"] = raw_text

                    if "Theater counts" in row_text or "Theaters" in row_text:
                        cells = row.find_all("td")
                        if len(cells) >= 2:
                            raw_text = cells[1].get_text().strip()
                            match = re.search(
                                r"([\d,]+)\s*opening theaters", raw_text, re.IGNORECASE
                            )
                            if match:
                                data["theaters"] = match.group(1)
                            else:
                                data["theaters"] = raw_text

            except Exception as e:
                print(f"Error scraping The Numbers for {numbers_slug}: {e}")

        # 2. Scrape Box Office Mojo
        if mojo_id:
            try:
                mojo_url = f"https://www.boxofficemojo.com/title/{mojo_id}/"
                page.goto(mojo_url, timeout=60000)
                page.wait_for_selector("body", timeout=5000)

                soup_mojo = BeautifulSoup(page.content(), "html.parser")

                # Rule 1: Domestic (%)
                percent_elem = soup_mojo.find("span", class_="percent")
                if percent_elem:
                    dom_str = percent_elem.get_text().replace("%", "").strip()
                    try:
                        dom_val = float(dom_str)
                        data["dom_pct"] = dom_val
                        data["intl_pct"] = round(100.0 - dom_val, 1)
                    except ValueError:
                        pass

                # Rule 2: Opening (USD)
                opening_label = soup_mojo.find(
                    string=lambda t: t and "Domestic Opening" in t
                )
                if opening_label:
                    parent_div = opening_label.find_parent("div", class_="a-section")
                    if parent_div:
                        money_elem = parent_div.find("span", class_="money")
                        if money_elem:
                            data["opening"] = money_elem.get_text().strip()

                # Rule 3: Box Office (USD)
                ww_span = soup_mojo.find(
                    "span",
                    class_="a-size-small",
                    string=lambda t: t and "Worldwide" in t,
                )
                if ww_span:
                    container = ww_span.find_parent("div")
                    if container:
                        money_elem = container.find("span", class_="money")
                        if money_elem:
                            data["box_office"] = money_elem.get_text().strip()

                # Rule 4: Domestic Distributor
                dist_label = soup_mojo.find(
                    string=lambda t: t and "Domestic Distributor" in t
                )
                if dist_label:
                    parent_div = dist_label.find_parent("div", class_="a-section")
                    if parent_div:
                        spans = parent_div.find_all("span")
                        if len(spans) >= 2:
                            dist_span = spans[1]
                            for a_tag in dist_span.find_all("a"):
                                a_tag.decompose()
                            raw_dist = dist_span.get_text()
                            dist_text = re.sub(r"\s+", " ", raw_dist).strip()
                            if dist_text:
                                data["distributor"] = dist_text

            except Exception as e:
                print(f"Error scraping Box Office Mojo for {mojo_id}: {e}")

        browser.close()
    return data


def parse_release_date(date_str):
    if not date_str or date_str == "-":
        return None
    formats = ["%d %b %Y", "%B %d, %Y", "%Y-%m-%d", "%d %B %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def process_movie(title_query, year):
    omdb = fetch_omdb_data(title_query, year=year)
    if omdb.get("Response") == "False":
        print(f"Movie '{title_query}' not found in OMDb.")
        return None

    release_raw = omdb.get("Released", "-")
    release_date = parse_release_date(release_raw)
    if not release_date or not (START_DATE <= release_date <= END_DATE):
        print(f"Skipping '{title_query}': Release date ({release_raw}) outside range.")
        return None

    numbers_slug = generate_numbers_slug(title_query, year)
    mojo_id = omdb.get("imdbID", None)

    financials = scrape_financials_with_playwright(numbers_slug, mojo_id)

    # Fetch production via TMDB API
    tmdb_production = fetch_tmdb(title_query, year)

    row = {
        "Release Date": release_raw,
        "Title": omdb.get("Title", title_query),
        "Production": tmdb_production
        if tmdb_production
        else clean_val(omdb.get("Production")),
        "Distributor": (
            financials.get("distributor", "-")
            if financials.get("distributor", "-") != "-"
            else clean_val(omdb.get("Distributor"))
        ),
        "Theaters": financials.get("theaters", "-"),
        "Director": clean_val(omdb.get("Director")),
        "Country": format_countries(omdb.get("Country")),
        "Genre": clean_val(omdb.get("Genre", "").replace(", ", " · ")),
        "Duration (min)": clean_val(omdb.get("Runtime", "0 min").replace(" min", "")),
        "Budget (USD)": financials.get("budget", "-"),
        "Re-release": "No",
        "Sequel/Prequel/Remake": "Yes"
        if any(
            w in title_query.lower()
            for w in ["2", "3", "4", "5", "conclusion", "remake", "part"]
        )
        else "No",
        "Rating": clean_val(omdb.get("Rated")),
        "Metacritic Score": clean_val(omdb.get("Metascore")),
        "Domestic (%)": financials.get("dom_pct", "-"),
        "International (%)": financials.get("intl_pct", "-"),
        "Opening (USD)": financials.get("opening", "-"),
        "Box Office (USD)": financials.get("box_office", "-"),
    }
    return row


# --- Load movies from simplified text file ---
movies_to_check = []
try:
    with open("movies_list.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 2:
                title, yr = parts
                movies_to_check.append((title, int(yr)))
except FileNotFoundError:
    print("Error: movies_list.txt not found. Please create one.")

dataset = []
for title, yr in movies_to_check:
    print(f"Processing {title} ({yr})...")
    result = process_movie(title, yr)
    if result:
        dataset.append(result)

if dataset:
    with open("filtered_movie_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(dataset)
    print("Done! Saved to filtered_movie_data.csv")
else:
    print("No movie data collected to save.")
