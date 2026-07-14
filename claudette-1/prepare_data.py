"""Build Claudette-1's training corpus: public-domain founding legal texts.

Downloads the Federalist Papers and the U.S. Constitution from Project
Gutenberg, strips the Gutenberg boilerplate, and writes data/corpus.txt.

Real LLM pretraining does exactly this at incomprehensible scale — trillions
of tokens scraped, filtered, deduplicated, and cleaned. Data quality is a
huge share of what separates good models from bad ones.
"""

import pathlib
import urllib.request

SOURCES = {
    "federalist.txt": "https://www.gutenberg.org/cache/epub/1404/pg1404.txt",
    "constitution.txt": "https://www.gutenberg.org/cache/epub/5/pg5.txt",
}

START_MARK = "*** START OF THE PROJECT GUTENBERG EBOOK"
END_MARK = "*** END OF THE PROJECT GUTENBERG EBOOK"

DATA_DIR = pathlib.Path(__file__).parent / "data"


def strip_gutenberg(text: str) -> str:
    """Keep only the text between the Gutenberg start/end markers."""
    start = text.find(START_MARK)
    if start != -1:
        start = text.find("\n", start) + 1
        text = text[start:]
    end = text.find(END_MARK)
    if end != -1:
        text = text[:end]
    return text.strip() + "\n"


def main():
    DATA_DIR.mkdir(exist_ok=True)
    parts = []
    for name, url in SOURCES.items():
        path = DATA_DIR / name
        if not path.exists():
            print(f"downloading {url}")
            urllib.request.urlretrieve(url, path)
        parts.append(strip_gutenberg(path.read_text(encoding="utf-8")))

    corpus = "\n\n".join(parts)
    out = DATA_DIR / "corpus.txt"
    out.write_text(corpus, encoding="utf-8")
    chars = sorted(set(corpus))
    print(f"wrote {out}: {len(corpus):,} characters, vocabulary of {len(chars)} distinct characters")


if __name__ == "__main__":
    main()
