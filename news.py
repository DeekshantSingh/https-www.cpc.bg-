import requests
import string
from parsel import Selector
from datetime import datetime
import pandas as pd

# Cookies used for making requests (can help with bypassing certain protections)
cookies = {
    'orchantiforgery_DefaultC%3a%5cKZK.Portal': 'CfDJ8HQ9ThffJR9NhFRsVDahbkpA496cDV-1w2lzoGVuj6wNQuceVitfrdgTvaTS-si9nuHjEKIcnDpKHBEhIz1c5WWiCWFcxjBSN6-9xpxWBo8cnQSBwqlMq7Qjqu25m3JrQoC2KuxdeGeAK9Ps3bNFX1Q',
    'cf_clearance': 'Lm7YXtjnXIu0tNPFYISmcUMAL2GdiE1FY0EAlAVaG5o-1731480046-1.2.1.1-5nDobld8gSrz.W4n5..CPQVj.3awTyMMkXtg90pBAKY7NDXSg.pqsGuxBt0q3b126u6v_QXd9xnNpwaYV831pbFa6UmI.9xx5raQZs_Dw5PRrg.DwLCaLwXAy11u6ZmllQVPG3GJAyq7jzRujlKg3PvjEOt0sZ32haiACFIf_XkIjB1cpZl.DyuGhnqBXXkj76XUruBx0OnhXDiPAREkg_9QZn4Xn0OCGfSda8TL4DJ4ygi8BvmmL.kGUBQN2RINH6iorceZd3tFXGTLXsu1seATEjO.CMYItkJpLdNpaBbuVLQdSsKwPfcguZAxWQ3TBvp3USjMieYHGAyYPsGAhbs4IFGxVp72CLPb50zsip4JwRiU8CZ6_y_hDVFOg1BFKNUtwV.L07e0c6B8gr7Qqw',
    'cconsent': '{"version":1,"categories":{"necessary":{"wanted":true},"optional":{"wanted":true}},"services":["analytics","system","accessibility"]}',
    '_ga': 'GA1.1.494414733.1731480075.1.1.1731480083.0.0.0',
    '.AspNetCore.Culture': 'c%3Den-US%7Cuic%3Den-US',
    '_ga_M3RFBTPXW9': 'GS1.1.1731480075.1.1.1731480083.0.0.0',
}

# Custom function to save the data into an Excel file
def save_to_excel(filename='cpc_news.xlsx'):
    df = pd.DataFrame(data_entry)  # Convert the list of dictionaries to a DataFrame
    df.to_excel(filename, index=False, engine='openpyxl')  # Save as Excel file
    print(f"Data saved to {filename}")  # Confirmation message

# Function to remove punctuation and extra spaces from a sentence
def remove_punctuation(sentence):
    translator = str.maketrans('', '', string.punctuation)  # Translation table to remove punctuation
    cleaned = sentence.translate(translator)  # Remove punctuation
    cleaned2 = ' '.join(cleaned.split())  # Remove extra spaces
    return cleaned2

# Function to format the date from 'day.month.year' to 'year-month-day'
def format_date(date_str):
    date_obj = datetime.strptime(date_str, '%d.%m.%Y')  # Parse the date
    return date_obj.strftime('%Y-%m-%d')  # Return in 'YYYY-MM-DD' format

# Main scraper loop for paginated news pages
i = 1
pagination = True
while pagination:

    url = f'https://www.cpc.bg/en/news?page={i}'  # URL with pagination

    # Send a GET request to the news page
    response = requests.get(url, cookies=cookies, headers=headers)
    parsed_data = Selector(response.text)  # Parse the page HTML using the Selector
    boxes = parsed_data.xpath('//div[@class="news-container"]//a')  # Find news boxes

    # Loop through each news box and extract data
    for box in boxes:
        news_date = box.xpath('.//div[@class="news-summary-date"]//text()').get()  # Extract date
        news_date = format_date(str(news_date).strip())  # Format the date
        news_summary = box.xpath('//div[@class="news-summary-content"]//text()').get()  # Extract summary
        news_link = 'https://www.cpc.bg/'+box.xpath('.//@href').get()  # Construct the full link
        if 'news' not in news_link.strip():
            news_link = None  # Skip invalid links

        news_title = box.xpath('.//div[@class="news-summary-title"]//text()').get()  # Extract title
        news_heading = ' '.join(news_title.split())  # Clean title
        response2 = requests.get(news_link, headers=headers, cookies=cookies)  # Fetch article page
        parsed_data2 = Selector(response2.text)  # Parse the article page

        # Extract full news content and clean it
        details_news = str(parsed_data2.xpath('//div[@class="news-detail-content"]//text()').getall()).strip().replace(']','').replace('[','')
        details_news2 = ' '.join(details_news.split()).replace("\\xa0",' ').replace("\', \'\\n\', \'",'').replace("\'",'').replace("\'",'').replace('\\n',' ')
        details_news2 = ' '.join(details_news2.split())  # Clean full content

        # Store the news details in a dictionary
        news_details = {
            "news_date": news_date,
            "news_link": news_link.strip(),
            "news_title": news_heading.strip(),
            "news_summary": news_summary.strip(),
            "news_details_content": details_news2
        }
        data_entry.append(news_details)  # Add news details to the list
        print(news_details)  # Print news details for debugging

    # Check if there is a next page; if not, stop the loop
    next_page = parsed_data.xpath('//li[contains(@class,"paggination-next")]/a[contains(@class,"disabled")]')
    if next_page:
        break
    else:
        i += 1  # Move to the next page

    print("============================================================")

# Save all collected data to an Excel file
save_to_excel()
print("done")
