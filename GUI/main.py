import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTextEdit, QStatusBar, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import json

# --- Import scrapers ---
from scrapers.jobs_ge import run_jobs_ge_script
from scrapers.my_jobs_ge import run_my_jobs_ge_script
from scrapers.hr_ge import run_hr_ge_script

class StopScrapingException(Exception):
    pass

class ScraperThread(QThread):
    log = pyqtSignal(str)
    done = pyqtSignal(list)

    def __init__(self, scraper_func):
        super().__init__()
        self.scraper_func = scraper_func
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        scraped = []

        def log_callback(msg):
            self.log.emit(msg)

        try:
            scraped = self.scraper_func(
                log_callback=log_callback,
                is_running=lambda: self._is_running
            )
        except Exception as e:
            self.log.emit(f"Error: {str(e)}")
        finally:
            self.done.emit(scraped)




class ScraperGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Seeker")
        self.setGeometry(100, 100, 800, 600)

        # --- Layouts ---
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # --- Dropdown ---
        self.site_selector = QComboBox()
        self.site_selector.addItems(["jobs.ge", "myjobs.ge", "hr.ge"])
        top_layout.addWidget(QLabel("Select site:"))
        top_layout.addWidget(self.site_selector)

        # --- Start Button ---
        self.start_button = QPushButton("Start Scraping")
        self.start_button.clicked.connect(self.start_scraping)
        top_layout.addWidget(self.start_button)

        # stop button

        self.stop_button = QPushButton("Stop Scraping")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scraping)
        top_layout.addWidget(self.stop_button)

        # --- Log Output ---
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Log output will appear here...")

        # --- Export & DB Buttons ---
        self.export_button = QPushButton("Export to JSON/CSV")
        self.export_button.clicked.connect(self.export_data)

        self.db_button = QPushButton("Add to Database")
        self.db_button.clicked.connect(self.add_to_db)

        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.db_button)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")

        # --- Assemble Layout ---
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.log_output)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

        # --- Scraper Map ---
        self.scraper_map = {
            "jobs.ge": run_jobs_ge_script,
            "myjobs.ge": run_my_jobs_ge_script,
            "hr.ge": run_hr_ge_script
        }

        self.scraped_jobs = []

    def stop_scraping(self):
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.stop()
            self.status_bar.showMessage("Stopping scraping...")
            self.log_output.append("Stopping...")

    def start_scraping(self):
        site = self.site_selector.currentText()
        scraper_func = self.scraper_map.get(site)

        if not scraper_func:
            self.log_output.append(f"No scraper found for {site}")
            return

        self.status_bar.showMessage(f"Scraping {site}...")
        self.log_output.append(f"Started scraping {site}...")

        self.thread = ScraperThread(scraper_func)
        self.thread.log.connect(self.log_output.append)
        self.thread.done.connect(self.scrape_done)
        self.thread.start()

        self.stop_button.setEnabled(True)

    def scrape_done(self, jobs):
        self.scraped_jobs = jobs
        self.status_bar.showMessage(f"Scraped {len(jobs)} jobs.")
        self.log_output.append(f"Done scraping. Got {len(jobs)} jobs.")
        self.stop_button.setEnabled(False)


    def export_data(self):
        if not self.scraped_jobs:
            self.log_output.append("No data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;CSV Files (*.csv)")
        if not path:
            return

        try:
            if path.endswith(".json"):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.scraped_jobs, f, ensure_ascii=False, indent=2)
                self.log_output.append(f"Exported to {path}")
            elif path.endswith(".csv"):
                import csv
                keys = self.scraped_jobs[0].keys()
                with open(path, "w", newline='', encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(self.scraped_jobs)
                self.log_output.append(f"Exported to {path}")
            else:
                self.log_output.append("Unsupported file format.")
        except Exception as e:
            self.log_output.append(f"Export error: {e}")

    def add_to_db(self):
        from scrapers.db_writer import insert_jobs_to_db

        if not self.scraped_jobs:
            self.log_output.append("No jobs to add to DB.")
            return

        site = self.site_selector.currentText().replace(".", "_")
        try:
            json_file = "temp_jobs.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(self.scraped_jobs, f, ensure_ascii=False, indent=2)
            insert_jobs_to_db(json_file, site, log_callback=self.log_output.append)
            self.status_bar.showMessage("Database updated.")
        except Exception as e:
            self.log_output.append(f"DB error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScraperGUI()
    window.show()
    sys.exit(app.exec())