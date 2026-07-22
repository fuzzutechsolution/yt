import sys
import os
import json
import csv
import sqlite3
import socket
import ssl
import logging
import threading
import queue
import time
import math
import urllib.parse
import ipaddress
from datetime import datetime, date

# Networking & Scanners
import requests
import validators
import whois
import dns.resolver
import tldextract

# Image & QR
from PIL import Image, ImageTk, ImageDraw
import cv2
try:
    import pyzbar.pyzbar as pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

# GUI
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter
import tkintermapview

# Plotting
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# PDF Reporting
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Global Application Settings & Styling Colors
BG_COLOR = "#0B1220"
CARD_COLOR = "#16213E"
SIDEBAR_COLOR = "#111827"
ACCENT_COLOR = "#00E5FF"
DANGER_COLOR = "#FF3B5C"
WARNING_COLOR = "#FFC107"
SUCCESS_COLOR = "#00E676"
TEXT_COLOR = "#FFFFFF"
TEXT_MUTED = "#8A99AD"

# Application Logging Setup
logging.basicConfig(
    filename="linkshield_system.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info("LinkShield AI initialized.")

# Translation maps for English & Spanish Multi-language Support
LANGUAGES = {
    "English": {
        "dashboard": "Dashboard",
        "quick_scan": "Quick Scan",
        "scan_history": "Scan History",
        "reports": "Reports",
        "settings": "Settings",
        "about": "About LinkShield",
        "welcome": "Welcome to LinkShield AI",
        "subtitle": "AI-Powered Realtime Link Safety & Threat Intelligence Scanner",
        "total_scans": "Total Scans",
        "clean_scans": "Clean Links",
        "warning_scans": "Warnings Triggered",
        "malicious_scans": "Threats Blocked",
        "recent_scans": "Recent Security Scans",
        "scan_chart_title": "Average Risk Assessment (Last 7 Scans)",
        "url_to_scan": "Enter URL to scan securely...",
        "btn_scan": "Scan Link",
        "btn_clear": "Clear",
        "btn_paste": "Paste",
        "btn_qr": "Scan QR",
        "status_ready": "System Status: Ready",
        "status_scanning": "Scanning Target URL...",
        "risk_gauge_title": "Risk Gauge",
        "tab_summary": "Summary",
        "tab_domain": "Domain Info",
        "tab_ssl": "SSL Cert",
        "tab_geo": "Server Location",
        "tab_redirects": "Redirect Trace",
        "tab_whois": "Raw WHOIS",
        "search_history": "Search URLs in history...",
        "filter_all": "All Records",
        "filter_today": "Today Only",
        "filter_week": "This Week",
        "filter_danger": "Threats Only",
        "filter_safe": "Clean Only",
        "btn_delete_selected": "Delete Scan Record",
        "btn_clear_history": "Wipe Local History",
        "btn_export_full": "Export All History Data",
        "settings_title": "Application Configuration",
        "lbl_theme": "UI Theme Mode:",
        "lbl_lang": "Interface Language:",
        "lbl_autosave": "Auto-Save Scan History to SQL DB:",
        "lbl_notifications": "System Sound & Alerts:",
        "lbl_export_path": "Default Reports Export Folder:",
        "btn_save_settings": "Apply Settings Configuration",
        "about_version": "Version: 1.2.0 (Stable Commercial)",
        "about_description": "LinkShield AI is an enterprise-grade desktop utility that intercepts, trace, and dissects URLs, tracking complete HTTP redirections, verifying SSL validity, resolving hosting geolocation, and applying machine risk heuristics to prevent cyber attacks.",
        "lbl_ready": "Ready to Scan",
        "alert_title": "Scan Complete",
        "lbl_no_history": "No records in system scan history yet.",
        "msg_invalid_url": "The input URL is not formatted correctly. Please verify.",
        "msg_scan_err": "An error occurred during safety scanner run: "
    },
    "Spanish": {
        "dashboard": "Tablero",
        "quick_scan": "Escaneo Rápido",
        "scan_history": "Historial de Escaneo",
        "reports": "Reportes",
        "settings": "Ajustes",
        "about": "Acerca de",
        "welcome": "Bienvenido a LinkShield AI",
        "subtitle": "Escáner de Seguridad de Enlaces e Inteligencia de Amenazas por IA",
        "total_scans": "Escaneos Totales",
        "clean_scans": "Enlaces Limpios",
        "warning_scans": "Alertas Generadas",
        "malicious_scans": "Amenazas Bloqueadas",
        "recent_scans": "Escaneos de Seguridad Recientes",
        "scan_chart_title": "Evaluación de Riesgo Promedio (Últimos 7 Escaneos)",
        "url_to_scan": "Ingrese URL para escanear de forma segura...",
        "btn_scan": "Escanear Enlace",
        "btn_clear": "Limpiar",
        "btn_paste": "Pegar",
        "btn_qr": "Escanear QR",
        "status_ready": "Estado del Sistema: Listo",
        "status_scanning": "Escaneando URL Objetivo...",
        "risk_gauge_title": "Indicador de Riesgo",
        "tab_summary": "Resumen",
        "tab_domain": "Información de Dominio",
        "tab_ssl": "Certificado SSL",
        "tab_geo": "Ubicación del Servidor",
        "tab_redirects": "Ruta de Redirecciones",
        "tab_whois": "WHOIS Completo",
        "search_history": "Buscar URLs en historial...",
        "filter_all": "Todos los Registros",
        "filter_today": "Solo Hoy",
        "filter_week": "Esta Semana",
        "filter_danger": "Solo Amenazas",
        "filter_safe": "Solo Limpios",
        "btn_delete_selected": "Eliminar Registro de Escaneo",
        "btn_clear_history": "Limpiar Historial Local",
        "btn_export_full": "Exportar Datos de Historial Completo",
        "settings_title": "Configuración del Aplicativo",
        "lbl_theme": "Modo de Tema de Interfaz:",
        "lbl_lang": "Idioma del Sistema:",
        "lbl_autosave": "Auto-guardar historial de escaneos en SQL DB:",
        "lbl_notifications": "Alertas de Sonido y Sistema:",
        "lbl_export_path": "Carpeta de Exportación de Reportes:",
        "btn_save_settings": "Aplicar Configuración",
        "about_version": "Versión: 1.2.0 (Estable Comercial)",
        "about_description": "LinkShield AI es una utilidad de escritorio empresarial que intercepta, rastrea y analiza URLs, registrando redirecciones HTTP, validando SSL, resolviendo geolocalización de servidores y aplicando heurísticas de riesgo.",
        "lbl_ready": "Listo para Escanear",
        "alert_title": "Escaneo Completado",
        "lbl_no_history": "No hay registros en el historial de escaneo aún.",
        "msg_invalid_url": "La URL ingresada no tiene un formato válido. Verifique.",
        "msg_scan_err": "Ocurrió un error en el escáner de seguridad: "
    }
}

# =====================================================================
# DATABASE HELPER CLASS
# =====================================================================
class DatabaseHelper:
    def __init__(self, db_path="linkshield.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    url TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    result_status TEXT NOT NULL,
                    details_json TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize SQLite database: {e}")

    def save_scan(self, url, risk_score, result_status, details):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            details_json = json.dumps(details)
            # Use local time for timestamp instead of default current_timestamp UTC
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO scan_history (timestamp, url, risk_score, result_status, details_json)
                VALUES (?, ?, ?, ?, ?)
            """, (now_str, url, risk_score, result_status, details_json))
            conn.commit()
            conn.close()
            logging.info(f"Saved scan results for URL: {url}")
        except Exception as e:
            logging.error(f"Failed to save scan: {e}")

    def get_history(self, search_query=None, filter_type="All Records"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = "SELECT id, timestamp, url, risk_score, result_status, details_json FROM scan_history"
            conditions = []
            params = []

            if search_query:
                conditions.append("url LIKE ?")
                params.append(f"%{search_query}%")

            if filter_type in ("Today Only", "Solo Hoy"):
                conditions.append("date(timestamp) = date('now')")
            elif filter_type in ("This Week", "Esta Semana"):
                conditions.append("date(timestamp) >= date('now', '-7 days')")
            elif filter_type in ("Threats Only", "Solo Amenazas"):
                conditions.append("result_status = 'DANGEROUS'")
            elif filter_type in ("Clean Only", "Solo Limpios"):
                conditions.append("result_status = 'SAFE'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY timestamp DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            history = []
            for row in rows:
                history.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "url": row[2],
                    "risk_score": row[3],
                    "result_status": row[4],
                    "details": json.loads(row[5])
                })
            return history
        except Exception as e:
            logging.error(f"Failed to fetch scan history: {e}")
            return []

    def delete_scan(self, scan_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_history WHERE id = ?", (scan_id,))
            conn.commit()
            conn.close()
            logging.info(f"Deleted scan record: {scan_id}")
        except Exception as e:
            logging.error(f"Failed to delete scan ID {scan_id}: {e}")

    def clear_history(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_history")
            conn.commit()
            conn.close()
            logging.info("Cleared scan history database completely.")
        except Exception as e:
            logging.error(f"Failed to clear history: {e}")

    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scan_history")
            total = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM scan_history WHERE result_status = 'SAFE'")
            safe = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM scan_history WHERE result_status = 'WARNING'")
            warning = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM scan_history WHERE result_status = 'DANGEROUS'")
            dangerous = cursor.fetchone()[0] or 0

            conn.close()
            return {"total": total, "safe": safe, "warning": warning, "dangerous": dangerous}
        except Exception as e:
            logging.error(f"Failed to fetch statistics: {e}")
            return {"total": 0, "safe": 0, "warning": 0, "dangerous": 0}

    def get_recent_scans(self, limit=5):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, url, risk_score, result_status, details_json
                FROM scan_history ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()
            history = []
            for row in rows:
                history.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "url": row[2],
                    "risk_score": row[3],
                    "result_status": row[4],
                    "details": json.loads(row[5])
                })
            return history
        except Exception as e:
            logging.error(f"Failed to fetch recent scans: {e}")
            return []


# =====================================================================
# SAFETY & RISK ANALYSIS SCANNER ENGINE
# =====================================================================
class LinkShieldScanner:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.max_redirects = 10
        self.timeout = 4.0

    def update_progress(self, message, percentage):
        if self.progress_callback:
            self.progress_callback(message, percentage)

    def scan(self, target_url):
        self.update_progress("Normalizing and validating URL format...", 5)
        raw_url = target_url.strip()
        url = raw_url
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Simple schema / validity verification
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.netloc:
            url = "https://" + raw_url
            parsed_url = urllib.parse.urlparse(url)

        if not validators.url(url):
            logging.warning(f"Invalid URL entered: {raw_url}")
            raise ValueError("URL syntax is invalid.")

        self.update_progress("Tracing potential HTTP redirect links...", 15)
        redirect_chain = []
        current_url = url
        hops = 0
        too_many_redirects = False
        hidden_redirect = False

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 LinkShieldAI/1.2"
        })

        while hops < self.max_redirects:
            try:
                # Do a HEAD request first, if it fails fallback to GET to avoid hangs
                try:
                    response = session.head(current_url, allow_redirects=False, timeout=self.timeout)
                except Exception:
                    response = session.get(current_url, allow_redirects=False, timeout=self.timeout)

                redirect_chain.append({
                    "hop": hops + 1,
                    "url": current_url,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                })

                if response.status_code in (301, 302, 303, 307, 308):
                    loc = response.headers.get("Location")
                    if loc:
                        next_url = urllib.parse.urljoin(current_url, loc)
                        if next_url == current_url:
                            break  # Self redirect cycle detected
                        current_url = next_url
                        hops += 1
                    else:
                        break
                else:
                    break
            except Exception as e:
                redirect_chain.append({
                    "hop": hops + 1,
                    "url": current_url,
                    "error": str(e),
                    "status_code": 0
                })
                logging.error(f"Redirect trace error at hop {hops}: {e}")
                break

        if hops >= self.max_redirects:
            too_many_redirects = True

        final_url = current_url
        final_parsed = urllib.parse.urlparse(final_url)
        final_domain = final_parsed.netloc.split(":")[0] if ":" in final_parsed.netloc else final_parsed.netloc

        self.update_progress("Extracting registrar registry information...", 30)
        ext = tldextract.extract(final_url)
        registered_domain = ext.registered_domain
        domain_name = ext.domain
        tld = ext.suffix

        self.update_progress("Running Domain DNS lookups...", 45)
        dns_records = {}
        dns_resolved_ip = None
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 2.0
            resolver.lifetime = 2.0
            for record_type in ["A", "AAAA", "MX", "TXT", "NS", "SOA", "CNAME"]:
                try:
                    answers = resolver.resolve(final_domain, record_type)
                    dns_records[record_type] = [str(rdata) for rdata in answers]
                    if record_type == "A" and dns_records["A"]:
                        dns_resolved_ip = dns_records["A"][0]
                except Exception:
                    dns_records[record_type] = []
        except Exception as e:
            logging.error(f"DNS resolution failure: {e}")
            try:
                dns_resolved_ip = socket.gethostbyname(final_domain)
                dns_records["A"] = [dns_resolved_ip]
            except Exception:
                pass

        self.update_progress("Evaluating SSL / TLS cipher properties...", 65)
        ssl_analysis = {
            "valid": False,
            "has_cert": False,
            "issuer": "N/A",
            "expiry": "N/A",
            "cipher": "N/A",
            "version": "N/A",
            "error": "No SSL/TLS active connection established."
        }
        if final_url.lower().startswith("https://"):
            try:
                context = ssl.create_default_context()
                with socket.create_connection((final_domain, 443), timeout=3.0) as sock:
                    with context.wrap_socket(sock, server_hostname=final_domain) as ssock:
                        cert = ssock.getpeercert()
                        cipher = ssock.cipher()
                        version = ssock.version()
                        ssl_analysis["valid"] = True
                        ssl_analysis["has_cert"] = True
                        ssl_analysis["cipher"] = f"{cipher[0]} ({cipher[1]} bits)"
                        ssl_analysis["version"] = version

                        if cert:
                            expiry_str = cert.get("notAfter")
                            if expiry_str:
                                ssl_analysis["expiry"] = expiry_str
                            issuer_data = cert.get("issuer")
                            if issuer_data:
                                issuer_parts = []
                                for item in issuer_data:
                                    for k, v in item:
                                        if k in ("commonName", "organizationName"):
                                            issuer_parts.append(v)
                                ssl_analysis["issuer"] = ", ".join(issuer_parts) if issuer_parts else str(issuer_data)
            except Exception as e:
                ssl_analysis["error"] = str(e)
                # Try unverified socket extraction to check presence of an invalid cert
                try:
                    context_unverified = ssl._create_unverified_context()
                    with socket.create_connection((final_domain, 443), timeout=2.0) as sock:
                        with context_unverified.wrap_socket(sock, server_hostname=final_domain) as ssock:
                            ssl_analysis["has_cert"] = True
                            ssl_analysis["cipher"] = str(ssock.cipher()[0])
                            ssl_analysis["version"] = ssock.version()
                            ssl_analysis["issuer"] = "Self-Signed or Expired Certificate"
                            ssl_analysis["expiry"] = "Untrusted / Validation error"
                            ssl_analysis["error"] = f"SSL Validation failed: {e}"
                except Exception:
                    pass

        self.update_progress("Retrieving registration age details (WHOIS)...", 80)
        whois_raw = ""
        whois_data = {
            "registrar": "Unknown",
            "creation_date": "Unknown",
            "expiration_date": "Unknown",
            "updated_date": "Unknown",
            "domain_age_days": "Unknown",
            "name_servers": "Unknown"
        }
        try:
            w = whois.whois(final_domain)
            whois_raw = str(w)
            whois_data["registrar"] = w.registrar or "Unknown"

            c_date = w.creation_date
            if c_date:
                if isinstance(c_date, list):
                    c_date = c_date[0]
                whois_data["creation_date"] = c_date.strftime("%Y-%m-%d") if hasattr(c_date, "strftime") else str(c_date)
                if isinstance(c_date, datetime):
                    age = (datetime.now() - c_date).days
                    whois_data["domain_age_days"] = f"{age} days"
                elif isinstance(c_date, date) and not isinstance(c_date, datetime):
                    age = (date.today() - c_date).days
                    whois_data["domain_age_days"] = f"{age} days"

            e_date = w.expiration_date
            if e_date:
                if isinstance(e_date, list):
                    e_date = e_date[0]
                whois_data["expiration_date"] = e_date.strftime("%Y-%m-%d") if hasattr(e_date, "strftime") else str(e_date)

            u_date = w.updated_date
            if u_date:
                if isinstance(u_date, list):
                    u_date = u_date[0]
                whois_data["updated_date"] = u_date.strftime("%Y-%m-%d") if hasattr(u_date, "strftime") else str(u_date)

            ns = w.name_servers
            if ns:
                whois_data["name_servers"] = ", ".join(ns) if isinstance(ns, list) else str(ns)
        except Exception as e:
            whois_raw = f"WHOIS extraction failed: {e}"

        self.update_progress("Resolving ISP Server Geolocation coordinates...", 90)
        geo_data = {
            "ip": dns_resolved_ip or "Unknown",
            "country": "Unknown",
            "country_code": "US",
            "city": "Unknown",
            "isp": "Unknown",
            "timezone": "Unknown",
            "asn": "Unknown",
            "latitude": 37.0902, # default US coordinates
            "longitude": -95.7129
        }
        if dns_resolved_ip and dns_resolved_ip != "Unknown":
            try:
                # Use standard ip-api for public resolution (free, non-commercial use)
                geo_resp = requests.get(f"http://ip-api.com/json/{dns_resolved_ip}", timeout=3.0)
                if geo_resp.status_code == 200:
                    geo_json = geo_resp.json()
                    if geo_json.get("status") == "success":
                        geo_data["country"] = geo_json.get("country", "Unknown")
                        geo_data["country_code"] = geo_json.get("countryCode", "US")
                        geo_data["city"] = geo_json.get("city", "Unknown")
                        geo_data["isp"] = geo_json.get("isp", "Unknown")
                        geo_data["timezone"] = geo_json.get("timezone", "Unknown")
                        geo_data["asn"] = geo_json.get("as", "Unknown")
                        geo_data["latitude"] = float(geo_json.get("lat", 37.0902))
                        geo_data["longitude"] = float(geo_json.get("lon", -95.7129))
            except Exception as e:
                logging.error(f"IP Geolocation request failed: {e}")

        self.update_progress("Applying LinkShield AI safety heuristics...", 95)
        risk_score = 100
        reasons = []

        # 1. SSL/HTTPS check
        if not final_url.lower().startswith("https://"):
            risk_score -= 15
            reasons.append({
                "rule": "Unencrypted Connection (No HTTPS)",
                "deduction": 15,
                "description": "The destination URL does not implement HTTPS encryption. Credentials and cookies can be easily intercepted in transit."
            })

        if final_url.lower().startswith("https://"):
            if not ssl_analysis["valid"]:
                deduction_amt = 30 if not ssl_analysis["has_cert"] else 20
                risk_score -= deduction_amt
                reasons.append({
                    "rule": "SSL Trust Verification Failure",
                    "deduction": deduction_amt,
                    "description": ssl_analysis.get("error", "The remote SSL server certificate failed trust validation.")
                })

        # 2. Redirect check
        short_domains = ["bit.ly", "tinyurl.com", "cutt.ly", "t.ly", "rb.gy", "is.gd", "ow.ly", "goo.gl", "buff.ly", "tiny.cc", "t.co", "lnkd.in"]
        initial_parsed = urllib.parse.urlparse(url)
        initial_domain = initial_parsed.netloc.lower()
        if any(sd in initial_domain for sd in short_domains):
            risk_score -= 5
            reasons.append({
                "rule": "Shortened / Obfuscated Domain",
                "deduction": 5,
                "description": f"URL uses a link shortener service ({initial_domain}) commonly chosen to mask real destinations."
            })

        if len(redirect_chain) > 3:
            deduction_amt = min(25, (len(redirect_chain) - 3) * 5 + 10)
            risk_score -= deduction_amt
            reasons.append({
                "rule": "Excessive Redirection Chain",
                "deduction": deduction_amt,
                "description": f"The scanner followed {len(redirect_chain)} redirects. Deep redirect loops are used to evade security scanners."
            })

        # 3. IP address representation check
        try:
            ipaddress.ip_address(final_domain)
            risk_score -= 25
            reasons.append({
                "rule": "Numeric IP Host Target",
                "deduction": 25,
                "description": "The URL specifies a numeric IP address instead of a standard hostname domain. Genuine websites rarely use IP endpoints."
            })
        except ValueError:
            pass

        # 4. Phishing brand keywords check
        keywords = ["login", "signin", "verify", "update", "secure", "bank", "account", "wallet", "paypal", "netflix", "microsoft", "google", "facebook", "instagram", "amazon", "discord", "steam", "github", "openai", "apple"]
        full_url_lower = final_url.lower()
        path_query_lower = (final_parsed.path + final_parsed.query).lower()
        found_keywords = [kw for kw in keywords if kw in path_query_lower]
        if found_keywords:
            deduction_amt = min(30, len(found_keywords) * 10)
            risk_score -= deduction_amt
            reasons.append({
                "rule": "Phishing Keywords in Path",
                "deduction": deduction_amt,
                "description": f"The URL path contains brand impersonation keywords: {', '.join(found_keywords)}."
            })

        # 5. Suspicious TLD check
        suspicious_tlds = ["xyz", "top", "gq", "work", "loan", "click", "cf", "ml", "ga", "club", "info", "bid", "date", "download", "men", "win", "stream", "racing", "science"]
        if tld.lower() in suspicious_tlds:
            risk_score -= 10
            reasons.append({
                "rule": "Suspicious TLD",
                "deduction": 10,
                "description": f"The domain uses the '.{tld}' extension, which has a very high mathematical rate of abuse."
            })

        # 6. Unicode Homograph attacks
        if final_domain.startswith("xn--"):
            risk_score -= 30
            reasons.append({
                "rule": "IDN Punycode Homograph Spoofing",
                "deduction": 30,
                "description": "The domain is Punycode (xn--), which simulates standard domain spellings using visual lookalike characters."
            })
        else:
            try:
                final_domain.encode("ascii")
            except UnicodeEncodeError:
                risk_score -= 30
                reasons.append({
                    "rule": "Unicode Domain Characters Found",
                    "deduction": 30,
                    "description": "The hostname uses non-ASCII characters, which is a key indicator of homograph brand spoofing."
                })

        # 7. URL Length
        if len(final_url) > 130:
            deduction_amt = 5 if len(final_url) <= 200 else 10
            risk_score -= deduction_amt
            reasons.append({
                "rule": "Excessive Link Length",
                "deduction": deduction_amt,
                "description": f"URL length is {len(final_url)} characters. Threat actors use extremely long links to hide active scripts."
            })

        # 8. Script injections
        js_patterns = ["<script", "script>", "javascript:", "onload=", "onerror=", "eval(", "alert(", "document.cookie"]
        found_js = [pat for pat in js_patterns if pat in full_url_lower]
        if found_js:
            risk_score -= 30
            reasons.append({
                "rule": "Active Script Injection",
                "deduction": 30,
                "description": f"The URL path contains syntax elements that simulate client-side JavaScript injection attacks: {', '.join(found_js)}."
            })

        # 9. Directory traversal
        traversal_patterns = ["../", "..\\", "%2e%2e%2f", "%2e%2e%5c"]
        found_traversal = [pat for pat in traversal_patterns if pat in full_url_lower]
        if found_traversal:
            risk_score -= 25
            reasons.append({
                "rule": "Directory Traversal Attack",
                "deduction": 25,
                "description": "Path strings indicate directory traversal patterns used to read local system configuration files."
            })

        # 10. Open redirects in query
        open_redirect_params = ["url=", "redirect=", "next=", "dest=", "destination=", "target=", "r=", "link=", "goto=", "forward="]
        has_open_redirect = False
        parsed_query = urllib.parse.parse_qs(final_parsed.query)
        for param, values in parsed_query.items():
            if param.lower() in open_redirect_params:
                for val in values:
                    if val.startswith(("http://", "https://")):
                        has_open_redirect = True
                        break
        if has_open_redirect:
            risk_score -= 20
            reasons.append({
                "rule": "Open Redirect vulnerability",
                "deduction": 20,
                "description": "The URL parameters contain external links. This pattern is abused to bypass security filters on safe domains."
            })

        # 11. Levenshtein TypoSquatting Brand checks
        brands = ["google", "microsoft", "facebook", "instagram", "amazon", "paypal", "netflix", "discord", "steam", "github", "openai", "apple"]
        
        def calculate_levenshtein(s1, s2):
            if len(s1) < len(s2):
                return calculate_levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            prev_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                cur_row = [i + 1]
                for j, c2 in enumerate(s2):
                    ins = prev_row[j + 1] + 1
                    dels = cur_row[j] + 1
                    subs = prev_row[j] + (c1 != c2)
                    cur_row.append(min(ins, dels, subs))
                prev_row = cur_row
            return prev_row[-1]

        impersonated = None
        for brand in brands:
            if domain_name != brand:
                dist = calculate_levenshtein(domain_name, brand)
                if dist <= 2 and abs(len(domain_name) - len(brand)) <= 2:
                    impersonated = brand
                    break
                elif brand in domain_name:
                    impersonated = brand
                    break

        if impersonated:
            risk_score -= 30
            reasons.append({
                "rule": "Brand Typosquatting / Impersonation",
                "deduction": 30,
                "description": f"The domain '{domain_name}' simulates the official corporate brand '{impersonated}' using character substitutions."
            })

        # Final score sanitization
        risk_score = max(0, min(100, risk_score))
        if risk_score >= 85:
            result_status = "SAFE"
        elif risk_score >= 50:
            result_status = "WARNING"
        else:
            result_status = "DANGEROUS"

        self.update_progress("Scan analysis complete.", 100)

        return {
            "url": raw_url,
            "final_url": final_url,
            "risk_score": risk_score,
            "result_status": result_status,
            "reasons": reasons,
            "dns_records": dns_records,
            "ssl_analysis": ssl_analysis,
            "whois": whois_data,
            "whois_raw": whois_raw,
            "geo_data": geo_data,
            "redirect_chain": redirect_chain,
            "too_many_redirects": too_many_redirects,
            "hidden_redirect": hidden_redirect
        }


# =====================================================================
# THREADED WORKER CONTROLLER
# =====================================================================
class ScanWorkerThread(threading.Thread):
    def __init__(self, target_url, result_queue, progress_callback):
        super().__init__()
        self.target_url = target_url
        self.result_queue = result_queue
        self.progress_callback = progress_callback
        self.daemon = True

    def run(self):
        try:
            scanner = LinkShieldScanner(progress_callback=self.progress_callback)
            scan_result = scanner.scan(self.target_url)
            self.result_queue.put(("SUCCESS", scan_result))
        except Exception as e:
            logging.error(f"Background worker thread failed: {e}")
            self.result_queue.put(("ERROR", str(e)))


# =====================================================================
# CUSTOM GAUGE WIDGET USING TKINTER CANVAS
# =====================================================================
class ThreatGauge(customtkinter.CTkCanvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, bg=CARD_COLOR, **kwargs)
        self.score = 100.0
        self.target_score = 100.0
        self.bind("<Configure>", self.draw_gauge)

    def set_score(self, new_score):
        self.target_score = float(new_score)
        self.animate_score()

    def animate_score(self):
        if abs(self.score - self.target_score) > 0.6:
            self.score += (self.target_score - self.score) * 0.18
            self.draw_gauge()
            self.after(20, self.animate_score)
        else:
            self.score = self.target_score
            self.draw_gauge()

    def draw_gauge(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 15 or h < 15:
            return

        cx = w / 2
        cy = h * 0.62
        r = min(w * 0.38, h * 0.52)

        # Draw base arc track
        self.create_arc(cx - r, cy - r, cx + r, cy + r, start=225, extent=-270,
                        style=tk.ARC, outline="#1E293B", width=16)

        # Map color values dynamically
        if self.score >= 85:
            color = SUCCESS_COLOR
            status_text = "SAFE"
        elif self.score >= 50:
            color = WARNING_COLOR
            status_text = "WARNING"
        else:
            color = DANGER_COLOR
            status_text = "DANGEROUS"

        # Draw actual threat arc based on current frame score
        extent_angle = -270.0 * (self.score / 100.0)
        self.create_arc(cx - r, cy - r, cx + r, cy + r, start=225, extent=extent_angle,
                        style=tk.ARC, outline=color, width=16)

        # Draw pointer needle
        needle_deg = 225.0 - (270.0 * (self.score / 100.0))
        needle_rad = math.radians(needle_deg)
        needle_len = r * 0.8
        nx = cx + needle_len * math.cos(needle_rad)
        ny = cy - needle_len * math.sin(needle_rad)

        self.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill="#FFFFFF", outline="#0B1220", width=2)
        self.create_line(cx, cy, nx, ny, fill="#FFFFFF", width=3, arrow=tk.LAST, arrowshape=(10, 12, 4))

        # Core HUD text metrics
        self.create_text(cx, cy + r * 0.3, text=f"{int(self.score)}", fill="#FFFFFF",
                         font=("Segoe UI", 36, "bold"))
        self.create_text(cx, cy + r * 0.65, text=status_text, fill=color,
                         font=("Segoe UI", 16, "bold"))


# =====================================================================
# MAIN WINDOW FRAME IMPLEMENTATION
# =====================================================================
class LinkShieldApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Read config options from user environment settings or set defaults
        self.current_language = "English"
        self.theme_mode = "Dark"
        self.animations_enabled = True
        self.autosave_enabled = True
        self.notifications_enabled = True
        self.export_path = os.path.join(os.path.expanduser("~"), "Desktop")

        self.db = DatabaseHelper()
        self.worker_queue = queue.Queue()
        self.latest_result = None

        # Window properties
        self.title("LinkShield AI - Cyber Safety URL Tracer")
        self.geometry("1280x820")
        self.minsize(1100, 750)
        
        # Color schemes & appearance initialization
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.configure(fg_color=BG_COLOR)

        # Define internal grid system
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main View
        self.grid_rowconfigure(0, weight=0)    # Topbar
        self.grid_rowconfigure(1, weight=1)    # Dynamic Panels
        self.grid_rowconfigure(2, weight=0)    # Statusbar

        self.setup_ui_layout()
        self.bind_shortcuts()
        self.switch_view("dashboard")
        self.start_clock_update()

    def setup_ui_layout(self):
        # 1. TOP BAR PANEL
        self.top_bar = customtkinter.CTkFrame(self, height=65, fg_color=SIDEBAR_COLOR, corner_radius=0)
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_bar.grid_propagate(False)

        # Brand / Logo details
        self.logo_label = customtkinter.CTkLabel(
            self.top_bar, text="🛡️ LinkShield AI",
            font=("Segoe UI", 20, "bold"), text_color=ACCENT_COLOR
        )
        self.logo_label.pack(side="left", padx=25)

        # Global Search Bar inside Topbar
        self.search_val = tk.StringVar()
        self.search_entry = customtkinter.CTkEntry(
            self.top_bar, width=320, placeholder_text="Search threat history database...",
            textvariable=self.search_val, fg_color=CARD_COLOR, border_color="#2B3654", text_color="#FFFFFF"
        )
        self.search_entry.pack(side="left", padx=50, pady=18)
        self.search_entry.bind("<Return>", self.trigger_global_search)

        # Current Clock Display widget
        self.clock_lbl = customtkinter.CTkLabel(
            self.top_bar, text="00:00:00", font=("Consolas", 14), text_color=TEXT_MUTED
        )
        self.clock_lbl.pack(side="right", padx=25)

        # Theme Switcher Control
        self.theme_toggle = customtkinter.CTkSwitch(
            self.top_bar, text="Light Theme Mode", command=self.toggle_gui_theme,
            progress_color=ACCENT_COLOR, text_color=TEXT_COLOR
        )
        self.theme_toggle.pack(side="right", padx=15)

        # 2. LEFT SIDEBAR PANEL
        self.sidebar = customtkinter.CTkFrame(self, width=220, fg_color=SIDEBAR_COLOR, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nss")
        self.sidebar.grid_propagate(False)

        self.sidebar_buttons = {}
        menu_items = [
            ("dashboard", "📊  Dashboard"),
            ("quick_scan", "🚀  Quick Scan"),
            ("scan_history", "📜  Scan History"),
            ("reports", "📁  Reports Portal"),
            ("settings", "⚙️  Settings"),
            ("about", "ℹ️  About LinkShield")
        ]

        # Draw Nav buttons
        for key, text in menu_items:
            btn = customtkinter.CTkButton(
                self.sidebar, text=text, font=("Segoe UI", 14),
                anchor="w", fg_color="transparent", text_color=TEXT_COLOR,
                hover_color=CARD_COLOR, height=45, corner_radius=6,
                command=lambda k=key: self.switch_view(k)
            )
            btn.pack(fill="x", padx=12, pady=6)
            self.sidebar_buttons[key] = btn

        # 3. CENTRAL PANEL ROUTER VIEWPORT
        self.main_viewport = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_viewport.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        
        # Init View pages cache
        self.views = {
            "dashboard": self.create_dashboard_view(),
            "quick_scan": self.create_quick_scan_view(),
            "scan_history": self.create_scan_history_view(),
            "reports": self.create_reports_view(),
            "settings": self.create_settings_view(),
            "about": self.create_about_view()
        }

        # 4. BOTTOM STATUS BAR
        self.status_bar = customtkinter.CTkFrame(self, height=30, fg_color=SIDEBAR_COLOR, corner_radius=0)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_propagate(False)

        self.status_lbl = customtkinter.CTkLabel(
            self.status_bar, text="Ready to scan", font=("Segoe UI", 12), text_color=SUCCESS_COLOR
        )
        self.status_lbl.pack(side="left", padx=20)

        self.status_progress = customtkinter.CTkProgressBar(
            self.status_bar, width=200, height=8, progress_color=ACCENT_COLOR
        )
        self.status_progress.pack(side="right", padx=20, pady=11)
        self.status_progress.set(0)

    # =====================================================================
    # VIEWPORT GENERATORS & SWITCHER LAYOUTS
    # =====================================================================
    def switch_view(self, target_key):
        for key, frame in self.views.items():
            frame.grid_forget()

        # Update active nav indicator highlights
        for key, button in self.sidebar_buttons.items():
            if key == target_key:
                button.configure(fg_color=CARD_COLOR, text_color=ACCENT_COLOR)
            else:
                button.configure(fg_color="transparent", text_color=TEXT_COLOR)

        self.views[target_key].grid(row=0, column=0, sticky="nsew")
        self.main_viewport.grid_columnconfigure(0, weight=1)
        self.main_viewport.grid_rowconfigure(0, weight=1)

        # Refresh database-linked stats or dashboards
        if target_key == "dashboard":
            self.refresh_dashboard_metrics()
        elif target_key == "scan_history":
            self.refresh_history_table()

    # 1. VIEW: DASHBOARD PANEL
    def create_dashboard_view(self):
        view = customtkinter.CTkFrame(self.main_viewport, fg_color="transparent")
        view.grid_columnconfigure((0, 1, 2, 3), weight=1)
        view.grid_rowconfigure(0, weight=0) # Title
        view.grid_rowconfigure(1, weight=0) # Cards Grid
        view.grid_rowconfigure(2, weight=1) # Graph & Logs

        # Welcome Text block
        self.dash_title = customtkinter.CTkLabel(
            view, text="Welcome to LinkShield AI", font=("Segoe UI", 24, "bold"), text_color=TEXT_COLOR, anchor="w"
        )
        self.dash_title.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 5))

        self.dash_sub = customtkinter.CTkLabel(
            view, text="AI-Powered Realtime Link Safety & Threat Intelligence Scanner",
            font=("Segoe UI", 13), text_color=TEXT_MUTED, anchor="w"
        )
        self.dash_sub.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))

        # Metrics cards configurations
        self.card_total = self.draw_metric_card(view, "Total Scans", "0", 0, ACCENT_COLOR)
        self.card_clean = self.draw_metric_card(view, "Clean Links", "0", 1, SUCCESS_COLOR)
        self.card_warn = self.draw_metric_card(view, "Warnings Triggered", "0", 2, WARNING_COLOR)
        self.card_threat = self.draw_metric_card(view, "Threats Blocked", "0", 3, DANGER_COLOR)

        # Dashboard visual center layouts (Graph + Recent table)
        bottom_frame = customtkinter.CTkFrame(view, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(20, 0))
        bottom_frame.grid_columnconfigure(0, weight=6) # Graph Canvas
        bottom_frame.grid_columnconfigure(1, weight=5) # Logs Table

        # Matplotlib Graph Container Card
        self.graph_card = customtkinter.CTkFrame(bottom_frame, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color="#1E293B")
        self.graph_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.graph_title_lbl = customtkinter.CTkLabel(
            self.graph_card, text="Average Risk Assessment Trends", font=("Segoe UI", 15, "bold"), text_color=TEXT_COLOR
        )
        self.graph_title_lbl.pack(pady=10, anchor="w", padx=15)

        self.plot_figure = plt.figure(figsize=(5, 3.5), facecolor=CARD_COLOR)
        self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, master=self.graph_card)
        self.plot_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Recent Logs Container Card
        logs_card = customtkinter.CTkFrame(bottom_frame, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color="#1E293B")
        logs_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.recent_lbl = customtkinter.CTkLabel(
            logs_card, text="Recent Security Scans", font=("Segoe UI", 15, "bold"), text_color=TEXT_COLOR
        )
        self.recent_lbl.pack(pady=10, anchor="w", padx=15)

        self.dash_log_container = customtkinter.CTkScrollableFrame(logs_card, fg_color="transparent")
        self.dash_log_container.pack(fill="both", expand=True, padx=10, pady=5)

        return view

    def draw_metric_card(self, parent, label_text, initial_value, column_idx, accent_clr):
        card = customtkinter.CTkFrame(parent, fg_color=CARD_COLOR, height=95, corner_radius=10, border_width=1, border_color="#1E293B")
        card.grid(row=1, column=column_idx, sticky="ew", padx=5)
        card.grid_propagate(False)

        accent_bar = customtkinter.CTkFrame(card, width=4, fg_color=accent_clr, corner_radius=2)
        accent_bar.pack(side="left", fill="y", padx=(0, 12))

        val_label = customtkinter.CTkLabel(card, text=initial_value, font=("Segoe UI", 28, "bold"), text_color=TEXT_COLOR)
        val_label.pack(anchor="w", padx=(0, 10), pady=(10, 0))

        lbl_label = customtkinter.CTkLabel(card, text=label_text, font=("Segoe UI", 12), text_color=TEXT_MUTED)
        lbl_label.pack(anchor="w", padx=(0, 10))

        # Store labels reference so values update dynamically later
        card.value_label = val_label
        card.title_label = lbl_label
        return card

    def refresh_dashboard_metrics(self):
        stats = self.db.get_stats()
        self.card_total.value_label.configure(text=str(stats["total"]))
        self.card_clean.value_label.configure(text=str(stats["safe"]))
        self.card_warn.value_label.configure(text=str(stats["warning"]))
        self.card_threat.value_label.configure(text=str(stats["dangerous"]))

        # Redraw Matplotlib trend chart
        self.draw_matplotlib_trend()

        # Refresh recent scanned items list
        for widget in self.dash_log_container.winfo_children():
            widget.destroy()

        recents = self.db.get_recent_scans(limit=5)
        if not recents:
            empty_lbl = customtkinter.CTkLabel(
                self.dash_log_container, text=LANGUAGES[self.current_language]["lbl_no_history"],
                text_color=TEXT_MUTED, font=("Segoe UI", 13)
            )
            empty_lbl.pack(pady=30)
            return

        for scan in recents:
            row_frame = customtkinter.CTkFrame(self.dash_log_container, fg_color="#1E293B", height=45, corner_radius=6)
            row_frame.pack(fill="x", pady=4, ipady=3)

            color_badge = SUCCESS_COLOR if scan["result_status"] == "SAFE" else (WARNING_COLOR if scan["result_status"] == "WARNING" else DANGER_COLOR)
            badge = customtkinter.CTkFrame(row_frame, width=8, height=8, corner_radius=4, fg_color=color_badge)
            badge.pack(side="left", padx=12)

            # Limit URL text length to fit
            clean_url = scan["url"][:42] + "..." if len(scan["url"]) > 45 else scan["url"]
            url_lbl = customtkinter.CTkLabel(row_frame, text=clean_url, font=("Segoe UI", 13, "bold"), text_color=TEXT_COLOR, anchor="w")
            url_lbl.pack(side="left", padx=5)

            score_lbl = customtkinter.CTkLabel(row_frame, text=f"Score: {scan['risk_score']}", font=("Segoe UI", 12), text_color=TEXT_MUTED)
            score_lbl.pack(side="right", padx=15)

            # Quick inspect event triggers
            row_frame.bind("<Button-1>", lambda event, r=scan["details"]: self.load_result_to_inspect(r))
            url_lbl.bind("<Button-1>", lambda event, r=scan["details"]: self.load_result_to_inspect(r))

    def draw_matplotlib_trend(self):
        self.plot_figure.clear()
        
        # Get historical data points
        history = self.db.get_history()[:7]
        history.reverse() # Chronological

        ax = self.plot_figure.add_subplot(111)
        ax.set_facecolor(CARD_COLOR)
        
        # Style layout colors matching theme
        ax.spines['bottom'].set_color('#2B3654')
        ax.spines['top'].set_color('#2B3654')
        ax.spines['right'].set_color('#2B3654')
        ax.spines['left'].set_color('#2B3654')
        ax.tick_params(axis='x', colors='#8A99AD', labelsize=8)
        ax.tick_params(axis='y', colors='#8A99AD', labelsize=8)
        ax.grid(True, color="#1E293B", linestyle="--")

        if len(history) < 2:
            # Fallback mock visualization showing empty states
            x_vals = [f"Scan {i+1}" for i in range(5)]
            y_vals = [100, 95, 100, 98, 100]
            ax.plot(x_vals, y_vals, marker='o', color=ACCENT_COLOR, linewidth=2)
            ax.set_ylim(0, 110)
        else:
            x_vals = []
            y_vals = []
            for idx, item in enumerate(history):
                short_url = item["url"].replace("https://", "").replace("http://", "")[:12] + "..." if len(item["url"]) > 15 else item["url"]
                x_vals.append(f"{idx+1}. {short_url}")
                y_vals.append(item["risk_score"])
            
            # Line coloring transitions based on average score
            line_color = SUCCESS_COLOR if sum(y_vals)/len(y_vals) >= 80 else (WARNING_COLOR if sum(y_vals)/len(y_vals) >= 50 else DANGER_COLOR)
            ax.plot(x_vals, y_vals, marker='s', color=line_color, linewidth=2.5, label="Risk Score")
            ax.set_ylim(0, 110)
            plt.xticks(rotation=15, ha='right')

        self.plot_figure.tight_layout()
        self.plot_canvas.draw()

    # 2. VIEW: QUICK SCAN PANEL
    def create_quick_scan_view(self):
        view = customtkinter.CTkFrame(self.main_viewport, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(0, weight=0) # Search bar
        view.grid_rowconfigure(1, weight=1) # Interactive results viewport

        # Entry URL scanning row
        search_card = customtkinter.CTkFrame(view, fg_color=CARD_COLOR, height=75, corner_radius=12, border_width=1, border_color="#1E293B")
        search_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        search_card.grid_propagate(False)

        self.url_input = customtkinter.CTkEntry(
            search_card, placeholder_text="Enter URL to scan securely...",
            font=("Segoe UI", 14), fg_color="#0F172A", border_color="#2B3654", text_color="#FFFFFF"
        )
        self.url_input.pack(side="left", fill="x", expand=True, padx=(20, 10), pady=15)
        self.url_input.bind("<Return>", lambda event: self.trigger_live_scan())

        self.btn_paste = customtkinter.CTkButton(
            search_card, text="Paste", width=75, font=("Segoe UI", 12),
            fg_color="#1E293B", text_color=ACCENT_COLOR, hover_color="#334155",
            command=self.paste_from_clipboard
        )
        self.btn_paste.pack(side="left", padx=5, pady=15)

        self.btn_qr_upload = customtkinter.CTkButton(
            search_card, text="Scan QR", width=85, font=("Segoe UI", 12),
            fg_color="#1E293B", text_color=ACCENT_COLOR, hover_color="#334155",
            command=self.upload_and_decode_qr
        )
        self.btn_qr_upload.pack(side="left", padx=5, pady=15)

        self.btn_scan = customtkinter.CTkButton(
            search_card, text="Scan Link", font=("Segoe UI", 14, "bold"),
            fg_color=ACCENT_COLOR, text_color="#0B1220", hover_color="#00B8D4",
            command=self.trigger_live_scan
        )
        self.btn_scan.pack(side="left", padx=(5, 20), pady=15)

        # Dynamic Content (Initially empty scan guidance, afterwards populated tabs)
        self.results_viewport = customtkinter.CTkFrame(view, fg_color="transparent")
        self.results_viewport.grid(row=1, column=0, sticky="nsew")
        self.results_viewport.grid_columnconfigure(0, weight=1)
        self.results_viewport.grid_rowconfigure(0, weight=1)

        self.empty_results_frame = customtkinter.CTkFrame(self.results_viewport, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color="#1E293B")
        self.empty_results_frame.grid(row=0, column=0, sticky="nsew")

        # Visual upload helper elements
        self.drop_icon = customtkinter.CTkLabel(self.empty_results_frame, text="🛡️", font=("Segoe UI", 82))
        self.drop_icon.pack(expand=True, pady=(80, 0))

        self.drop_label = customtkinter.CTkLabel(
            self.empty_results_frame, text="Click to browse TXT / QR codes, or type URL above to begin active scanning",
            font=("Segoe UI", 16, "bold"), text_color=TEXT_COLOR
        )
        self.drop_label.pack(expand=True, pady=(0, 5))

        self.btn_select_file = customtkinter.CTkButton(
            self.empty_results_frame, text="Browse Files", font=("Segoe UI", 13),
            fg_color="#1E293B", text_color=ACCENT_COLOR, hover_color="#334155",
            command=self.browse_and_load_file
        )
        self.btn_select_file.pack(expand=True, pady=(0, 80))

        # Main dynamic results HUD panel
        self.scan_hud_frame = customtkinter.CTkFrame(self.results_viewport, fg_color="transparent")
        self.scan_hud_frame.grid_columnconfigure(0, weight=4) # Gauge
        self.scan_hud_frame.grid_columnconfigure(1, weight=7) # Detailed Tabs
        self.scan_hud_frame.grid_rowconfigure(0, weight=1)

        # LEFT SIDE OF HUD: GAUGE
        left_hud = customtkinter.CTkFrame(self.scan_hud_frame, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color="#1E293B")
        left_hud.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_hud.grid_columnconfigure(0, weight=1)
        left_hud.grid_rowconfigure(0, weight=0) # title
        left_hud.grid_rowconfigure(1, weight=1) # Gauge widget
        left_hud.grid_rowconfigure(2, weight=0) # Button

        self.gauge_lbl = customtkinter.CTkLabel(left_hud, text="Risk Gauge", font=("Segoe UI", 16, "bold"), text_color=TEXT_COLOR)
        self.gauge_lbl.grid(row=0, column=0, pady=15)

        self.gauge_canvas = ThreatGauge(left_hud)
        self.gauge_canvas.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Reporting Action Panel
        action_panel = customtkinter.CTkFrame(left_hud, fg_color="transparent")
        action_panel.grid(row=2, column=0, pady=20)

        self.btn_pdf_report = customtkinter.CTkButton(
            action_panel, text="Export PDF Report", fg_color=ACCENT_COLOR, text_color="#0B1220",
            font=("Segoe UI", 13, "bold"), hover_color="#00B8D4", command=self.export_pdf_report
        )
        self.btn_pdf_report.pack(side="left", padx=5)

        # RIGHT SIDE OF HUD: TAB PANEL
        self.hud_tabs = customtkinter.CTkTabview(
            self.scan_hud_frame, fg_color=CARD_COLOR, segmented_button_selected_color=CARD_COLOR,
            segmented_button_selected_hover_color="#1E293B", segmented_button_unselected_color="#0F172A",
            text_color=ACCENT_COLOR
        )
        self.hud_tabs.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Create standard tabs
        self.tab_sum = self.hud_tabs.add("Summary")
        self.tab_dom = self.hud_tabs.add("Domain Info")
        self.tab_cert = self.hud_tabs.add("SSL Cert")
        self.tab_loc = self.hud_tabs.add("Server Location")
        self.tab_trace = self.hud_tabs.add("Redirect Trace")
        self.tab_raw = self.hud_tabs.add("Raw WHOIS")

        self.setup_hud_tab_elements()

        return view

    def setup_hud_tab_elements(self):
        # 1. SUMMARY TAB
        self.tab_sum.grid_columnconfigure(0, weight=1)
        self.tab_sum.grid_rowconfigure(0, weight=0) # link details
        self.tab_sum.grid_rowconfigure(1, weight=1) # threats list

        self.sum_link_lbl = customtkinter.CTkLabel(self.tab_sum, text="Scanned URL:", font=("Segoe UI", 14, "bold"), text_color=TEXT_COLOR, anchor="w")
        self.sum_link_lbl.grid(row=0, column=0, sticky="ew", padx=15, pady=10)

        self.sum_threat_container = customtkinter.CTkScrollableFrame(self.tab_sum, fg_color="#0F172A")
        self.sum_threat_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        # 2. DOMAIN INFO TAB
        self.tab_dom.grid_columnconfigure(0, weight=1)
        self.tab_dom.grid_rowconfigure(0, weight=1) # meta grid
        self.tab_dom.grid_rowconfigure(1, weight=1) # DNS records list

        self.dom_meta_container = customtkinter.CTkFrame(self.tab_dom, fg_color="transparent")
        self.dom_meta_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)
        self.dom_meta_container.grid_columnconfigure((0, 1), weight=1)

        self.dns_records_box = customtkinter.CTkTextbox(self.tab_dom, fg_color="#0F172A", font=("Consolas", 12))
        self.dns_records_box.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        # 3. SSL CERT TAB
        self.tab_cert.grid_columnconfigure(0, weight=1)
        self.tab_cert.grid_rowconfigure(0, weight=1)
        self.ssl_cert_box = customtkinter.CTkTextbox(self.tab_cert, fg_color="#0F172A", font=("Consolas", 12))
        self.ssl_cert_box.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        # 4. SERVER GEOLOCATION TAB
        self.tab_loc.grid_columnconfigure(0, weight=1)
        self.tab_loc.grid_rowconfigure(0, weight=2) # Info labels
        self.tab_loc.grid_rowconfigure(1, weight=3) # Embedded Map

        self.geo_info_container = customtkinter.CTkFrame(self.tab_loc, fg_color="transparent")
        self.geo_info_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)
        self.geo_info_container.grid_columnconfigure((0, 1), weight=1)

        # Map initialization
        self.map_view = tkintermapview.TkinterMapView(self.tab_loc, corner_radius=8)
        self.map_view.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.map_view.set_zoom(4)

        # 5. REDIRECT TRACE TAB
        self.tab_trace.grid_columnconfigure(0, weight=1)
        self.tab_trace.grid_rowconfigure(0, weight=1)
        self.redirect_trace_container = customtkinter.CTkScrollableFrame(self.tab_trace, fg_color="#0F172A")
        self.redirect_trace_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        # 6. RAW WHOIS TAB
        self.tab_raw.grid_columnconfigure(0, weight=1)
        self.tab_raw.grid_rowconfigure(0, weight=1)
        self.whois_box = customtkinter.CTkTextbox(self.tab_raw, fg_color="#0F172A", font=("Consolas", 12))
        self.whois_box.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

    def paste_from_clipboard(self):
        try:
            pasted = self.clipboard_get()
            self.url_input.delete(0, tk.END)
            self.url_input.insert(0, pasted)
        except Exception:
            pass

    def browse_and_load_file(self):
        file_path = filedialog.askopenfilename(
            title="Open Scannable File",
            filetypes=[("Text Documents / QR Images", "*.txt;*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".png", ".jpg", ".jpeg"):
            self.decode_qr_image(file_path)
        else:
            self.load_txt_file_urls(file_path)

    def decode_qr_image(self, file_path):
        self.status_lbl.configure(text="Decoding QR code image...", text_color=WARNING_COLOR)
        # Attempt to decode via OpenCV/pyzbar fallbacks
        decoded_url = None
        
        # Primary check: OpenCV Builtin detector
        try:
            img = cv2.imread(file_path)
            if img is not None:
                detector = cv2.QRCodeDetector()
                val, pts, straight = detector.detectAndDecode(img)
                if val:
                    decoded_url = val
        except Exception as e:
            logging.error(f"OpenCV QR decode failed: {e}")

        # Secondary check: Pyzbar decoder
        if not decoded_url and PYZBAR_AVAILABLE:
            try:
                from PIL import Image as PILImage
                decoded_objs = pyzbar.decode(PILImage.open(file_path))
                if decoded_objs:
                    decoded_url = decoded_objs[0].data.decode("utf-8")
            except Exception as e:
                logging.error(f"Pyzbar QR decode failed: {e}")

        if decoded_url:
            self.url_input.delete(0, tk.END)
            self.url_input.insert(0, decoded_url)
            self.status_lbl.configure(text="QR code decoded successfully.", text_color=SUCCESS_COLOR)
            self.trigger_live_scan()
        else:
            self.status_lbl.configure(text="No QR code payload detected in image.", text_color=DANGER_COLOR)
            messagebox.showerror("QR Decode Error", "Could not locate or extract a valid URL from the uploaded image.")

    def load_txt_file_urls(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            if lines:
                # Set the first valid url to search path
                self.url_input.delete(0, tk.END)
                self.url_input.insert(0, lines[0])
                self.status_lbl.configure(text=f"Imported {len(lines)} URLs. Loading target URL...", text_color=SUCCESS_COLOR)
                self.trigger_live_scan()
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to load text file: {e}")

    def upload_and_decode_qr(self):
        file_path = filedialog.askopenfilename(
            title="Select QR Code Image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp"), ("All Files", "*.*")]
        )
        if file_path:
            self.decode_qr_image(file_path)

    # =====================================================================
    # LIVE SYSTEM SCANNING CONTROLLER
    # =====================================================================
    def trigger_live_scan(self):
        target = self.url_input.get().strip()
        if not target:
            return

        # Prepare UI components
        self.status_lbl.configure(text="System starting scan execution...", text_color=WARNING_COLOR)
        self.status_progress.set(0.05)
        self.btn_scan.configure(state="disabled")

        # Hide old HUD cards and show loading state
        self.empty_results_frame.grid_forget()
        self.scan_hud_frame.grid_forget()

        # Start thread execution to prevent GUI blocking
        worker = ScanWorkerThread(target, self.worker_queue, self.push_worker_progress)
        worker.start()

        # Register poller event loop checks
        self.after(100, self.poll_worker_results)

    def push_worker_progress(self, message, percentage):
        # Direct callback wrapper executed from background thread safely
        self.after(0, lambda: self.update_scan_progress_ui(message, percentage))

    def update_scan_progress_ui(self, message, percentage):
        self.status_lbl.configure(text=message, text_color=WARNING_COLOR)
        self.status_progress.set(percentage / 100.0)

    def poll_worker_results(self):
        try:
            # Check queue status non-blocking
            status, payload = self.worker_queue.get_nowait()
            self.btn_scan.configure(state="normal")
            self.status_progress.set(1.0)

            if status == "SUCCESS":
                self.status_lbl.configure(text="URL safety scan completed.", text_color=SUCCESS_COLOR)
                self.latest_result = payload
                self.load_result_to_inspect(payload)
                
                # Check Auto-Save SQL config
                if self.autosave_enabled:
                    self.db.save_scan(payload["url"], payload["risk_score"], payload["result_status"], payload)
                    self.refresh_dashboard_metrics()
            else:
                self.status_lbl.configure(text=f"Scan error: {payload}", text_color=DANGER_COLOR)
                messagebox.showerror("LinkScan Failure", f"An error occurred during URL safety scan:\n{payload}")
                self.empty_results_frame.grid(row=0, column=0, sticky="nsew")
        except queue.Empty:
            # Re-schedule poller cycle
            self.after(100, self.poll_worker_results)

    def load_result_to_inspect(self, result):
        self.latest_result = result
        self.empty_results_frame.grid_forget()
        self.scan_hud_frame.grid(row=0, column=0, sticky="nsew")
        self.switch_view("quick_scan")

        # Update Gauge needle
        self.gauge_canvas.set_score(result["risk_score"])

        # Populate HUD panels
        self.populate_summary_tab(result)
        self.populate_domain_tab(result)
        self.populate_ssl_tab(result)
        self.populate_geo_tab(result)
        self.populate_redirects_tab(result)
        self.populate_whois_tab(result)

    # HUD PANEL INJECTORS
    def populate_summary_tab(self, result):
        # Update url label
        short_url = result["final_url"][:60] + "..." if len(result["final_url"]) > 63 else result["final_url"]
        self.sum_link_lbl.configure(text=f"Scanned Target Final URL:\n{short_url}")

        # Clear old items
        for widget in self.sum_threat_container.winfo_children():
            widget.destroy()

        if not result["reasons"]:
            # URL IS CLEAN
            safe_frame = customtkinter.CTkFrame(self.sum_threat_container, fg_color="#1E293B", corner_radius=6)
            safe_frame.pack(fill="x", pady=5, padx=5)
            lbl = customtkinter.CTkLabel(
                safe_frame, text="✅  No major structural threats or visual spoofing issues detected.",
                font=("Segoe UI", 13, "bold"), text_color=SUCCESS_COLOR, wraplength=450
            )
            lbl.pack(pady=15, padx=15)
        else:
            for reason in result["reasons"]:
                item_frame = customtkinter.CTkFrame(self.sum_threat_container, fg_color="#1E293B", corner_radius=6)
                item_frame.pack(fill="x", pady=4, padx=5)

                lbl_rule = customtkinter.CTkLabel(
                    item_frame, text=f"⚠️  {reason['rule']}  [-{reason['deduction']} pts]",
                    font=("Segoe UI", 13, "bold"), text_color=DANGER_COLOR, anchor="w"
                )
                lbl_rule.pack(fill="x", padx=12, pady=(8, 2))

                lbl_desc = customtkinter.CTkLabel(
                    item_frame, text=reason["description"], font=("Segoe UI", 12),
                    text_color=TEXT_MUTED, wraplength=480, justify="left", anchor="w"
                )
                lbl_desc.pack(fill="x", padx=12, pady=(0, 8))

    def populate_domain_tab(self, result):
        # Clean subgrid
        for widget in self.dom_meta_container.winfo_children():
            widget.destroy()

        metadata = [
            ("Registrar:", result["whois"].get("registrar", "Unknown")),
            ("Domain Age:", result["whois"].get("domain_age_days", "Unknown")),
            ("Creation Date:", result["whois"].get("creation_date", "Unknown")),
            ("Expiration Date:", result["whois"].get("expiration_date", "Unknown")),
            ("Update Date:", result["whois"].get("updated_date", "Unknown")),
            ("Name Servers:", result["whois"].get("name_servers", "Unknown")[:45] + "..." if len(result["whois"].get("name_servers", "Unknown")) > 45 else result["whois"].get("name_servers", "Unknown"))
        ]

        for i, (k, v) in enumerate(metadata):
            lbl_k = customtkinter.CTkLabel(self.dom_meta_container, text=k, font=("Segoe UI", 13, "bold"), text_color=TEXT_MUTED, anchor="w")
            lbl_k.grid(row=i, column=0, padx=10, pady=4, sticky="w")
            lbl_v = customtkinter.CTkLabel(self.dom_meta_container, text=str(v), font=("Segoe UI", 13), text_color=TEXT_COLOR, anchor="w")
            lbl_v.grid(row=i, column=1, padx=10, pady=4, sticky="w")

        # DNS entries table formatting
        dns_str = "=====================================================\n"
        dns_str += "                    DNS RECORDS                      \n"
        dns_str += "=====================================================\n"
        for qtype, records in result["dns_records"].items():
            if records:
                dns_str += f"\n[{qtype} Records]:\n"
                for r in records:
                    dns_str += f"  > {r}\n"
            else:
                dns_str += f"\n[{qtype} Records]: None Resolved\n"

        self.dns_records_box.configure(state="normal")
        self.dns_records_box.delete("1.0", tk.END)
        self.dns_records_box.insert("1.0", dns_str)
        self.dns_records_box.configure(state="disabled")

    def populate_ssl_tab(self, result):
        ssl_info = result["ssl_analysis"]
        ssl_str = "=====================================================\n"
        ssl_str += "             SSL / TLS CERTIFICATE REPORT            \n"
        ssl_str += "=====================================================\n\n"
        
        if ssl_info["has_cert"]:
            ssl_str += f"Trust Verification: {'TRUSTED/VALID' if ssl_info['valid'] else 'INVALID/UNTRUSTED'}\n"
            ssl_str += f"Issuer:             {ssl_info['issuer']}\n"
            ssl_str += f"Expiration Date:    {ssl_info['expiry']}\n"
            ssl_str += f"TLS Cipher Suite:   {ssl_info['cipher']}\n"
            ssl_str += f"TLS Version:        {ssl_info['version']}\n"
            if not ssl_info["valid"]:
                ssl_str += f"\n[Security Alert]:   {ssl_info['error']}\n"
        else:
            ssl_str += "No SSL/TLS Certificate was resolved on remote port 443.\n"
            ssl_str += f"Diagnosis Detail:   {ssl_info['error']}\n"

        self.ssl_cert_box.configure(state="normal")
        self.ssl_cert_box.delete("1.0", tk.END)
        self.ssl_cert_box.insert("1.0", ssl_str)
        self.ssl_cert_box.configure(state="disabled")

    def populate_geo_tab(self, result):
        geo = result["geo_data"]
        
        # Clean subgrid
        for widget in self.geo_info_container.winfo_children():
            widget.destroy()

        geo_meta = [
            ("IP Endpoint:", geo.get("ip", "Unknown")),
            ("Country Name:", geo.get("country", "Unknown")),
            ("City / Region:", geo.get("city", "Unknown")),
            ("Hosting ISP:", geo.get("isp", "Unknown")),
            ("ASN Network:", geo.get("asn", "Unknown")),
            ("Coordinates:", f"Lat: {geo.get('latitude', 0.0)}, Lon: {geo.get('longitude', 0.0)}")
        ]

        for i, (k, v) in enumerate(geo_meta):
            lbl_k = customtkinter.CTkLabel(self.geo_info_container, text=k, font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED, anchor="w")
            lbl_k.grid(row=i, column=0, padx=10, pady=2, sticky="w")
            lbl_v = customtkinter.CTkLabel(self.geo_info_container, text=str(v), font=("Segoe UI", 12), text_color=TEXT_COLOR, anchor="w")
            lbl_v.grid(row=i, column=1, padx=10, pady=2, sticky="w")

        # Position marker coordinates on map widget
        lat = geo.get("latitude", 37.0902)
        lon = geo.get("longitude", -95.7129)
        self.map_view.set_position(lat, lon)
        self.map_view.set_marker(lat, lon, text=geo.get("isp", "Server Host"))

    def populate_redirects_tab(self, result):
        for widget in self.redirect_trace_container.winfo_children():
            widget.destroy()

        chain = result["redirect_chain"]
        if not chain:
            empty_lbl = customtkinter.CTkLabel(self.redirect_trace_container, text="No redirects triggered.", text_color=TEXT_MUTED)
            empty_lbl.pack(pady=20)
            return

        for i, hop in enumerate(chain):
            hop_frame = customtkinter.CTkFrame(self.redirect_trace_container, fg_color="#1E293B", corner_radius=6)
            hop_frame.pack(fill="x", pady=4, padx=5)

            status_clr = SUCCESS_COLOR if hop.get("status_code", 0) in (200, 204) else WARNING_COLOR
            lbl_hop = customtkinter.CTkLabel(
                hop_frame, text=f"HOP {hop['hop']}: Status {hop.get('status_code', 'ERR')}",
                font=("Segoe UI", 13, "bold"), text_color=status_clr, anchor="w"
            )
            lbl_hop.pack(fill="x", padx=12, pady=(6, 2))

            short_url = hop["url"][:60] + "..." if len(hop["url"]) > 63 else hop["url"]
            lbl_url = customtkinter.CTkLabel(
                hop_frame, text=short_url, font=("Segoe UI", 12),
                text_color=TEXT_COLOR, anchor="w", justify="left"
            )
            lbl_url.pack(fill="x", padx=12, pady=(0, 6))

            # Draw directional link arrow unless final node
            if i < len(chain) - 1:
                arrow = customtkinter.CTkLabel(self.redirect_trace_container, text="▼", font=("Segoe UI", 14), text_color=ACCENT_COLOR)
                arrow.pack(pady=2)

    def populate_whois_tab(self, result):
        self.whois_box.configure(state="normal")
        self.whois_box.delete("1.0", tk.END)
        self.whois_box.insert("1.0", result.get("whois_raw", "WHOIS record not extracted."))
        self.whois_box.configure(state="disabled")

    # =====================================================================
    # VIEW: SCAN HISTORY PANEL
    # =====================================================================
    def create_scan_history_view(self):
        view = customtkinter.CTkFrame(self.main_viewport, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(0, weight=0) # Controls
        view.grid_rowconfigure(1, weight=1) # Logs Table

        controls_card = customtkinter.CTkFrame(view, fg_color=CARD_COLOR, height=70, corner_radius=12, border_width=1, border_color="#1E293B")
        controls_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        controls_card.grid_propagate(False)

        self.hist_search_entry = customtkinter.CTkEntry(
            controls_card, placeholder_text="Search URLs in history...",
            width=280, fg_color="#0F172A", border_color="#2B3654"
        )
        self.hist_search_entry.pack(side="left", padx=15, pady=18)
        self.hist_search_entry.bind("<KeyRelease>", lambda event: self.refresh_history_table())

        self.hist_filter = customtkinter.CTkComboBox(
            controls_card, values=["All Records", "Today Only", "This Week", "Threats Only", "Clean Only"],
            command=lambda v: self.refresh_history_table()
        )
        self.hist_filter.pack(side="left", padx=10, pady=18)
        self.hist_filter.set("All Records")

        self.btn_del_log = customtkinter.CTkButton(
            controls_card, text="Delete Record", fg_color="#1E293B", text_color=DANGER_COLOR,
            hover_color="#334155", font=("Segoe UI", 12, "bold"), command=self.delete_history_row
        )
        self.btn_del_log.pack(side="right", padx=15, pady=18)

        self.btn_clear_all_logs = customtkinter.CTkButton(
            controls_card, text="Wipe History", fg_color="#1E293B", text_color=DANGER_COLOR,
            hover_color="#334155", font=("Segoe UI", 12, "bold"), command=self.clear_all_history_data
        )
        self.btn_clear_all_logs.pack(side="right", padx=5, pady=18)

        # Style standard ttk Treeview container for logs listing
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD_COLOR, fieldbackground=CARD_COLOR, foreground="#FFFFFF",
                        rowheight=35, font=("Segoe UI", 11), borderwidth=0)
        style.configure("Treeview.Heading", background="#0F172A", foreground=ACCENT_COLOR,
                        font=("Segoe UI", 12, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", "#1E293B")], foreground=[("selected", ACCENT_COLOR)])

        tree_frame = customtkinter.CTkFrame(view, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color="#1E293B")
        tree_frame.grid(row=1, column=0, sticky="nsew")

        self.history_tree = ttk.Treeview(tree_frame, columns=("id", "timestamp", "url", "score", "status"), show="headings")
        self.history_tree.pack(fill="both", expand=True, padx=15, pady=15)

        self.history_tree.heading("id", text="ID")
        self.history_tree.heading("timestamp", text="Timestamp")
        self.history_tree.heading("url", text="Scanned URL Address")
        self.history_tree.heading("score", text="Risk Score")
        self.history_tree.heading("status", text="Threat Status")

        self.history_tree.column("id", width=50, minwidth=40, anchor="center")
        self.history_tree.column("timestamp", width=180, minwidth=150, anchor="center")
        self.history_tree.column("url", width=550, minwidth=400, anchor="w")
        self.history_tree.column("score", width=90, minwidth=70, anchor="center")
        self.history_tree.column("status", width=120, minwidth=100, anchor="center")

        # Double click inspect event
        self.history_tree.bind("<Double-1>", self.on_history_row_double_click)

        return view

    def refresh_history_table(self):
        # Clear items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        search = self.hist_search_entry.get().strip()
        filt = self.hist_filter.get()

        records = self.db.get_history(search_query=search, filter_type=filt)
        for r in records:
            self.history_tree.insert(
                "", tk.END, values=(r["id"], r["timestamp"], r["url"], r["risk_score"], r["result_status"]),
                tags=(r["id"],)
            )

    def delete_history_row(self):
        selection = self.history_tree.selection()
        if not selection:
            return
        row_id = self.history_tree.item(selection[0])["values"][0]
        self.db.delete_scan(row_id)
        self.refresh_history_table()
        self.refresh_dashboard_metrics()

    def clear_all_history_data(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to permanently delete all scan records from history?"):
            self.db.clear_history()
            self.refresh_history_table()
            self.refresh_dashboard_metrics()

    def on_history_row_double_click(self, event):
        selection = self.history_tree.selection()
        if not selection:
            return
        row_id = self.history_tree.item(selection[0])["values"][0]
        
        # Load from SQL cache and display details on Scan HUD
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT details_json FROM scan_history WHERE id = ?", (row_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            details = json.loads(row[0])
            self.load_result_to_inspect(details)

    def trigger_global_search(self, event):
        query = self.search_val.get().strip()
        if query:
            self.switch_view("scan_history")
            self.hist_search_entry.delete(0, tk.END)
            self.hist_search_entry.insert(0, query)
            self.refresh_history_table()

    # =====================================================================
    # VIEW: REPORTS PORTAL VIEW
    # =====================================================================
    def create_reports_view(self):
        view = customtkinter.CTkFrame(self.main_viewport, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(0, weight=1)

        card = customtkinter.CTkFrame(view, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color="#1E293B")
        card.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        card.grid_columnconfigure(0, weight=1)

        lbl = customtkinter.CTkLabel(card, text="Reports Portal", font=("Segoe UI", 22, "bold"), text_color=TEXT_COLOR)
        lbl.pack(pady=(30, 20))

        # Folder selection widgets
        path_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        path_frame.pack(fill="x", padx=40, pady=10)

        self.lbl_exp_path = customtkinter.CTkLabel(path_frame, text=f"Export Directory: {self.export_path}", text_color=TEXT_MUTED, font=("Segoe UI", 13))
        self.lbl_exp_path.pack(side="left", padx=10)

        btn_ch_dir = customtkinter.CTkButton(
            path_frame, text="Change Folder", font=("Segoe UI", 12), fg_color="#1E293B", text_color=ACCENT_COLOR,
            command=self.change_export_directory
        )
        btn_ch_dir.pack(side="right", padx=10)

        # Selection checkboxes for formats
        formats_frame = customtkinter.CTkFrame(card, fg_color="#0F172A", height=110, corner_radius=8)
        formats_frame.pack(fill="x", padx=50, pady=25)
        
        self.rep_pdf_val = tk.BooleanVar(value=True)
        self.rep_csv_val = tk.BooleanVar(value=False)
        self.rep_json_val = tk.BooleanVar(value=False)
        self.rep_html_val = tk.BooleanVar(value=False)

        customtkinter.CTkCheckBox(formats_frame, text="Adobe PDF Document", variable=self.rep_pdf_val, text_color=TEXT_COLOR, fg_color=ACCENT_COLOR).pack(side="left", expand=True, padx=10, pady=15)
        customtkinter.CTkCheckBox(formats_frame, text="CSV Data Sheet", variable=self.rep_csv_val, text_color=TEXT_COLOR, fg_color=ACCENT_COLOR).pack(side="left", expand=True, padx=10, pady=15)
        customtkinter.CTkCheckBox(formats_frame, text="JSON Dump", variable=self.rep_json_val, text_color=TEXT_COLOR, fg_color=ACCENT_COLOR).pack(side="left", expand=True, padx=10, pady=15)
        customtkinter.CTkCheckBox(formats_frame, text="HTML Report Webpage", variable=self.rep_html_val, text_color=TEXT_COLOR, fg_color=ACCENT_COLOR).pack(side="left", expand=True, padx=10, pady=15)

        btn_export = customtkinter.CTkButton(
            card, text="Generate & Export Reports for Latest Scan", font=("Segoe UI", 15, "bold"),
            fg_color=ACCENT_COLOR, text_color="#0B1220", hover_color="#00B8D4", height=45,
            command=self.export_all_latest_reports
        )
        btn_export.pack(pady=20)

        return view

    def change_export_directory(self):
        path = filedialog.askdirectory(title="Select Reports Export Folder")
        if path:
            self.export_path = path
            self.lbl_exp_path.configure(text=f"Export Directory: {self.export_path}")

    def export_all_latest_reports(self):
        if not self.latest_result:
            messagebox.showwarning("No Data", "Please scan a URL first before generating reports.")
            return

        exported = []
        # Compile selected reports
        if self.rep_pdf_val.get():
            pdf_path = self.export_pdf_report()
            if pdf_path:
                exported.append(f"PDF: {pdf_path}")
        if self.rep_csv_val.get():
            csv_path = self.export_csv_report()
            if csv_path:
                exported.append(f"CSV: {csv_path}")
        if self.rep_json_val.get():
            json_path = self.export_json_report()
            if json_path:
                exported.append(f"JSON: {json_path}")
        if self.rep_html_val.get():
            html_path = self.export_html_report()
            if html_path:
                exported.append(f"HTML: {html_path}")

        if exported:
            messagebox.showinfo("Export Successful", "Generated reports saved successfully:\n" + "\n".join(exported))

    # PDF EXPORT SCRIPT
    def export_pdf_report(self):
        if not self.latest_result:
            messagebox.showwarning("No Data", "Scan a URL first before exporting.")
            return None

        # Determine filename
        filename = f"LinkShield_Report_{int(time.time())}.pdf"
        target_file = os.path.join(self.export_path, filename)

        try:
            doc = SimpleDocTemplate(target_file, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styled Paragraph types
            title_style = ParagraphStyle(
                'TitleStyle', parent=styles['Heading1'],
                textColor=colors.HexColor(ACCENT_COLOR), fontSize=24, spaceAfter=20
            )
            h2_style = ParagraphStyle(
                'H2Style', parent=styles['Heading2'],
                textColor=colors.HexColor(CARD_COLOR), fontSize=14, spaceBefore=10, spaceAfter=8
            )
            body_style = ParagraphStyle(
                'BodyStyle', parent=styles['Normal'],
                textColor=colors.black, fontSize=11, spaceBefore=4, spaceAfter=4
            )
            
            story = []
            # Header
            story.append(Paragraph("🛡️ LinkShield AI Threat Assessment", title_style))
            story.append(Spacer(1, 10))

            # Core metadata
            meta_data = [
                ["Target Scan URL:", self.latest_result["url"]],
                ["Final Destination URL:", self.latest_result["final_url"]],
                ["Risk Score Heuristics:", f"{self.latest_result['risk_score']} / 100"],
                ["Threat Classification:", self.latest_result["result_status"]],
                ["Scan Date / Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]
            t_meta = Table(meta_data, colWidths=[150, 350])
            t_meta.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_meta)
            story.append(Spacer(1, 20))

            # Threat issues list
            story.append(Paragraph("Identified Threat Markers", h2_style))
            if not self.latest_result["reasons"]:
                story.append(Paragraph("No security threats detected during active scan.", body_style))
            else:
                for idx, r in enumerate(self.latest_result["reasons"]):
                    story.append(Paragraph(f"<b>{idx+1}. {r['rule']} (Deducted: {r['deduction']} points)</b>", body_style))
                    story.append(Paragraph(r['description'], body_style))
                    story.append(Spacer(1, 8))

            doc.build(story)
            logging.info(f"Report PDF exported to {target_file}")
            return target_file
        except Exception as e:
            logging.error(f"Failed to generate Report PDF: {e}")
            messagebox.showerror("PDF Export Error", f"Failed to build PDF document:\n{e}")
            return None

    # CSV EXPORT SCRIPT
    def export_csv_report(self):
        filename = f"LinkShield_Report_{int(time.time())}.csv"
        target_file = os.path.join(self.export_path, filename)
        try:
            with open(target_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Parameter", "Value"])
                writer.writerow(["Scan URL", self.latest_result["url"]])
                writer.writerow(["Final Destination", self.latest_result["final_url"]])
                writer.writerow(["Risk Score", self.latest_result["risk_score"]])
                writer.writerow(["Classification", self.latest_result["result_status"]])
                writer.writerow(["DNS IP Address", self.latest_result["geo_data"]["ip"]])
                writer.writerow(["Server Country", self.latest_result["geo_data"]["country"]])
                writer.writerow(["ISP Host", self.latest_result["geo_data"]["isp"]])
            return target_file
        except Exception as e:
            logging.error(f"Failed to export CSV: {e}")
            return None

    # JSON EXPORT SCRIPT
    def export_json_report(self):
        filename = f"LinkShield_Report_{int(time.time())}.json"
        target_file = os.path.join(self.export_path, filename)
        try:
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(self.latest_result, f, indent=4)
            return target_file
        except Exception as e:
            logging.error(f"Failed to export JSON: {e}")
            return None

    # HTML EXPORT SCRIPT
    def export_html_report(self):
        filename = f"LinkShield_Report_{int(time.time())}.html"
        target_file = os.path.join(self.export_path, filename)
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>LinkShield AI - Scan Report</title>
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; background-color: #0b1220; color: #ffffff; padding: 40px; }}
                    .card {{ background-color: #16213e; border: 1px solid #1e293b; border-radius: 12px; padding: 25px; max-width: 800px; margin: 0 auto; }}
                    h1 {{ color: #00e5ff; border-bottom: 2px solid #1e293b; padding-bottom: 10px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #1e293b; }}
                    th {{ color: #8a99ad; }}
                    .danger {{ color: #ff3b5c; font-weight: bold; }}
                    .safe {{ color: #00e676; font-weight: bold; }}
                    .warning {{ color: #ffc107; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>🛡️ LinkShield Security Assessment</h1>
                    <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <table>
                        <tr><th>Target Link</th><td>{self.latest_result["url"]}</td></tr>
                        <tr><th>Final Destination</th><td>{self.latest_result["final_url"]}</td></tr>
                        <tr><th>Risk Score Index</th><td>{self.latest_result["risk_score"]} / 100</td></tr>
                        <tr><th>Threat Status</th><td class="{self.latest_result['result_status'].lower()}">{self.latest_result["result_status"]}</td></tr>
                        <tr><th>Server Location</th><td>{self.latest_result["geo_data"]["city"]}, {self.latest_result["geo_data"]["country"]} ({self.latest_result["geo_data"]["ip"]})</td></tr>
                    </table>
                </div>
            </body>
            </html>
            """
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(html)
            return target_file
        except Exception as e:
            logging.error(f"Failed to export HTML: {e}")
            return None

    # =====================================================================
    # VIEW: SETTINGS WINDOW PANEL
    # =====================================================================
    def create_settings_view(self):
        view = customtkinter.CTkFrame(self.main_viewport, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(0, weight=1)

        card = customtkinter.CTkFrame(view, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color="#1E293B")
        card.grid(row=0, column=0, sticky="nsew", padx=50, pady=30)
        card.grid_columnconfigure(0, weight=1)

        # Title
        self.settings_title_lbl = customtkinter.CTkLabel(card, text="Application Configuration", font=("Segoe UI", 20, "bold"), text_color=TEXT_COLOR)
        self.settings_title_lbl.pack(pady=25)

        # Config Panel Grid elements
        config_grid = customtkinter.CTkFrame(card, fg_color="transparent")
        config_grid.pack(fill="x", padx=60)
        config_grid.grid_columnconfigure(0, weight=0)
        config_grid.grid_columnconfigure(1, weight=1)

        # 1. Themes Selector
        lbl_th = customtkinter.CTkLabel(config_grid, text="UI Theme Mode:", font=("Segoe UI", 13, "bold"), text_color=TEXT_COLOR)
        lbl_th.grid(row=0, column=0, padx=10, pady=12, sticky="e")
        self.opt_theme = customtkinter.CTkComboBox(config_grid, values=["Dark", "Light"])
        self.opt_theme.grid(row=0, column=1, padx=10, pady=12, sticky="w")
        self.opt_theme.set(self.theme_mode)

        # 2. Languages Selector
        lbl_lg = customtkinter.CTkLabel(config_grid, text="Interface Language:", font=("Segoe UI", 13, "bold"), text_color=TEXT_COLOR)
        lbl_lg.grid(row=1, column=0, padx=10, pady=12, sticky="e")
        self.opt_lang = customtkinter.CTkComboBox(config_grid, values=["English", "Spanish"])
        self.opt_lang.grid(row=1, column=1, padx=10, pady=12, sticky="w")
        self.opt_lang.set(self.current_language)

        # 3. Auto-save Switch
        lbl_as = customtkinter.CTkLabel(config_grid, text="Auto-Save Scan History to SQL DB:", font=("Segoe UI", 13, "bold"), text_color=TEXT_COLOR)
        lbl_as.grid(row=2, column=0, padx=10, pady=12, sticky="e")
        self.switch_autosave = customtkinter.CTkSwitch(config_grid, text="", progress_color=ACCENT_COLOR)
        self.switch_autosave.grid(row=2, column=1, padx=10, pady=12, sticky="w")
        if self.autosave_enabled:
            self.switch_autosave.select()

        # 4. Notifications Switch
        lbl_nt = customtkinter.CTkLabel(config_grid, text="System Sound & Alerts:", font=("Segoe UI", 13, "bold"), text_color=TEXT_COLOR)
        lbl_nt.grid(row=3, column=0, padx=10, pady=12, sticky="e")
        self.switch_alerts = customtkinter.CTkSwitch(config_grid, text="", progress_color=ACCENT_COLOR)
        self.switch_alerts.grid(row=3, column=1, padx=10, pady=12, sticky="w")
        if self.notifications_enabled:
            self.switch_alerts.select()

        # Save trigger Button
        self.btn_apply = customtkinter.CTkButton(
            card, text="Apply Settings Configuration", font=("Segoe UI", 14, "bold"),
            fg_color=ACCENT_COLOR, text_color="#0B1220", hover_color="#00B8D4",
            command=self.save_user_configurations
        )
        self.btn_apply.pack(pady=40)

        return view

    def save_user_configurations(self):
        self.theme_mode = self.opt_theme.get()
        self.current_language = self.opt_lang.get()
        self.autosave_enabled = self.switch_autosave.get() == 1
        self.notifications_enabled = self.switch_alerts.get() == 1

        # Apply GUI Theme immediately
        if self.theme_mode == "Dark":
            customtkinter.set_appearance_mode("dark")
            self.theme_toggle.deselect()
            self.theme_toggle.configure(text="Light Theme Mode")
        else:
            customtkinter.set_appearance_mode("light")
            self.theme_toggle.select()
            self.theme_toggle.configure(text="Dark Theme Mode")

        # Reload static titles text for active language
        self.apply_language_translation()

        messagebox.showinfo("Configuration Updated", "Your local configuration changes were successfully applied.")

    def apply_language_translation(self):
        lang = LANGUAGES[self.current_language]
        
        # Sidebar text translations
        self.sidebar_buttons["dashboard"].configure(text="📊  " + lang["dashboard"])
        self.sidebar_buttons["quick_scan"].configure(text="🚀  " + lang["quick_scan"])
        self.sidebar_buttons["scan_history"].configure(text="📜  " + lang["scan_history"])
        self.sidebar_buttons["reports"].configure(text="📁  " + lang["reports"])
        self.sidebar_buttons["settings"].configure(text="⚙️  " + lang["settings"])
        self.sidebar_buttons["about"].configure(text="ℹ️  " + lang["about"])

        # Dashboard Text translations
        self.dash_title.configure(text=lang["welcome"])
        self.dash_sub.configure(text=lang["subtitle"])
        self.card_total.title_label.configure(text=lang["total_scans"])
        self.card_clean.title_label.configure(text=lang["clean_scans"])
        self.card_warn.title_label.configure(text=lang["warning_scans"])
        self.card_threat.title_label.configure(text=lang["malicious_scans"])
        self.graph_title_lbl.configure(text=lang["scan_chart_title"])
        self.recent_lbl.configure(text=lang["recent_scans"])

        # Quick Scan translations
        self.url_input.configure(placeholder_text=lang["url_to_scan"])
        self.btn_scan.configure(text=lang["btn_scan"])
        self.gauge_lbl.configure(text=lang["risk_gauge_title"])
        self.hud_tabs.rename("Summary", lang["tab_summary"])
        self.hud_tabs.rename("Domain Info", lang["tab_domain"])
        self.hud_tabs.rename("SSL Cert", lang["tab_ssl"])
        self.hud_tabs.rename("Server Location", lang["tab_geo"])
        self.hud_tabs.rename("Redirect Trace", lang["tab_redirects"])
        self.hud_tabs.rename("Raw WHOIS", lang["tab_whois"])

        # Settings page translations
        self.settings_title_lbl.configure(text=lang["settings_title"])
        self.btn_apply.configure(text=lang["btn_save_settings"])

    def toggle_gui_theme(self):
        if self.theme_toggle.get() == 1:
            customtkinter.set_appearance_mode("light")
            self.theme_toggle.configure(text="Dark Theme Mode")
            self.theme_mode = "Light"
        else:
            customtkinter.set_appearance_mode("dark")
            self.theme_toggle.configure(text="Light Theme Mode")
            self.theme_mode = "Dark"

    # =====================================================================
    # VIEW: ABOUT VIEW PANEL
    # =====================================================================
    def create_about_view(self):
        view = customtkinter.CTkFrame(self.main_viewport, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(0, weight=1)

        card = customtkinter.CTkFrame(view, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color="#1E293B")
        card.grid(row=0, column=0, sticky="nsew", padx=60, pady=60)
        card.grid_columnconfigure(0, weight=1)

        logo = customtkinter.CTkLabel(card, text="🛡️", font=("Segoe UI", 92))
        logo.pack(pady=(40, 10))

        title = customtkinter.CTkLabel(card, text="LinkShield AI", font=("Segoe UI", 24, "bold"), text_color=ACCENT_COLOR)
        title.pack()

        version = customtkinter.CTkLabel(card, text="Version: 1.2.0 (Stable Commercial)", font=("Segoe UI", 12), text_color=TEXT_MUTED)
        version.pack(pady=5)

        desc = customtkinter.CTkLabel(
            card, text="LinkShield AI is an enterprise-grade desktop utility that intercepts, traces, and dissects URLs. It tracks complete HTTP redirections, verifies SSL/TLS certificate validity, resolves hosting server ISP locations, and runs deep behavioral analysis heuristics to prevent phishing and redirect-spoof attacks.",
            font=("Segoe UI", 13), text_color=TEXT_COLOR, wraplength=550, justify="center"
        )
        desc.pack(pady=20, padx=40)

        # Updates Simulator Button
        btn_update = customtkinter.CTkButton(
            card, text="Check for Updates", font=("Segoe UI", 13, "bold"), fg_color="#1E293B", text_color=ACCENT_COLOR,
            command=lambda: messagebox.showinfo("System Update", "LinkShield AI is currently running the latest stable build (1.2.0).")
        )
        btn_update.pack(pady=(10, 40))

        return view

    # =====================================================================
    # KEYBOARD SHORTCUTS BINDINGS
    # =====================================================================
    def bind_shortcuts(self):
        # Keyboard accelerators bindings
        self.bind("<Control-v>", lambda event: self.paste_from_clipboard())
        self.bind("<Control-V>", lambda event: self.paste_from_clipboard())
        self.bind("<Control-r>", lambda event: self.trigger_live_scan())
        self.bind("<Control-R>", lambda event: self.trigger_live_scan())
        self.bind("<Control-s>", lambda event: self.export_pdf_report())
        self.bind("<Control-S>", lambda event: self.export_pdf_report())
        self.bind("<Delete>", lambda event: self.clear_scan_fields())

    def clear_scan_fields(self):
        self.url_input.delete(0, tk.END)
        self.status_progress.set(0)
        self.status_lbl.configure(text="Ready to scan", text_color=SUCCESS_COLOR)

    # Clock update task
    def start_clock_update(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_lbl.configure(text=now)
        self.after(1000, self.start_clock_update)


# =====================================================================
# PROGRAM ENTRY POINT
# =====================================================================
if __name__ == "__main__":
    app = LinkShieldApp()
    app.mainloop()
