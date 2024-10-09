"""
This piece of code helps to collect research papers corresponding to certain key-words. This makes use of Google Scholar's API to work.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
from datetime import datetime
import scholarly

def scrape_google_scholar(query,output_file,genre):
    """Scrapes Google Scholar for given query and downloads PDFs."""
    if not os.path.exists(genre):
        os.makedirs(genre)
        
    base_url = "https://scholar.google.com/scholar?"
    params = {
        "q": query,
        "hl": "en",
        """
        "as_sdt": "0" - This value is used for a standard search, which returns results based on the search query.
        "as_sdt": "1" - This value is used for a citation search. When you set as_sdt to 1, Google Scholar will search for articles that cite the specified query.
        "as_sdt": "2" - This value is used for a related articles search. Google Scholar will find articles that are related to the specified query based on its understanding of the topic.
        """
        "as_sdt": "2", 
        "as_ylo": "2014",  # Adjust year range as needed
        "as_vis": "1"
    }

    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Prepare CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Link', 'Title', 'Abstract', 'Publication Date', 'PDF Available', 'Citation'])
        
        # Find all paper divs
        paper_divs = soup.find_all('div', class_='gs_r gs_or gs_scl')
        
        for paper_div in paper_divs:
            # Extract link
            link_elem = paper_div.find('h3', class_='gs_rt').find('a')
            link = link_elem['href'] if link_elem else "Link not found"
            
            # Extract title
            title_elem = paper_div.find('h3', class_='gs_rt')
            title = title_elem.text if title_elem else "Title not found"
            
            # Extract abstract
            abstract_elem = paper_div.find('div', class_='gs_rs')
            abstract = abstract_elem.text if abstract_elem else "Abstract not found"
            
            # Extract publication date
            pub_date_elem = paper_div.find('div', class_='gs_a')
            pub_date = pub_date_elem.text if pub_date_elem else "Date not found"
            
            # Check for PDF
            pdf_link = paper_div.find('div', class_='gs_or_ggsm').find('a', href=True)
            pdf_available = "Yes" if pdf_link else "No"
            
            # Write to CSV
            csvwriter.writerow([link, title, abstract, pub_date, pdf_available])
            
            # Download PDF if available
            if pdf_link:
                pdf_url = urljoin(base_url, pdf_link['href'])
                download_pdf(genre,pdf_url, title)
                
def download_pdf(genre,pdf_url, title):
    """Downloads a PDF given its URL and saves it with the paper's title."""
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            # Clean the title to use as filename
            filename = "".join(c if c.isalnum() else "_" for c in title)
            filename = filename[:50] + ".pdf"  # Limit filename length
            filename = os.path.join(genre, filename)
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download PDF for: {title}")
    except Exception as e:
        print(f"Error downloading PDF for {title}: {str(e)}")

if __name__ == "__main__":
    genre = input("Enter the genre: ")
    query = input("Enter the query: ")  
    output_file = f"{genre}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    query_list = open("query_list","a")
    query_list.write(f"{genre}\t{query}\t{datetime.now().strftime('%Y%m%d_%H%M%S')}\n")
    scrape_google_scholar(query, output_file, genre)
    print(f"Results saved to {output_file}")
