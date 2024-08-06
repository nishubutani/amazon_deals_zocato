import asyncio
from datetime import datetime
import os

from pyppeteer import launch
import json
import re
import logging

# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging to a file in the "logs" directory, organized by day
today_date = datetime.now().strftime("%d_%m_%Y")
log_filename = f'logs/cookie_log_{today_date}.log'
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def main():
    logging.info("Launching browser")
    # Launch the browser
    browser = await launch(headless=True)
    page = await browser.newPage()

    # Go to the Amazon deals page
    logging.info("Navigating to Amazon deals page")
    await page.goto('https://www.amazon.com/deals', {'waitUntil': 'networkidle2'})

    # Wait for the page to load and cookies to be set
    logging.info("Waiting for the page to load")
    await asyncio.sleep(10)  # Adjust the timeout as needed

    # Execute JavaScript to get all cookies as a string
    logging.info("Extracting cookies")
    cookies = await page.evaluate('''() => {
        let cookieObject = {};
        document.cookie.split(';').forEach(cookie => {
            let [name, value] = cookie.split('=');
            cookieObject[name.trim()] = value;
        });
        return cookieObject;
    }''')

    # Extract the slate_token using XPath
    logging.info("Extracting slate_token using XPath")
    slate_token_element = await page.xpath('//meta[@name="encrypted-slate-token"]')
    if slate_token_element:
        slate_token = await page.evaluate('(element) => element.getAttribute("content")', slate_token_element[0])
        logging.info("Slate token found")
    else:
        slate_token = None
        logging.warning("Slate token not found")

    # Extract the page content
    logging.info("Extracting page content")
    page_content = await page.content()

    # Use regex to find the csrf_token
    logging.info("Extracting csrf_token using regex")
    csrf_token_match = re.search(r'"csrfToken":"(.*?)","', page_content)
    csrf_token = csrf_token_match.group(1) if csrf_token_match else None
    if csrf_token:
        logging.info("CSRF token found")
    else:
        logging.warning("CSRF token not found")

    # Save cookies and tokens to a file
    logging.info("Saving cookies and tokens to a file")
    data = {
        'cookies': cookies,
        'slate_token': slate_token,
        'csrf_token': csrf_token,
    }

    with open('data.json', 'w') as f:
        json.dump(data, f)
        logging.info("Data saved to data.json")

    # Close the browser
    logging.info("Closing browser")
    await browser.close()


# Run the main function
asyncio.get_event_loop().run_until_complete(main())
