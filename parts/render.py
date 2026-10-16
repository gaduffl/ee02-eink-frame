"""Render the parts list from parts.toml + affiliate.toml into README.md.

SPDX-License-Identifier: MIT

Usage:  python3 parts/render.py            rewrite the block between the PARTS markers in README.md
        python3 parts/render.py --check    exit 1 if README.md is out of date
"""
import os
import sys
import tomllib
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(os.path.dirname(HERE), "README.md")
START, END = "<!-- PARTS:START -->", "<!-- PARTS:END -->"
STORES = [("com", "amazon.com"), ("de", "amazon.de"), ("fr", "amazon.fr")]
DISCLOSURE = {
    "com": "As an Amazon Associate I earn from qualifying purchases.",
    "de": "Als Amazon-Partner verdiene ich an qualifizierten Verkäufen.",
    "fr": "En tant que Partenaire Amazon, je réalise un bénéfice sur les achats remplissant les conditions requises.",
}


def load(name):
    with open(os.path.join(HERE, name), "rb") as f:
        return tomllib.load(f)


def link(store, entry, tags):
    tag = tags.get(store, "").strip()
    suffix = f"tag={quote_plus(tag)}" if tag else ""
    if "asin" in entry:
        url = f"https://www.amazon.{store}/dp/{entry['asin']}"
        url += f"?{suffix}" if suffix else ""
        return url, entry.get("label", entry["asin"])
    url = f"https://www.amazon.{store}/s?k={quote_plus(entry['search'])}"
    url += f"&{suffix}" if suffix else ""
    return url, entry.get("label", "search")


def render():
    data, tags = load("parts.toml"), load("affiliate.toml")
    seeed_tags = {k: v.strip() for k, v in tags.get("seeed", {}).items() if v.strip()}
    out = []
    used = [s for s, _ in STORES if tags.get(s, "").strip()]
    if used or seeed_tags:
        text = " ".join(DISCLOSURE[s] for s in used)
        if seeed_tags:
            text += " Links to Seeed Studio are affiliate links as well."
        out.append("> **Affiliate links.** " + text.strip() + " The price is the same for you.")
        out.append("")
    out.append("| Part | Qty | " + " | ".join(n for _, n in STORES) + " |")
    out.append("|---|---|" + "---|" * len(STORES))
    unverified = False
    for p in data["part"]:
        cell = f"**{p['name']}**"
        if p.get("needs"):
            cell += f"<br><sub>{p['needs']}</sub>"
        extra = []
        for o in p.get("other", []):
            extra.append(f"[{o['label']}]({o['url']})")
        if p.get("note"):
            extra.append(p["note"])
        if extra:
            cell += "<br><sub>" + " · ".join(extra) + "</sub>"
        cols = []
        if "seeed" in p:
            url = seeed_tags.get(p["id"], p["seeed"]["url"])
            label = p["seeed"].get("label", "Seeed Studio")
            out.append(f"| {cell} | {p['qty']} | " + " | ".join([f"[{label}]({url})"] * len(STORES)) + " |")
            continue
        for store, _ in STORES:
            entry = p.get(store)
            if not entry:
                cols.append("–")
                continue
            url, label = link(store, entry, tags)
            mark = ""
            if "asin" in entry and not entry.get("verified", False):
                mark, unverified = " \\*", True
            cols.append(f"[{label}]({url}){mark}")
        out.append(f"| {cell} | {p['qty']} | " + " | ".join(cols) + " |")
    out.append("")
    notes = ["Search links open an Amazon search for the part; pick any listing that meets the requirement under the part name."]
    if unverified:
        notes.append("\\* Suggested listing, not yet checked against the requirements. Check the size and connector before you buy.")
    if data.get("checked"):
        notes.append(f"Listings checked on {data['checked']}; Amazon listings change, so check the details before you buy.")
    out.append("<sub>" + "<br>".join(notes) + "</sub>")
    return "\n".join(out)


def main():
    text = open(README, encoding="utf-8").read()
    if START not in text or END not in text:
        sys.exit(f"README.md needs {START} and {END} markers")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{render()}\n{END}{tail}"
    if "--check" in sys.argv:
        sys.exit(0 if new == text else 1)
    with open(README, "w", encoding="utf-8") as f:
        f.write(new)
    print("README.md parts list updated")


if __name__ == "__main__":
    main()
