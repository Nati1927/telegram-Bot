import io
import sys
from bs4 import BeautifulSoup
import requests
import time
import logging
import html

BOT_TOKEN = '6569019672:AAGZM-WC54xi2Y2Yorvs3ODCadwv7UBqupw'
CHANNEL_ID = '@nattiOnlineMarket'  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

posted_posts = set()

def send_to_channel(title, price, image_url, view_more_link):
    try:
        api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
        
        # Download the image
        response = requests.get(image_url)
        if response.status_code == 200:
            # Save the image locally
            with open('temp_image.jpg', 'wb') as f:
                f.write(response.content)
            
            # Open the image file
            photo_file = {'photo': open('temp_image.jpg', 'rb')}
            
            # HTML caption with clickable link around the image and "View More" link
            caption_html = f"<a href='{view_more_link}'>;</a><b>{html.escape(title)}</b>\n<b>Price</b>:{html.escape(price)}\n<a href='{view_more_link}'>View More</a>"

            params = {
                'chat_id': CHANNEL_ID,
                'caption': caption_html,
                'parse_mode': 'HTML'
            }

            response = requests.post(api_url, params=params, files=photo_file)
            response.raise_for_status()

            logger.info("Message sent successfully to the channel.")
        else:
            logger.error("Failed to download the image.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to the channel: {e}")

def scrape_and_send_to_channel():
    url = 'https://helloomarket.com/'

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve the webpage. Error: {e}")
        return

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
    
        products = soup.select('.box-content .box-product .product-items .product-block')

        for product in products:
            image_url = product.select_one('.product-block-inner img').get('src')
            title = product.select_one('.product-details .caption h4').text.strip()
            price = product.select_one('.product-details .caption p').text.strip()
            view_more_link = product.select_one('.product-details .caption a').get('href')

            if title not in posted_posts:
                logger.info(f"Sending message to the channel for: {title}")
                send_to_channel(title, price, image_url, view_more_link)

                posted_posts.add(title)

            time.sleep(5)

    else:
        logger.warning(f"Failed to retrieve the webpage. Status code: {response.status_code}")

while True:
    scrape_and_send_to_channel()
    time.sleep(400)
