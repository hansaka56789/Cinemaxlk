import json
import os
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

PAGES = {
    "home": "https://cinemaxlk.vercel.app/index.html",
    "discover": "https://cinemaxlk.vercel.app/discover.html",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
}


def scrape_page(name: str, url: str) -> dict:
    res = requests.get(url, headers=HEADERS, timeout=30)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    movies = []

    for h3 in soup.find_all("h3"):
        title = h3.get_text(strip=True)
        if not title:
            continue

        meta_el = h3.find_next("p")
        meta = meta_el.get_text(strip=True) if meta_el else ""

        img = None
        prev_img = h3.find_previous("img")
        if prev_img and prev_img.get("src"):
            img = prev_img["src"]

        movies.append({"title": title, "meta": meta, "img": img})

    return {
        "source": url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "count": len(movies),
        "results": movies,
    }


def main():
    os.makedirs("data", exist_ok=True)

    for name, url in PAGES.items():
        try:
            data = scrape_page(name, url)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            continue

        with open(f"data/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"{name}: {data['count']} items saved")


if __name__ == "__main__":
    main()
