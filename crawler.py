import os
import requests
from bs4 import BeautifulSoup, Comment
import json
import time
from filter_text import filter_content
from filter_image import is_valid_image, filter_violent_images
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

def fetch_wikipedia_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the web page")
        return None
    return response.text

def save_content_to_json(paragraphs, links, images, tables, metadata, forms, base_url, original_url, filename='page_content.json'):
    data = {
        'original_url': original_url,
        'content': [{'index': i+1, 'paragraph': para} for i, para in enumerate(paragraphs)],
        'links': [{'index': i+1, 'link': link['href'] if link['href'].startswith('http') else base_url + link['href']} for i, link in enumerate(links)],
        'images': [{'index': i+1, 'path': os.path.abspath(img_path)} for i, img_path in enumerate(images)],
        'tables': [{'index': i+1, 'table': str(table)} for i, table in enumerate(tables)],
        'metadata': metadata,
        'forms': forms
    }
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def download_and_filter_image(img_url, base_url, directory, retries=3):
    if img_url.startswith('//'):
        img_url = 'https:' + img_url
    elif img_url.startswith('/'):
        img_url = base_url + img_url

    for attempt in range(retries):
        try:
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                if is_valid_image(response):
                    img = Image.open(BytesIO(response.content))
                    if filter_violent_images(img):
                        img_path = os.path.join(directory, f'image_{len(os.listdir(directory)) + 1}.jpg')
                        with open(img_path, 'wb') as f:
                            f.write(response.content)
                        return img_path
            else:
                print(f"Failed to download image {img_url}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        except Exception as e:
            print(f"Failed to process image {img_url}: {e}")
    return None

def download_images(soup, base_url, directory='images'):
    if not os.path.exists(directory):
        os.makedirs(directory)

    images = soup.find_all('img')
    image_paths = []
    for img in images:
        img_url = img.get('src')
        if img_url is None:
            continue  # Skip images without src attribute
        
        img_path = download_and_filter_image(img_url, base_url, directory)
        if img_path:
            image_paths.append(img_path)
    
    return image_paths

def extract_paragraphs_and_headings(soup):
    content = []
    for element in soup.find_all(['p', 'h2', 'h3']):
        if element.name in ['h2', 'h3']:
            content.append(f"Heading: {element.get_text()}")
        elif element.name == 'p':
            content.append(element.get_text())
    return content

def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

def crawl_page(url, output_dir):
    base_url = get_base_url(url)
    html_content = fetch_wikipedia_page(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        content = extract_paragraphs_and_headings(soup)
        links = soup.find_all('a', href=True)
        tables = soup.find_all('table')
        metadata = {
            'title': soup.title.string if soup.title else '',
            'description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else ''
        }
        forms = [{'action': form.get('action', ''), 'method': form.get('method', ''), 'inputs': [{'name': input.get('name'), 'value': input.get('value', '')} for input in form.find_all('input')]} for form in soup.find_all('form')]
        
        filtered_content = filter_content(content)
        
        image_paths = download_images(soup, base_url, directory=os.path.join(output_dir, 'images'))
        
        save_content_to_json(filtered_content, links, image_paths, tables, metadata, forms, base_url, url, filename=os.path.join(output_dir, 'page_content.json'))
        print(f"Content from {url} saved in {output_dir}")