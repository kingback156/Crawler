import os
from search import search_google
from crawler import crawl_page

def main():
    query = input("Please enter your search query: ")
    num_results = 10
    
    results = search_google(query, num_results)
    
    if results:
        if not os.path.exists('crawler_results'):
            os.makedirs('crawler_results')
        
        for i, result in enumerate(results):
            output_dir = os.path.join('crawler_results', f'result_{i+1}')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            crawl_page(result['link'], output_dir)
        
        print(f"All search results processed and saved in 'crawler_results' folder")
    else:
        print("No search results found")

if __name__ == "__main__":
    main()
