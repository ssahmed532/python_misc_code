import requests

from bs4 import BeautifulSoup


PACKT_FREE_LEARNING_URL = r'https://www.packtpub.com/free-learning'


def main() -> None:
    response = requests.get(PACKT_FREE_LEARNING_URL)
    #print(response.status_code)
    #print(response.text)

    book_title = "Not available"
    author = "Not available"
    publication_date = "Not available"
    page_count = (-1)
    book_description = "Not available"

    soup = BeautifulSoup(response.content, "html.parser")
    print(f'Title: {soup.title.text}')

    elements = soup.find_all('h3', class_='product-info__title')
    if elements:
        book_title = elements[0].text.strip()

    elements = soup.find_all('span', class_='product-info__author free_learning__author')
    for element in elements:
        author = element.text.strip()

    elements = soup.find_all('div', class_='free_learning__product_pages_date')
    if elements:
        results = elements[0].find_all_next('span')
        if results:
            publication_date = results[0].text.split(':')[1].strip()

    elements = soup.find_all('div', class_='free_learning__product_pages')
    if elements:
        results = elements[0].find_all_next('span')
        if results:
            page_count = int(results[0].text.split()[1])

    elements = soup.find_all('div', class_='free_learning__product_description')
    if elements:
        results = elements[0].find_all_next('span')
        if results:
            book_description = results[0].text.strip()

    print('PACKT Free eBook details are:')
    print(f'\tTitle:            {book_title}')
    print(f'\tAuthor:           {author}')
    print(f'\tPublication date: {publication_date}')
    print(f'\tPage count:       {page_count}')
    print(f'\tDescription:      {book_description}')
    print()


if __name__ == '__main__':
    main()
