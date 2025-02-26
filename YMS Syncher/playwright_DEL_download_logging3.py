
import os
import logging
from playwright.sync_api import sync_playwright

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run(playwright):
    # Define download path relative to the script
    script_dir = os.path.dirname(__file__)  # Get the directory where the script is located
    download_path = os.path.join(script_dir, 'downloads')  # Create a 'downloads' folder in the same directory
    
    # Ensure the download directory exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    logger.info("Launching browser...")
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    
    page = context.new_page()
    page.goto("https://allen.ymshub.com/login")
    page.get_by_placeholder("Username").click()
    page.get_by_placeholder("Username").fill("kthomas")
    page.get_by_placeholder("Username").press("Tab")
    page.get_by_placeholder("Password").fill("Password1!")
    page.get_by_placeholder("Password").press("Enter")
    page.get_by_role("link", name=" Reports").click()
    page.get_by_role("link", name="DEL Driver Event Log").click()
    page.get_by_role("combobox", name="All start facilities").click()
    page.wait_for_timeout(2)  # Adjust the time as needed
    page.get_by_role("button", name="Select All", exact=True).click()
    page.get_by_role("combobox", name="All end facilities").click()
    page.wait_for_timeout(2)  # Adjust the time as needed
    page.get_by_role("button", name="Select All", exact=True).click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("button", name="Show 100 rows▼").click()
    page.get_by_role("button", name="Show All").click()
    page.wait_for_timeout(5000)  # Adjust the time as needed
    # Capture the download and save it
    with page.expect_download() as download_info:
        page.get_by_role("button", name="CSV").click()
    
    download = download_info.value
    suggested_filename = download.suggested_filename
    file_path = os.path.join(download_path, suggested_filename)  # Save the file in the 'downloads' folder
    download.save_as(file_path)
    logger.info(f"File downloaded to: {file_path}")
    page.wait_for_timeout(2000)  # Adjust the time as needed
    # Logging out after download
    logger.info("Logging out...")
    page.get_by_role("link", name="").click()

    context.close()
    browser.close()
    logger.info("Browser closed successfully.")

# Running the script using Playwright
with sync_playwright() as playwright:
    run(playwright)
