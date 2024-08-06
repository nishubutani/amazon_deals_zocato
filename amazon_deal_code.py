import json
import logging
import os
import time
import random
import pandas as pd
import requests
from parsel import Selector
from datetime import datetime


# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging to a file in the "logs" directory, organized by day
today_date = datetime.now().strftime("%d_%m_%Y")
log_filename = f'logs/scraper_log_{today_date}.log'
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# scrape_type = "discount"
params = {}

scraper_type = int(input("please select the scraper_type\n\n\t 1.deals\n\t 2.discount \n\n\tEnter here :-"))

if scraper_type == 1:
# if scrape_type == "deals":
    params['filters'] = '{"includedDepartments":[],"excludedDepartments":[],"includedTags":[],"excludedTags":["restrictedasin","noprime","GS_DEAL","StudentDeal"],"promotionTypes":[],"accessTypes":[]}'
    params['refinementFilters'] = '[{"id":"reviewRating","value":["4"]},{"id":"price","value":["2"]},{"id":"percentOff","value":["3"]}]'
elif scraper_type == 2:
# elif scrape_type == "discount":
    params['filters'] = '{"includedDepartments":[],"excludedDepartments":[],"includedTags":[],"excludedTags":["restrictedasin","noprime","GS_DEAL","StudentDeal"],"promotionTypes":["COUPON"],"accessTypes":[]}'
    params['refinementFilters'] = '[{"id":"reviewRating","value":["4"]},{"id":"price","value":["2"]},{"id":"percentOff","value":["3"]},{"id":"departments","value":["11055981"]}]'
else:
    print("")

# cookies = { # 'session-id': '139-5319982-5406647', 'session-id': '147-2845108-4886318', # 'session-id-time':
#     '2082787201l', 'session-id-time': '2082787201l', 'lc-main': 'en_US', 'i18n-prefs': 'INR', # 'ubid-main':
#     '135-9624645-9041922', 'ubid-main': '131-1740196-4335608', 'sp-cdn': '"L5Z9:IN"', # 'session-token':
#     'raq6p4LiaINGOcLeitHGGZp3P7UqT6EsJ/jfh39dfqwvHMMJTNLfA1hu2X7hlzoRVQhcfrHoWnkqoEiFJpZ4PSUnqX5ave3YdCI0mfLUiSi8rmdVXuvm0wM2pZDgsj7dxiqTBMs1u00+jAQZDDxXUNjulumxggIzw6/+DcePwpWXRAvfKiqKsVzdWQBCasjGHDdyQ7c/HwvnMwcN/3SFToW4Fn1wl7aJr9P4ec3q1pou+UyicAFcXlMBN/UD/BeEdezsK0JQIKRw7DQBYwnYI6rY6RWJHIZBSCiCQhlRdspcp6TM5GCSS6zdDMp720AnwQ2GtLK7YuJ2djg4U1Ct10E21bRPT/8M', 'session-token': 'ZtznrN9TK86EHcyG01hQokOA8bqCTZIZNBTqRL9R99pNKRIjYa5972mgG/hzgg4FR+3Za9tUy+SL2dNA+bZQ3M0QfVtw8o5GTZsnQHpKw1CSy10TIX0TjBiymdaxozADDjxottjozTKXgnmuiBv5qNvhfrjqfKXvaWOkTXqaWcb0PC69sVWrHQpOiXp/rOTuoq/A0WHEnwpvdSigM2s+pd18NPfF4+gdEkTNKynCfSpT97OOy0JoX7bmH51HmuaMl312u5cvA1ixtYqJBcjNLut/vWHeCT8GKKBV9lmsg1xBGOxaF+pvy3L6/IhfIuXCnohVyxAAIvDaHLx4JeSDJ1H0LLRTwrLv', }

try:
    with open('data.json', 'r') as f:
        cookies1 = json.load(f)
        cookies = cookies1['cookies']
        slate_token = cookies1['slate_token']
        csrf_token = cookies1['csrf_token']
        logging.info("Successfully loaded cookies and tokens from data.json")
except Exception as e:
    logging.error(f"Failed to load cookies and tokens: {e}")
    exit()


