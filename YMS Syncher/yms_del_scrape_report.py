from config import DOWNLOAD_DIR, LOG_FILE
from pathlib import Path
import logging
from playwright.sync_api import sync_playwright
import subprocess
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def scrape_driver_event_log():
    """Scrape the Driver Event Log report and download it as a CSV."""
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            # Navigate to the login page
            logger.info("Navigating to the login page...")
            page.goto("https://allen.ymshub.com/login")

            # Login
            logger.info("Logging in...")
            page.fill("input[placeholder='Username']", "kthomas")
            page.fill("input[placeholder='Password']", "Password1!")
            page.press("input[placeholder='Password']", "Enter")

            # Navigate to the report page
            logger.info("Navigating to the report page...")
            page.click("a:has-text('Reports')")
            page.click("a:has-text('DEL Driver Event Log')")

            # Configure filters
            logger.info("Configuring filters...")
            page.get_by_role("combobox", name="All start facilities").click()
            page.wait_for_timeout(3000)  # Adjust the time as needed
            page.get_by_role("button", name="Select All", exact=True).click()
            page.wait_for_timeout(9000)  # Adjust the time as needed
            page.get_by_role("combobox", name="All end facilities").click()
            page.wait_for_timeout(9000)  # Adjust the time as needed
            page.get_by_role("button", name="Select All", exact=True).click()
            page.get_by_role("button", name="Search").click()

            # Set rows to show all
            logger.info("Configuring rows to show all...")
            page.click("button:has-text('Show 100 rows')")
            page.click("button:has-text('Show All')")

            # Wait for the table to load
            page.wait_for_timeout(9000)

            # Download the CSV
            logger.info("Downloading the report as a CSV...")
            with page.expect_download() as download_info:
                page.click("button:has-text('CSV')")
            download = download_info.value

            # Save the downloaded file
            file_path = DOWNLOAD_DIR / download.suggested_filename
            download.save_as(str(file_path))
            logger.info(f"Report downloaded to: {file_path}")

            # Close browser
            context.close()
            browser.close()

            return file_path
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting scrape...")
        csv_path = scrape_driver_event_log()

        # Run the import script
        logger.info("Running the import script...")
        script_dir = Path(__file__).resolve().parent
        import_script_path = script_dir / "yms_del_import_csv_to_sql.py"
        from sys import executable
        subprocess.run([executable, str(import_script_path), str(csv_path)])
    except Exception as e:
        logger.error(f"Error in main execution: {e}")

