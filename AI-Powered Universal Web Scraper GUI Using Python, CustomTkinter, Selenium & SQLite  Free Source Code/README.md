# Universal AI Web Scraper

A complete, production-quality desktop application written in Python. This app features a modern dark futuristic interface built with **CustomTkinter** that guides users through extracting publicly displayed web page elements using a heuristic **AI Parsing Engine** backed by **Selenium** and **BeautifulSoup4**.

---

## 🚀 Key Features

* **Heuristic AI Prompt Classifier**: Parses natural-language extraction commands (like *"extract product names and prices"*) and matches them to robust element-mapping traversal algorithms.
* **Dual Rendering core**: Utilizes **Selenium WebDriver** for executing dynamic Javascript-heavy pages and **BeautifulSoup4** for rapid, accurate HTML parsing.
* **Background Worker Threads**: Executes scraping runs in isolated threads, preventing GUI freeze and displaying live runtime stats (elapsed time, item counters, progression status).
* **Multi-Format Exports**: Saves data caches directly from SQLite into CSV, Excel (`.xlsx`), JSON, and professional landscaped PDFs (built via `ReportLab`).
* **Database Persistency**: Stores configuration settings, scrape history registries, raw tabular results, and historical execution tracing logs inside a robust SQLite engine.
* **Ethical Compliance checking**: Incorporates domain robots.txt scanning. Does not bypass firewalls, CAPTCHAs, or authentication layers, enforcing fair scraping guidelines.

---

## 🛠️ Technology Stack

* **GUI Shell**: CustomTkinter
* **Web Automation**: Selenium (uses standard Selenium Manager for driver downloads)
* **Parsing**: BeautifulSoup4 (BS4)
* **Databases**: SQLite3
* **Analytics & Spreadsheets**: Pandas, OpenPyXL
* **Reporting**: ReportLab
* **File Operations**: JSON, CSV
* **Thread safety**: Threading, Queues
* **Logging**: Standard Python Logging with database persistence and GUI log streams.

---

## 📦 Installation Guide

### Prerequisites
* Python 3.8 to 3.12 (Recommend 3.10+).
* An internet connection (needed for the first scrape to let Selenium Manager download browser drivers).

### Step-by-Step Setup
1. Clone or extract the project directory:
   ```bash
   cd "Universal AI Web Scraper"
   ```
2. Install the necessary packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

---

## 📦 How to Package into EXE using PyInstaller

To bundle the Python desktop app into a single standalone executable file (`.exe`) for Windows:

1. Install **PyInstaller**:
   ```bash
   pip install pyinstaller
   ```
2. Build the application using the following CLI parameters:
   ```bash
   pyinstaller --noconsole --onefile --name="Universal_AI_Web_Scraper" --clean app.py
   ```
   * `--noconsole`: Hides the background Windows terminal/command prompt shell when the GUI starts.
   * `--onefile`: Compresses all dependencies, custom views, components, and libraries into a single executable.
   * `--name`: Defines the target file name.

3. Locate the executable inside the generated `dist/` folder:
   ```
   dist/Universal_AI_Web_Scraper.exe
   ```

> [!NOTE]
> Since CustomTkinter relies on external asset folders (like json themes), PyInstaller handles bundling standard assets, but you can explicitly add search paths if styles fail to load on launch:
> `pyinstaller --noconsole --onefile --add-data "venv/Lib/site-packages/customtkinter;customtkinter/" app.py`

---

## 🔮 Future Improvement Ideas

1. **Local LLM Offline Parsing**: Integrate offline semantic parsing libraries (e.g. llama.cpp or Ollama APIs) to parse raw page source strings without rigid regex heuristics.
2. **Visual Selector Mode**: Add an interactive browser viewport overlay that allows users to click elements on the page, generating custom CSS/XPath selectors.
3. **Advanced Rate-Limiting Scheduling**: Incorporate recurring cron-based triggers to scrape pages daily/weekly, sending automated PDF/Excel reports to configured email servers.
4. **Proxy & Cookie profiles manager**: Enable proxy rotation arrays and session cookie imports to emulate realistic user paths across authorized pathways.