headers = {
    'accept': 'application/vnd.com.amazon.api+json; type="promotions.search.result/v1"; expand="rankedPromotions[].product(product/v2).title(product.offer.title/v1),rankedPromotions[].product(product/v2).links(product.links/v2),rankedPromotions[].product(product/v2).buyingOptions[].dealBadge(product.deal-badge/v1),rankedPromotions[].product(product/v2).buyingOptions[].dealDetails(product.deal-details/v1),rankedPromotions[].product(product/v2).buyingOptions[].promotionsUnified(product.promotions-unified/v1),rankedPromotions[].product(product/v2).productImages(product.product-images/v2),rankedPromotions[].product(product/v2).twisterVariations(product.twister-variations/v2)"; experiments="BadgeColors_4da10b4,slotName_72rvpj15,insightTypes_72rvpj15"',
    'accept-language': 'en-US',
    'content-type': 'application/json',
    'origin': 'https://www.amazon.com',
    'priority': 'u=1, i',
    'referer': 'https://www.amazon.com/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    # 'x-amzn-encrypted-slate-token': 'AnYxFaujBfG7Tt6kcxxkLvd14HLXqE1q7ttjNzvHHCydkbYvV1aJiXDObq4MdCALVR1SRzJVMchvLa5JnGAmG4nwSanrxh27ebk4bgkcYEA2F9AyJQtAvCIhwP3m1pTjIHsJgH75aKFq5S/jv5qgwbVXl4/2iVn00oaFywNLHTlFPGkZwgcG1FptnJQ51YnC9+8/XX0e0bFs9s5QDvuKoTbVPTJ97FYfmdS+nAf0etsOaeonf86Un4yLlX3V2hCiPNvq8WR4E1NCoVgVNB02tD+vbZM0Axg=',
    # 'x-amzn-encrypted-slate-token': 'AnYxqu1pfmzNNCd2NUYpe83AU9RxlJSofca4kwi5Xgn3EUIK4TKcr8vdpbTFnDoMSFqwk4d4HE0h+uqNZ866/xM7xjjkdDQr9wsNrny7I3gZkaDY9XMhmKss424G6HS6HFnDjQBV3xx1r1Rm1opbWYkolaMuvMoVnrXaK6KwtKrYdyV8Ca//Uj6VPL3DyEPhR2NJT5jlnx6fuC+jtdavWAYTWr5l/+UeCKo21d+MEoIkKU/bf9daU/rzTLR3EyAI+DbNDgmy0AbmWWqFixuUx6TqEEifjg==',
    'x-amzn-encrypted-slate-token': slate_token,
    # 'x-api-csrf-token': '1@g40wFa56M2hp3AImxWzRaStETGl/vsvrqRHATW9WcSQAAAAAAQAAAABmpeU/cmF3AAAAAGfA1H5nd8xGEcC33NuKVw==@RQ2CWZ',
    'x-api-csrf-token': csrf_token,
    'x-cc-currency-of-preference': 'INR',
}

params.update({
    'pageSize': '100',
    'startIndex': '0',
    'calculateRefinements': 'false',
    '_enableNestedRefs': 'true',
    'rankingContext': '{"pageTypeId":"deals","rankGroup":"BUZZ_WORTHY_RANKING"}',
    'sortOrder': 'DEFAULT',
    'pinnedPromotionGroups': '[["B07PXGQC1Q"]]',
})

def get_response_with_retries(url, params, headers, cookies, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, cookies=cookies)
            if response.status_code == 200:
                logging.info(f"Attempt {attempt + 1} succeeded with status code 200")
                return response
            elif response.status_code == 503:
                logging.warning(f"Attempt {attempt + 1} failed with status code 503. Retrying...")
                time.sleep(random.uniform(5.05, 15.0))
            else:
                logging.error(f"Attempt {attempt + 1} failed with unexpected status code {response.status_code}")
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} encountered an error: {e}")

    return None

response = get_response_with_retries('https://data.amazon.com/api/marketplaces/ATVPDKIKX0DER/promotions', params, headers, cookies)

