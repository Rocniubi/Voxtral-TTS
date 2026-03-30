from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "index.html"
LOCALES_DIR = ROOT / "locales"

SUPPORTED_LOCALES = [
    {"key": "en", "lang": "en", "label": "English"},
    {"key": "zh-cn", "lang": "zh-CN", "label": "简体中文"},
    {"key": "zh-tw", "lang": "zh-TW", "label": "繁體中文"},
    {"key": "ko", "lang": "ko", "label": "한국어"},
    {"key": "ja", "lang": "ja", "label": "日本語"},
    {"key": "de", "lang": "de", "label": "Deutsch"},
    {"key": "fr", "lang": "fr", "label": "Français"},
    {"key": "es", "lang": "es", "label": "Español"},
    {"key": "pt-br", "lang": "pt-BR", "label": "Português (Brasil)"},
    {"key": "pt-pt", "lang": "pt-PT", "label": "Português"},
    {"key": "ar", "lang": "ar", "label": "العربية"},
    {"key": "ru", "lang": "ru", "label": "Русский"},
    {"key": "tr", "lang": "tr", "label": "Türkçe"},
    {"key": "sv", "lang": "sv", "label": "Svenska"},
    {"key": "nl", "lang": "nl", "label": "Nederlands"},
    {"key": "ro", "lang": "ro", "label": "Română"},
    {"key": "bg", "lang": "bg", "label": "Български"},
    {"key": "fi", "lang": "fi", "label": "Suomi"},
]


def locale_path(locale_key: str) -> str:
    return "/" if locale_key == "en" else f"/{locale_key}/"


def locale_url(locale_key: str) -> str:
    return f"https://voxtraltts.online{locale_path(locale_key)}"


def clear_and_text(tag, text: str) -> None:
    if tag is None:
        return
    tag.clear()
    tag.append(text)


def set_link(tag, config: dict) -> None:
    if tag is None or not config:
        return
    tag.clear()
    tag.append(config["title"])
    tag["href"] = config["url"]
    if config["url"].startswith("http://") or config["url"].startswith("https://"):
        tag["target"] = "_blank"
        tag["rel"] = "noreferrer"
    else:
        tag.attrs.pop("target", None)
        tag.attrs.pop("rel", None)


def render_title(soup: BeautifulSoup, tag, title: str, highlight_text: str) -> None:
    if tag is None:
        return
    tag.clear()
    if not highlight_text or highlight_text not in title:
        tag.append(title)
        return

    before, after = title.split(highlight_text, 1)
    if before:
        tag.append(before)
    highlight = soup.new_tag("span", attrs={"class": "highlight"})
    highlight.string = highlight_text
    tag.append(highlight)
    if after:
        tag.append(after)


def render_nav(soup: BeautifulSoup, container, items: list[dict]) -> None:
    if container is None:
        return
    container.clear()
    for item in items:
        link = soup.new_tag("a", href=item["url"])
        link.string = item["title"]
        container.append(link)


def render_support_points(soup: BeautifulSoup, container, items: list[str]) -> None:
    if container is None:
        return
    container.clear()
    for item in items:
        li = soup.new_tag("li")
        li.string = item
        container.append(li)


def render_cards(soup: BeautifulSoup, container, items: list[dict]) -> None:
    if container is None:
        return
    container.clear()
    for index, item in enumerate(items, start=1):
        article = soup.new_tag("article", attrs={"class": "info-card"})

        marker = soup.new_tag("div", attrs={"class": "info-card__index"})
        marker.string = str(index)
        article.append(marker)

        title = soup.new_tag("h3")
        title.string = item["title"]
        article.append(title)

        desc = soup.new_tag("p")
        desc.string = item["description"]
        article.append(desc)

        container.append(article)


def render_faq(soup: BeautifulSoup, container, items: list[dict]) -> None:
    if container is None:
        return
    container.clear()
    for index, item in enumerate(items):
        details = soup.new_tag("details", attrs={"class": "faq-item"})
        if index == 0:
            details["open"] = ""

        summary = soup.new_tag("summary")
        summary.string = item["title"]
        details.append(summary)

        body = soup.new_tag("p")
        body.string = item["description"]
        details.append(body)

        container.append(details)


def render_language_ui(soup: BeautifulSoup, locale_key: str) -> None:
    current = next((item for item in SUPPORTED_LOCALES if item["key"] == locale_key), SUPPORTED_LOCALES[0])

    current_label = soup.find(id="language-current-label")
    clear_and_text(current_label, current["label"])

    menu = soup.find(id="language-menu")
    if menu is not None:
        menu.clear()
        for item in SUPPORTED_LOCALES:
            link = soup.new_tag("a", href=locale_path(item["key"]), attrs={"class": "language-switcher__link"})
            link["lang"] = item["lang"]
            if item["key"] == locale_key:
                link["aria-current"] = "true"
            link.string = item["label"]
            menu.append(link)

    footer = soup.find(id="footer-language-links")
    if footer is not None:
        footer.clear()
        for item in SUPPORTED_LOCALES:
            link = soup.new_tag("a", href=locale_path(item["key"]), attrs={"class": "footer-language-links__link"})
            link["lang"] = item["lang"]
            if item["key"] == locale_key:
                link["aria-current"] = "true"
            link.string = item["label"]
            footer.append(link)


