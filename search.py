import os
import requests
from bs4 import BeautifulSoup
import json

def search_google(query, num_results=10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    search_url = f"https://www.google.com/search?q={query}"
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve search results")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for g in soup.find_all('div', class_='g')[:num_results]:
        title = g.find('h3')
        if title:
            link = g.find('a', href=True)
            if link:
                results.append({
                    'title': title.get_text(),
                    'link': link['href']
                })
    return results

def save_results_to_json(results, directory='results'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for i, result in enumerate(results):
        filename = os.path.join(directory, f'result_{i+1}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

def main():
    query = input("Please enter your search: ")
    results = search_google(query)
    if results:
        save_results_to_json(results)
        print(f"Top {len(results)} search results saved in the 'results' folder")
    else:
        print("No results found")

if __name__ == "__main__":
    main()