if response and response.status_code == 200:
    data = response.json()
    # ranked_promotions = data.get('entity', {}).get('rankedPromotions', [])
    ranked_promotions = data.get('entity', {}).get('rankedPromotions', [])[:10]  # Limit to first 10 promotions
    logging.info(f"file Generated: files/{len(ranked_promotions)}")

    product_data_list = []

    count = 0
    for promotion in ranked_promotions:
        try:
            title = promotion['product']['entity']['productImages']['entity'].get('altText', '')
            asin = promotion['product']['entity']['asin']
            discount_text = ''
            discount = ''
            product_images = []
            product_url = f"https://www.amazon.com/dp/{asin}"

            try:
                txt = promotion['product']['entity']['buyingOptions'][0]['promotionsUnified']['entity']['displayablePromotions'][0]['claimAjaxPostLink']['data'].get('successText', '')
                if txt:
                    discount_text = txt.split("</b>")[1].split("<")[0].strip()
            except Exception as e:
                logging.warning(f"Failed to parse discount text: {e}")
                discount_text = ''

            try:
                discount = promotion['product']['entity']['buyingOptions'][0]['dealBadge']['entity']['label']['content']['fragments']
            except Exception as e:
                logging.warning(f"Failed to parse discount: {e}")
                discount = ''

            try:
                image_data = promotion['product']['entity']['productImages']['entity']['images']
                base_url = "https://m.media-amazon.com/images/I/"

                for image in image_data:
                    hi_res_url = f"{base_url}{image['hiRes']['physicalId']}.{image['hiRes']['extension']}"
                    low_res_url = f"{base_url}{image['lowRes']['physicalId']}.{image['lowRes']['extension']}"
                    product_images.extend([hi_res_url, low_res_url])
            except Exception as e:
                logging.warning(f"Failed to parse product images: {e}")
                product_images = []

            for attempt in range(3):
                try:
                    product_response = requests.get(product_url, headers=headers)
                    if product_response.status_code == 200:
                        break
                    else:
                        print(f"Attempt {attempt+1} to get product details failed. Retrying...")
                        time.sleep(random.uniform(1.05, 5.0))
                except Exception as e:
                    logging.error(f"Attempt {attempt + 1} encountered an error: {e}")

            if product_response.status_code == 200:
                selector = Selector(product_response.text)
                product_title = selector.xpath('//span[@id="productTitle"]/text()').get().strip() if selector.xpath('//span[@id="productTitle"]/text()') else ''
                list_price = selector.xpath('//td[contains(text(),"List Price:")]/../td/span/span[@class="a-offscreen"]/text()').get()
                deal_price = selector.xpath('//td[contains(text(),"Deal Price:")]/../td/span/span[@class="a-offscreen"]/text()').get()
                discount = selector.xpath('//td[contains(text(),"You Save:")]/../td/span/text()[2]').get()
                normal_price = selector.xpath('//td[contains(text(),"Price:")]/../td/span/span[@class="a-offscreen"]/text()').get()

                about_item = selector.xpath('//div[@id="feature-bullets"]/ul/li/span/text()').getall()
                about_item1 = about_item[0].strip() if about_item else ''
                about_item2 = about_item[1].strip() if len(about_item) > 1 else ''

                item = {
                    'Product Image': None,
                    'Product Image URL List': product_images,
                    'Product Description': title,
                    'Normal Price': normal_price,
                    'Discounted Price': deal_price,
                    'List Price': list_price,
                    'Discount or Coupon': discount,
                    'Discount or Deal Text': discount_text,
                    'Link URL': product_url,
                    'About Item 1': about_item1,
                    'About Item 2': about_item2,
                }

                # Add dynamic 'Product Image URL' entries
                for i, image_url in enumerate(product_images[:5]):
                    item[f'Product Image URL{i + 1}'] = image_url

                product_data_list.append(item)
                count = count + 1
                logging.info(f"Data inserted: {count}")
                time.sleep(random.uniform(1.05, 5.0))
        except:
            pass

    today_date = datetime.now().strftime("%d_%m_%Y")
    csv_file = f'{scraper_type}_output_{today_date}.csv'


    df = pd.DataFrame(product_data_list, index=range(1, len(product_data_list) + 1))
    df.to_csv(f'files/{csv_file}', index=False)
    logging.info(f"file Generated: files/{csv_file}")

else:
    logging.info(f"Failed to retrieve data after multiple attempts.")