def render_alternates(soup: BeautifulSoup) -> None:
    head = soup.head
    if head is None:
        return

    for old in head.select('link[data-locale-alternate="true"]'):
        old.decompose()

    for item in SUPPORTED_LOCALES:
        link = soup.new_tag("link", rel="alternate", hreflang=item["lang"], href=locale_url(item["key"]))
        link["data-locale-alternate"] = "true"
        head.append(link)

    x_default = soup.new_tag("link", rel="alternate", hreflang="x-default", href=locale_url("en"))
    x_default["data-locale-alternate"] = "true"
    head.append(x_default)


def update_head(soup: BeautifulSoup, locale_key: str, content: dict) -> None:
    html_tag = soup.find("html")
    if html_tag is not None:
        html_tag["lang"] = content["locale"]

    if soup.title is not None:
        soup.title.string = content["meta"]["title"]

    meta_map = {
        ("name", "description"): content["meta"]["description"],
        ("name", "keywords"): content["meta"].get("keywords", ""),
        ("property", "og:title"): content["meta"]["title"],
        ("property", "og:description"): content["meta"]["description"],
        ("property", "og:url"): locale_url(locale_key),
        ("name", "twitter:title"): content["meta"]["title"],
        ("name", "twitter:description"): content["meta"]["description"],
    }

    for (attr_name, attr_value), value in meta_map.items():
        tag = soup.find("meta", attrs={attr_name: attr_value})
        if tag is not None:
            tag["content"] = value

    canonical = soup.find("link", rel="canonical")
    if canonical is not None:
        canonical["href"] = locale_url(locale_key)

    brand_link = soup.find(id="brand-link")
    if brand_link is not None:
        brand_link["href"] = locale_path(locale_key)

    render_alternates(soup)


def render_page(locale_key: str) -> str:
    locale_file = LOCALES_DIR / f"{locale_key}.json"
    content = json.loads(locale_file.read_text())
    template = TEMPLATE_PATH.read_text()
    template = re.sub(r"(?is)^\s*(<!doctype html>\s*)+", "", template)
    soup = BeautifulSoup(template, "html.parser")

    update_head(soup, locale_key, content)

    render_nav(soup, soup.find(id="header-nav"), content["header"]["nav"])
    render_language_ui(soup, locale_key)

    clear_and_text(soup.find(id="hero-eyebrow"), content["hero"]["eyebrow"])
    render_title(soup, soup.find(id="hero-title"), content["hero"]["title"], content["hero"].get("highlightText"))
    clear_and_text(soup.find(id="hero-description"), content["hero"]["description"])
    set_link(soup.find(id="hero-primary-button"), content["hero"]["primaryButton"])
    set_link(soup.find(id="hero-secondary-button"), content["hero"]["secondaryButton"])
    render_support_points(soup, soup.find(id="support-points"), content["hero"]["supportingPoints"])

    clear_and_text(soup.find(id="demo-title"), content["site"]["demo"]["title"])
    clear_and_text(soup.find(id="demo-description"), content["site"]["demo"]["description"])
    clear_and_text(soup.find(id="demo-note"), content["site"]["demo"]["note"])
    set_link(
        soup.find(id="demo-open-button"),
        {
            "title": content["site"]["demo"]["openLabel"],
            "url": content["site"]["demo"].get("openUrl", "#faq"),
        },
    )
    demo_iframe = soup.find(id="demo-iframe")
    if demo_iframe is not None:
        demo_iframe["title"] = content["site"]["demo"]["title"]
        demo_iframe["src"] = content["site"]["demo"]["url"]

    clear_and_text(soup.find(id="overview-label"), content["overview"]["label"])
    clear_and_text(soup.find(id="overview-title"), content["overview"]["title"])
    clear_and_text(soup.find(id="overview-description"), content["overview"]["description"])
    render_cards(soup, soup.find(id="overview-items"), content["overview"]["items"])

    clear_and_text(soup.find(id="quick-start-label"), content["quickStart"]["label"])
    clear_and_text(soup.find(id="quick-start-title"), content["quickStart"]["title"])
    clear_and_text(soup.find(id="quick-start-description"), content["quickStart"]["description"])
    render_cards(soup, soup.find(id="quick-start-items"), content["quickStart"]["items"])

    clear_and_text(soup.find(id="faq-label"), content["faq"]["label"])
    clear_and_text(soup.find(id="faq-title"), content["faq"]["title"])
    clear_and_text(soup.find(id="faq-description"), content["faq"]["description"])
    render_faq(soup, soup.find(id="faq-items"), content["faq"]["items"])

    clear_and_text(soup.find(id="cta-label"), content["cta"]["label"])
    clear_and_text(soup.find(id="cta-title"), content["cta"]["title"])
    clear_and_text(soup.find(id="cta-description"), content["cta"]["description"])
    set_link(soup.find(id="cta-primary-button"), content["cta"]["primaryButton"])
    set_link(soup.find(id="cta-secondary-button"), content["cta"]["secondaryButton"])

    return "<!doctype html>\n" + str(soup)


def main() -> None:
    for item in SUPPORTED_LOCALES:
        html = render_page(item["key"])
        if item["key"] == "en":
            target = ROOT / "index.html"
        else:
            target_dir = ROOT / item["key"]
            target_dir.mkdir(exist_ok=True)
            target = target_dir / "index.html"
        target.write_text(html)

    urls = [locale_url(item["key"]) for item in SUPPORTED_LOCALES]
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        priority = "1.0" if url == locale_url("en") else "0.8"
        sitemap_lines.extend(
            [
                "  <url>",
                f"    <loc>{url}</loc>",
                "    <changefreq>daily</changefreq>",
                f"    <priority>{priority}</priority>",
                "  </url>",
            ]
        )
    sitemap_lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap_lines) + "\n")


if __name__ == "__main__":
    main()
