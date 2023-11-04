import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# Read the Excel file into a DataFrame
df = pd.read_excel("Input.xlsx")

# Iterate through the DataFrame rows
for index, row in df.iterrows():
    URL_ID = str(row['URL_ID'])
    link = row['URL']

    if pd.notna(link):
        response = requests.get(link)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        article_content = []
        article_elements = soup.find_all('p')
        
        for article_element in article_elements:
            article_content.append(article_element.get_text().strip())

        if not os.path.exists('scraped_content'):
            os.makedirs('scraped_content')

        filename = f'{URL_ID}.txt'
        filepath = os.path.join('scraped_content', filename)

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write("Article Content:\n")
            for content in article_content:
                file.write(content + '\n')

        print(f"Content for URLID {URL_ID} saved to '{filepath}'")
