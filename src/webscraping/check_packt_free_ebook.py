import requests

from bs4 import BeautifulSoup


PACKT_FREE_LEARNING_URL = r'https://www.packtpub.com/free-learning'


def main() -> None:
    response = requests.get(PACKT_FREE_LEARNING_URL)
    print(response.status_code)
    print(response.text)
    
    book_title = ""
    author = ""
    publication_date = ""
    page_count = ""
    book_description = ""
    
    soup = BeautifulSoup(response.content, "html.parser")
    print(f'Title: {soup.title.text}')   
    
    first_h3 = soup.select('h3')[0].text
    print(first_h3)
    book_title = first_h3
    
    elements = soup.find_all('span', class_='product-info__author free_learning__author')
    for element in elements:
        author = element.text.strip()

    elements = soup.find_all('span', class_='free_learning__product_pages_date')
    for element in elements:
        publication_date = element.text.strip()
        
    elements = soup.find_all('span', class_='free_learning__product_pages')
    for element in elements:
        page_count = element.text.strip()
        
    elements = soup.find_all('span', class_='free_learning__product_description')
    for element in elements:
        book_description = element.text.strip()
    
    print('PACKT Free eBook details are:')
    print(f'\tTitle:            {book_title}')
    print(f'\tAuthor:           {author}')
    print(f'\tPublication date: {publication_date}')
    print(f'\tPage count:       {page_count}')
    print(f'\tDescription:      {book_description}')
    print()


if __name__ == '__main__':
    main()
