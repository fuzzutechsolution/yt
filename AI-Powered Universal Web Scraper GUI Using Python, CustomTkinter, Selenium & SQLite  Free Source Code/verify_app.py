"""
Universal AI Web Scraper - Unit & Integration Verification Script
Tests DatabaseManager operations, AIHtmlParser heuristic extraction, and Exporter formats.
"""

import sys
import os
import shutil
import logging

# Ensure project root is in system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from parser import AIHtmlParser
from exporter import DataExporter

# Setup test logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def test_database():
    logger.info("--- Testing Database Manager ---")
    db = DatabaseManager.get_instance()
    
    # 1. Test settings
    db.set_setting("test_key", "test_value_123")
    val = db.get_setting("test_key")
    assert val == "test_value_123", f"Setting retrieval failed: got {val}"
    logger.info("✓ Settings read/write successful.")

    # 2. Test history entry
    hist_id = db.add_history_entry("http://localhost/test", "Extract headings", "2026-07-20 12:00:00", "RUNNING")
    assert hist_id > 0, "Failed to insert history row."
    
    db.update_history_status(hist_id, "COMPLETED", count=5)
    
    history_list = db.get_history(limit=1)
    assert len(history_list) == 1, "Failed to fetch history."
    assert history_list[0]["status"] == "COMPLETED", "Failed to update history status."
    assert history_list[0]["results_count"] == 5, "Failed to update count."
    logger.info("✓ History management successful.")

    # 3. Test results entry
    dummy_results = [{"Title": "Product A", "Price": "$10"}, {"Title": "Product B", "Price": "$20"}]
    db.save_results(hist_id, dummy_results)
    
    retrieved_results = db.get_results_for_history(hist_id)
    assert len(retrieved_results) == 2, f"Failed to retrieve results: got {len(retrieved_results)}"
    assert retrieved_results[0]["Title"] == "Product A", "Results payload corrupt."
    logger.info("✓ Results caching and JSON serialization successful.")


def test_parser():
    logger.info("--- Testing AI HTML Parser Heuristics ---")
    
    dummy_html = """
    <html>
      <head><title>Test Store</title></head>
      <body>
        <h1>Main Store Heading</h1>
        <h2>Subheading list</h2>
        
        <!-- Product items -->
        <div class="product-card">
          <h4>Cool Sneakers</h4>
          <span class="price">$120.00</span>
        </div>
        <div class="product-card">
          <h4>Retro Jacket</h4>
          <span class="price">€95.50</span>
        </div>
        
        <!-- Articles -->
        <article class="post">
          <h2><a href="/news/first-post">First Post Title</a></h2>
          <time datetime="2026-05-12">May 12, 2026</time>
        </article>

        <!-- FAQs -->
        <div class="faq">
          <dt>Is support free?</dt>
          <dd>Yes, it is 24/7 free support.</dd>
        </div>
        
        <!-- Contacts -->
        <p>Contact developer at developer@example.com or support line +1-555-0199.</p>
      </body>
    </html>
    """

    parser = AIHtmlParser("http://localhost/store")

    # 1. Heading Extraction
    res, exp = parser.parse(dummy_html, "Extract all visible headings")
    assert len(res) == 5, f"Headings count incorrect: got {len(res)}"
    assert res[0]["Heading Text"] == "Main Store Heading", "Heading text match failure."
    logger.info("✓ Heuristic Heading parser successful.")

    # 2. Product Extraction
    res, exp = parser.parse(dummy_html, "Extract product names and prices")
    assert len(res) == 2, f"Products count incorrect: got {len(res)}"
    assert res[0]["Product Name"] == "Cool Sneakers", f"Product name extraction error: got {res[0]}"
    assert res[0]["Price"] == "$120.00", f"Product price extraction error: got {res[0]}"
    logger.info("✓ Heuristic Product parser successful.")

    # 3. Article Extraction
    res, exp = parser.parse(dummy_html, "Extract article titles and publish dates")
    assert len(res) == 1, f"Articles count incorrect: got {len(res)}"
    assert res[0]["Article Title"] == "First Post Title", "Article title failure."
    assert "2026-05-12" in res[0]["Publish Date"] or "May 12, 2026" in res[0]["Publish Date"], "Article date failure."
    logger.info("✓ Heuristic Article/News parser successful.")

    # 4. FAQ Extraction
    res, exp = parser.parse(dummy_html, "Extract FAQ sections")
    assert len(res) == 1, f"FAQ count incorrect: got {len(res)}"
    assert res[0]["Question"] == "Is support free?", "FAQ question failure."
    logger.info("✓ Heuristic FAQ parser successful.")

    # 5. Contacts Extraction
    res, exp = parser.parse(dummy_html, "Extract contact information")
    assert len(res) == 2, f"Contacts count incorrect: got {len(res)}"
    emails = [r["Value"] for r in res if r["Contact Type"] == "Email Address"]
    phones = [r["Value"] for r in res if r["Contact Type"] == "Phone Number"]
    assert "developer@example.com" in emails, "Email extraction failure."
    assert "+1-555-0199" in phones, "Phone extraction failure."
    logger.info("✓ Heuristic Contact scanner successful.")


def test_exporter():
    logger.info("--- Testing Data Exporter ---")
    
    test_data = [
        {"Product Name": "Standard Notebook", "Price": "$1,200.00", "Stock": "In Stock"},
        {"Product Name": "Mechanical Keyboard", "Price": "$150.00", "Stock": "Out of Stock"},
        {"Product Name": "Wireless Mouse", "Price": "$80.00", "Stock": "In Stock"}
    ]
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_exports"))
    meta = {
        "url": "http://localhost/test-store",
        "prompt": "Extract product names and prices",
        "timestamp": "2026-07-20 12:30:00"
    }

    # Clean previous output
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # 1. Export CSV
    csv_file = DataExporter.export_data(test_data, "csv", "verify_export", output_dir, meta)
    assert os.path.exists(csv_file), "CSV file was not created."
    
    # 2. Export JSON
    json_file = DataExporter.export_data(test_data, "json", "verify_export", output_dir, meta)
    assert os.path.exists(json_file), "JSON file was not created."

    # 3. Export XLSX (Excel)
    xlsx_file = DataExporter.export_data(test_data, "xlsx", "verify_export", output_dir, meta)
    assert os.path.exists(xlsx_file), "XLSX file was not created."

    # 4. Export PDF (ReportLab)
    pdf_file = DataExporter.export_data(test_data, "pdf", "verify_export", output_dir, meta)
    assert os.path.exists(pdf_file), "PDF file was not created."

    logger.info(f"✓ Exporter verification successful. Files generated in: {output_dir}")
    
    # Cleanup files
    shutil.rmtree(output_dir)


def run_tests():
    logger.info("=================================")
    logger.info("STARTING WEB SCRAPER TEST SUITE")
    logger.info("=================================")
    try:
        test_database()
        test_parser()
        test_exporter()
        logger.info("=================================")
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("=================================")
    except Exception as e:
        logger.error("Test execution failed!", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
