import asyncio
from pyppeteer import launch
import json

async def main():
    # Launch the browser
    browser = await launch(headless=False)
    page = await browser.newPage()

    # Go to the Amazon deals page
    await page.goto('https://www.amazon.com/deals', {'waitUntil': 'networkidle2'})

    # Wait for cookies to be set
    await asyncio.sleep(10)  # Adjust the timeout as needed

    # Execute JavaScript to get all cookies as a string
    cookies = await page.evaluate('''() => {
        let cookieObject = {};
        document.cookie.split(';').forEach(cookie => {
            let [name, value] = cookie.split('=');
            cookieObject[name.trim()] = value;
        });
        return cookieObject;
    }''')

    # Save cookies to a file
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)

    print('Cookies saved to cookies.json')



    # Close the browser
    await browser.close()

# Run the main function
asyncio.get_event_loop().run_until_complete(main())
