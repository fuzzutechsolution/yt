"""
Universal AI Web Scraper - AI Parsing Engine
Classifies natural-language prompts and maps them to heuristic BeautifulSoup extraction routines.
Logs detailed reasoning about the chosen parsing strategy.
"""

import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class AIHtmlParser:
    """
    Parses HTML content based on natural language prompts.
    Uses pattern matching and heuristic element traversal to extract structured tables.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    def parse(self, html_content: str, prompt: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Classifies the prompt, executes the corresponding extraction strategy,
        and returns the results and a description of the strategy used.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        intent, explanation = self._classify_intent(prompt)
        logger.info(f"AI Scraper classified intent: '{intent}' based on prompt: '{prompt}'")
        
        results = []
        try:
            if intent == "headings":
                results = self._extract_headings(soup)
            elif intent == "products":
                results = self._extract_products(soup)
            elif intent == "articles":
                results = self._extract_articles(soup)
            elif intent == "table":
                results = self._extract_tables(soup)
            elif intent == "images":
                results = self._extract_images(soup)
            elif intent == "links":
                results = self._extract_links(soup)
            elif intent == "contact":
                results = self._extract_contacts(soup)
            elif intent == "faqs":
                results = self._extract_faqs(soup)
            elif intent == "blog":
                results = self._extract_blog_posts(soup)
            elif intent == "categories":
                results = self._extract_categories(soup)
            else:
                # General Keyword Fallback
                results = self._extract_keyword_matches(soup, prompt)
                explanation = f"General keyword extraction matching terms in prompt: '{prompt}'."
        except Exception as e:
            logger.error(f"Error during parsing with intent '{intent}': {e}", exc_info=True)
            explanation = f"Failed to execute parsing for intent '{intent}'. Error: {str(e)}"
            results = []

        return results, explanation

    def _classify_intent(self, prompt: str) -> Tuple[str, str]:
        """Classifies the natural language prompt using keyword heuristics."""
        p = prompt.lower().strip()
        
        if any(w in p for w in ["heading", "header", "h1", "h2", "h3", "headings"]):
            return "headings", "Extracted all structural heading tags (H1-H6) and their nesting text hierarchy."
            
        if any(w in p for w in ["product", "price", "shop", "item", "cost", "pricing"]):
            return "products", "Analyzed the DOM for lists of items containing pricing formats (e.g. $, €, £, Rs) and associated labels."
            
        if any(w in p for w in ["article", "news", "publish", "post", "author", "articles"]):
            return "articles", "Scanned for structured article elements, headers with anchors, and nearby date stamps."
            
        if any(w in p for w in ["table", "grid", "tabular", "matrix"]):
            return "table", "Located physical HTML <table> tags and extracted row-column structural data grids."
            
        if any(w in p for w in ["image", "img", "picture", "photo", "src", "images"]):
            return "images", "Extracted all image sources (img tags, lazy-load sources, alt texts, and titles)."
            
        if any(w in p for w in ["link", "url", "href", "anchors", "links"]):
            return "links", "Collected all hyperlinks (a tags) containing anchor text and absolute references."
            
        if any(w in p for w in ["contact", "email", "phone", "address", "number", "tel"]):
            return "contact", "Scanned raw textual structure of the document to extract valid email formats and phone numbers."
            
        if any(w in p for w in ["faq", "question", "answer", "frequently"]):
            return "faqs", "Detected QA sections using common classes and structural tags (dt/dd or headers ending with question marks)."
            
        if any(w in p for w in ["blog", "feed"]):
            return "blog", "Searched for elements containing blog layouts, posts, feeds, and matching headers."
            
        if any(w in p for w in ["category", "categories", "menu", "navigation", "navbar"]):
            return "categories", "Isolated menus, sidebars, lists, or headers representing structural site categories."

        return "fallback", "Could not automatically match an exact layout pattern. Falling back to keyword search."

    # --- Extraction Heuristics ---

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for header in soup.find_all(tag):
                text = header.get_text(strip=True)
                if text:
                    results.append({
                        "Heading Level": tag.upper(),
                        "Heading Text": text
                    })
        return results

    def _extract_products(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        # Find elements containing price indicators: $ or € or £ or Rs. or numeric patterns followed/preceded by currency
        price_regex = re.compile(r'(\$\s?\d+(?:[.,]\d{2})?|€\s?\d+(?:[.,]\d{2})?|£\s?\d+(?:[.,]\d{2})?|Rs\.?\s?\d+(?:[.,]\d{2})?)')
        
        # Let's search all elements containing price text
        price_nodes = soup.find_all(text=price_regex)
        if not price_nodes:
            # Fallback search for span/div with classes like price, cost, prc
            price_nodes = soup.find_all(class_=re.compile(r'(price|cost|prc|pricing)', re.IGNORECASE))

        # Track processed container nodes to avoid duplicate entries for the same product card
        processed_containers = set()

        for node in price_nodes:
            # Get parent element
            parent = node.parent if hasattr(node, 'parent') else node
            if not parent:
                continue

            # Walk up to find a container representing a product card (usually has some sizing or class)
            container = parent
            levels = 0
            while container and levels < 4:
                # Product containers often have classes like card, product, item, post, grid-cell, row
                c_name = " ".join(container.get("class", [])) if container.get("class") else ""
                if any(k in c_name.lower() for k in ["product", "card", "item", "grid", "post", "shop"]):
                    break
                container = container.parent
                levels += 1

            if not container:
                container = parent

            if container in processed_containers:
                continue
            processed_containers.add(container)

            # Find name inside container (look for header tags first, then bold elements, then longest text)
            name = ""
            for h_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b']:
                found_h = container.find(h_tag)
                if found_h:
                    name = found_h.get_text(strip=True)
                    break

            if not name:
                # Extract text excluding the price itself
                all_text = [t.strip() for t in container.find_all(text=True) if t.strip()]
                # Find longest text block that is not the price
                text_blocks = [t for t in all_text if not price_regex.search(t) and len(t) > 2]
                name = text_blocks[0] if text_blocks else "Unknown Product"

            # Re-verify/find price inside the container
            price = ""
            price_match = container.find(text=price_regex)
            if price_match:
                price = price_regex.search(price_match).group(0)
            else:
                price_text = container.get_text()
                match = price_regex.search(price_text)
                price = match.group(0) if match else "N/A"

            # Clean name length
            name = name[:100] if name else "Unknown Product"

            results.append({
                "Product Name": name,
                "Price": price
            })

        return results

    def _extract_articles(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        # Look for article blocks
        articles = soup.find_all(['article', 'section'])
        # If no explicit article tags, look for divs with article-like class names
        if not articles:
            articles = soup.find_all(class_=re.compile(r'(article|post|story|entry|news-item)', re.IGNORECASE))

        # Simple date regex helper
        date_pattern = re.compile(
            r'(\b\d{4}[-/]\d{2}[-/]\d{2}\b|\b[A-Za-z]{3}\s\d{1,2},?\s\d{4}\b|\b\d{1,2}\s[A-Za-z]{3,9}\s\d{4}\b)'
        )

        for art in articles:
            # Title: look for heading or link
            title_node = art.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=re.compile(r'(title|heading|header)', re.IGNORECASE))
            if not title_node:
                title_node = art.find(['h1', 'h2', 'h3', 'h4'])
            if not title_node:
                title_node = art.find('a')

            if not title_node:
                continue

            title = title_node.get_text(strip=True)
            if len(title) < 5: # Skip short fragments
                continue

            # Link
            link = ""
            if title_node.name == 'a' and title_node.get('href'):
                link = urljoin(self.base_url, title_node.get('href'))
            else:
                a_tag = art.find('a')
                if a_tag and a_tag.get('href'):
                    link = urljoin(self.base_url, a_tag.get('href'))

            # Publish date
            date_str = "Unknown Date"
            # Look for time tag
            time_tag = art.find('time')
            if time_tag:
                date_str = time_tag.get_text(strip=True) or time_tag.get('datetime', 'Unknown Date')
            else:
                # Look for tags with class containing 'date'
                date_node = art.find(class_=re.compile(r'(date|time|published|created)', re.IGNORECASE))
                if date_node:
                    date_str = date_node.get_text(strip=True)
                else:
                    # Scan all text block inside for a date regex
                    art_text = art.get_text()
                    match = date_pattern.search(art_text)
                    if match:
                        date_str = match.group(0)

            results.append({
                "Article Title": title,
                "Publish Date": date_str,
                "Link URL": link
            })

        # Fallback: if no articles found, grab all links that have header tags inside or nearby dates
        if not results:
            for header in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                a_tag = header.find('a') or header.parent.name == 'a' and header.parent
                if a_tag and a_tag.get('href'):
                    title = header.get_text(strip=True)
                    link = urljoin(self.base_url, a_tag.get('href'))
                    results.append({
                        "Article Title": title,
                        "Publish Date": "N/A",
                        "Link URL": link
                    })

        return results

    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        tables = soup.find_all('table')
        for t_idx, table in enumerate(tables):
            # Try to parse structure
            thead = table.find('thead')
            tbody = table.find('tbody')
            rows = table.find_all('tr')
            
            if not rows:
                continue

            # Determine headers
            headers = []
            start_row = 0
            
            if thead:
                th_elements = thead.find_all('th')
                headers = [th.get_text(strip=True) for th in th_elements]
            else:
                # Check if first row contains 'th' elements
                first_row_th = rows[0].find_all('th')
                if first_row_th:
                    headers = [th.get_text(strip=True) for th in first_row_th]
                    start_row = 1
                else:
                    # Check first row 'td' elements as headers if they are styled/bold
                    first_row_td = rows[0].find_all('td')
                    headers = [f"Column_{i+1}" for i in range(len(first_row_td))]
                    # Don't skip first row if it's actual data
            
            headers = [h if h else f"Column_{i+1}" for i, h in enumerate(headers)]

            for row in rows[start_row:]:
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue
                row_dict = {}
                # Add table index to help identify table source if multiple exist
                row_dict["Table Index"] = f"Table {t_idx + 1}"
                
                for col_idx, cell in enumerate(cells):
                    header_name = headers[col_idx] if col_idx < len(headers) else f"Extra_Col_{col_idx+1}"
                    row_dict[header_name] = cell.get_text(strip=True)
                
                # Check if row is not completely empty
                if any(v for k, v in row_dict.items() if k != "Table Index"):
                    results.append(row_dict)
                    
        return results

    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        images = soup.find_all('img')
        for idx, img in enumerate(images):
            # Extract src with lazy-load fallbacks
            src = img.get('src') or img.get('data-src') or img.get('data-lazy') or img.get('srcset')
            if not src:
                continue
            
            # Clean url
            src = urljoin(self.base_url, src.split()[0]) # split handles srcset formats (e.g. url 2x)
            alt = img.get('alt', '').strip() or "N/A"
            title = img.get('title', '').strip() or "N/A"
            
            # Dimensions
            width = img.get('width', 'Unknown')
            height = img.get('height', 'Unknown')

            results.append({
                "Image ID": idx + 1,
                "Image URL": src,
                "Alt Text": alt,
                "Title": title,
                "Dimensions": f"{width}x{height}"
            })
        return results

    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        links = soup.find_all('a', href=True)
        for idx, link in enumerate(links):
            text = link.get_text(strip=True) or link.get('title', '').strip() or "[Empty Image/Icon]"
            href = urljoin(self.base_url, link['href'])
            
            results.append({
                "Link Index": idx + 1,
                "Anchor Text": text[:150],
                "Destination URL": href
            })
        return results

    def _extract_contacts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        # Get raw visible text
        # Remove scripts, styles
        for element in soup(["script", "style", "meta", "noscript", "header", "footer"]):
            element.decompose()
        
        raw_text = soup.get_text(separator=" \n ")

        # Regular Expressions
        email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b')
        # Robust international & domestic phone numbers matcher
        phone_regex = re.compile(r'(\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{3,4}(?:[-.\s]?\d{3,4})?)')

        emails = set(email_regex.findall(raw_text))
        phones = set(phone_regex.findall(raw_text))
        
        # Strip/deduplicate phone numbers that are too short to be real numbers
        cleaned_phones = set()
        for p in phones:
            digits = re.sub(r'\D', '', p)
            if 7 <= len(digits) <= 15:
                cleaned_phones.add(p.strip())

        for email in emails:
            results.append({
                "Contact Type": "Email Address",
                "Value": email
            })

        for phone in cleaned_phones:
            results.append({
                "Contact Type": "Phone Number",
                "Value": phone
            })

        return results

    def _extract_faqs(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        # Method 1: definition lists dt / dd
        dts = soup.find_all('dt')
        dds = soup.find_all('dd')
        if len(dts) == len(dds) and dts:
            for q, a in zip(dts, dds):
                results.append({
                    "Question": q.get_text(strip=True),
                    "Answer": a.get_text(strip=True)
                })
            return results

        # Method 2: Elements with 'faq', 'question', 'answer' class names
        qa_containers = soup.find_all(class_=re.compile(r'(faq|accordion|question-answer)', re.IGNORECASE))
        for cont in qa_containers:
            q_node = cont.find(class_=re.compile(r'(question|trigger|title|header)', re.IGNORECASE))
            a_node = cont.find(class_=re.compile(r'(answer|content|body|pane)', re.IGNORECASE))
            if q_node and a_node:
                results.append({
                    "Question": q_node.get_text(strip=True),
                    "Answer": a_node.get_text(strip=True)
                })

        # Method 3: Parse elements ending with "?" and find succeeding siblings
        if not results:
            for heading in soup.find_all(['h2', 'h3', 'h4', 'strong', 'p']):
                text = heading.get_text(strip=True)
                if text.endswith('?') and len(text) > 8:
                    # Find next sibling paragraph or text
                    sibling = heading.find_next(['p', 'div', 'span'])
                    if sibling:
                        ans_text = sibling.get_text(strip=True)
                        if len(ans_text) > 10:
                            results.append({
                                "Question": text,
                                "Answer": ans_text
                            })
        
        return results

    def _extract_blog_posts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        # Map blogs similarly to articles
        results = []
        blog_containers = soup.find_all(class_=re.compile(r'(blog|post|entry|feed)', re.IGNORECASE))
        for blog in blog_containers:
            title_node = blog.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'(title|header|heading)', re.IGNORECASE))
            if not title_node:
                title_node = blog.find(['h2', 'h3'])
            
            if title_node:
                title = title_node.get_text(strip=True)
                a_tag = blog.find('a', href=True)
                link = urljoin(self.base_url, a_tag['href']) if a_tag else "N/A"
                if len(title) > 5:
                    results.append({
                        "Blog Title": title,
                        "Blog Link": link
                    })
                    
        if not results:
            # Fall back to general article layout
            return self._extract_articles(soup)
            
        return results

    def _extract_categories(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        results = []
        # Menus, sidebars, navigation
        nav_elements = soup.find_all(['nav', 'aside'])
        # Add divs with nav-like class names
        nav_elements.extend(soup.find_all(class_=re.compile(r'(menu|nav|sidebar|category|categories)', re.IGNORECASE)))
        
        processed_links = set()
        for nav in nav_elements:
            links = nav.find_all('a', href=True)
            for link in links:
                text = link.get_text(strip=True)
                href = urljoin(self.base_url, link['href'])
                if text and len(text) < 40 and href not in processed_links:
                    processed_links.add(href)
                    results.append({
                        "Category Name": text,
                        "Category URL": href
                    })
                    
        return results

    def _extract_keyword_matches(self, soup: BeautifulSoup, prompt: str) -> List[Dict[str, Any]]:
        """
        Generic extractor if no specific intent matches.
        Extracts paragraphs or text elements containing the key terms parsed from the prompt.
        """
        # Split prompt into keywords (excluding stopwords)
        stopwords = {"extract", "all", "the", "and", "or", "in", "of", "about", "for", "with", "information", "details", "data", "list", "show", "me"}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        keywords = [w for w in words if w not in stopwords]

        if not keywords:
            # Default fallback: get all paragraph contents
            results = []
            for idx, p in enumerate(soup.find_all('p')[:50]):
                text = p.get_text(strip=True)
                if len(text) > 20:
                    results.append({
                        "Item ID": idx + 1,
                        "Content Summary": text[:200]
                    })
            return results

        results = []
        matched_blocks = []
        # Search divs, paragraphs, list items
        for element in soup.find_all(['p', 'div', 'span', 'li']):
            text = element.get_text(strip=True)
            if len(text) < 15 or len(text) > 1000:
                continue
            
            # Count keyword hits
            hits = sum(1 for kw in keywords if kw in text.lower())
            if hits >= max(1, len(keywords) // 2):
                matched_blocks.append((hits, text))

        # Sort by keyword matches (descending)
        matched_blocks.sort(key=lambda x: x[0], reverse=True)
        
        # De-duplicate matches
        seen = set()
        idx = 1
        for hits, text in matched_blocks:
            cleaned_text = " ".join(text.split())
            if cleaned_text not in seen:
                seen.add(cleaned_text)
                results.append({
                    "Match ID": idx,
                    "Relevance Score": f"{hits}/{len(keywords)} terms",
                    "Text Segment": cleaned_text[:250] + ("..." if len(cleaned_text) > 250 else "")
                })
                idx += 1
                if idx > 100:  # Cap fallback results
                    break

        return results
