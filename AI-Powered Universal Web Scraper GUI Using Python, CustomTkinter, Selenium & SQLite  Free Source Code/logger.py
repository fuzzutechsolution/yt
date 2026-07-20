"""
Universal AI Web Scraper - Logging Module
Provides thread-safe logging, file logging, database logging, and GUI console log stream.
"""

import logging
import os
import sys
from queue import Queue
from datetime import datetime

# Global log queue for GUI console updates
log_queue = Queue(maxsize=1000)

class QueueHandler(logging.Handler):
    """
    Custom logging handler that streams logs to a thread-safe Queue
    for consumption by the GUI log console.
    """
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.queue.full():
                try:
                    self.queue.get_nowait()
                except Exception:
                    pass
            self.queue.put_nowait(msg)
        except Exception:
            self.handleError(record)

class DatabaseHandler(logging.Handler):
    """
    Custom logging handler that persists logs to the SQLite database.
    Imports DatabaseManager dynamically to avoid circular imports.
    """
    def emit(self, record):
        try:
            from database import DatabaseManager
            db = DatabaseManager.get_instance()
            if db:
                timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
                db.insert_log(timestamp, record.levelname, record.getMessage())
        except Exception:
            # Prevent logging errors from crashing the application or looping
            pass

def setup_logging(log_file="scraper.log", log_level=logging.INFO):
    """
    Configures the root logger with File, Database, Stream, and GUI Queue handlers.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Console / Stdout handler (primarily for terminal debug)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # 2. File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to create file logger: {e}", file=sys.stderr)

    # 3. GUI Queue Handler
    q_handler = QueueHandler(log_queue)
    q_handler.setFormatter(formatter)
    q_handler.setLevel(log_level)
    root_logger.addHandler(q_handler)

    # 4. Database Handler
    db_handler = DatabaseHandler()
    db_handler.setLevel(logging.INFO) # Keep warnings/info+ in DB
    root_logger.addHandler(db_handler)

    logging.info("Logging system initialized successfully.")
