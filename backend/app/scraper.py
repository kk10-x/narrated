import trafilatura


def fetch_article_text(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise ValueError(f"Could not fetch content from {url}")

    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    if not text or len(text.strip()) < 200:
        raise ValueError("Extracted article text was too short to narrate")

    return text.strip()
