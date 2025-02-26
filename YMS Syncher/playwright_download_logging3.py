import os
import logging
from playwright.sync_api import Playwright, sync_playwright
from import_csv_to_sql import import_csv_to_sql  # Ensure this import is correct

# Use an absolute path for the log file
log_file_path = r'C:\ymsinventorysnapshot\import_csv_to_sql.log'

# Configure logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Create a logger
logger = logging.getLogger(__name__)

logger.info("Executing playwright_download_logging3.py script!")

def run(playwright: Playwright) -> None:
    try:
        logger.info("Launching browser...")
        browser = playwright.chromium.launch(headless=False)  # Set headless to True
        context = browser.new_context()
        page = context.new_page()
        
        logger.info("Navigating to login page...")
        page.goto("https://allen.ymshub.com/login")
        
        # Fill in the username and password
        logger.info("Filling in login credentials...")
        page.get_by_placeholder("Username").click()
        page.get_by_placeholder("Username").fill("kthomas")
        page.get_by_placeholder("Username").press("Tab")
        page.get_by_placeholder("Password").fill("Password1!")
        
        # Click the login button
        logger.info("Logging in...")
        page.get_by_role("button", name="Let's go").click()
        
        page.get_by_role("link", name=" Reports").click()
        page.wait_for_timeout(2000)  # Adjust the time as needed
        page.get_by_role("link", name="CI Current Inventory").click()
        page.wait_for_timeout(2000)  # Adjust the time as needed
        page.get_by_role("combobox", name="Building").click()
        page.wait_for_timeout(2000)  # Adjust the time as needed
        page.get_by_role("button", name="Select All", exact=True).click()
        page.wait_for_timeout(2000)  # Adjust the time as needed
        #page.get_by_role("button", name="Search").click()
        page.wait_for_timeout(2000)  # Adjust the time as needed
        page.get_by_role("button", name="Show 100 rows▼").click()
        page.wait_for_timeout(2000)  # Adjust the time as needed
        page.get_by_role("button", name="Show All").click()
        page.wait_for_timeout(3000)  # Adjust the time as needed

        # Click the CSV download button and wait for the download to start
        logger.info("Downloading CSV...")
        with page.expect_download() as download_info:
            page.get_by_role("button", name="CSV").click()
        
        download = download_info.value
        suggested_filename = download.suggested_filename
        download_path = os.path.join(os.getcwd(), suggested_filename)
        download.save_as(download_path)
        logger.info(f"File downloaded to: {download_path}")
        
        # Click the logout button
        logger.info("Logging out...")
        page.get_by_role("link", name="").click()

        # Close the browser
        context.close()
        browser.close()
        logger.info("Browser closed.")
        
        # Call the import function
        logger.info("Importing CSV to SQL...")
        import_csv_to_sql(download_path)  # Correct function call
        logger.info("CSV import completed.")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
