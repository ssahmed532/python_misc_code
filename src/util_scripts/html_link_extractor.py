#
# A Python script to extract all valid hyperlinks found on a given URL.
#
# Based on sample code from the following articles:
#   - https://www.geeksforgeeks.org/extract-all-the-urls-from-the-webpage-using-python/
#   - https://www.thepythoncode.com/article/extract-all-website-links-python
#
# Requires:
#   - bs4
#   - requests
#
#


import sys
import requests
from os.path        import splitext
from urllib.parse   import urlparse, urljoin
from bs4            import BeautifulSoup


IMAGE_EXTS = ['.png', '.jpg', '.jpeg', '.gif']
URL_SEP_CHAR = '/'


internal_urls = set()
external_urls = set()



def get_ext_from_url(url):
    """Return the filename extension from url, or ''."""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext  # or ext[1:] if you don't want the leading '.'


def is_valid_url(url):
    parsed = urlparse(url)

    ext = get_ext_from_url(url)

    # Any URL that points to a file is not considered valid e.g.:
    #   https://10pearls.com/wp-content/uploads/2020/06/peter-hesse-video-post.jpg
    #   https://10pearls.com/wp-content/uploads/2020/06/gdpr-demystified-video-post.jpg
    #
    return (bool(parsed.netloc)
            and bool(parsed.scheme) 
            and (parsed.scheme == 'http' or parsed.scheme == 'https') 
            and not bool(ext))


def get_all_webpage_links(url):
    urls = set()

    domain_name = urlparse(url).netloc
    print("Target URL={}, domain name={}".format(url, domain_name))

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    for a_tag in soup.find_all("a"):
        href = a_tag.get("href")
        print("Debug1: href = {}".format(href))

        if (href == "") or (href is None):
            continue

        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        print("Debug2: href = {}".format(href))

        parsed_href = urlparse(href)
        print("Parsed href={}".format(parsed_href))
        # remove URL GET parameters, URL fragments, etc.
        #href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        #print("Debug3: href = {}".format(href))

        #continue

        if not is_valid_url(href):
            # not a valid URL
            print("ERROR: this URL is not valid: {}".format(href))
            continue

        print("Debug4: href = {}".format(href))

        # make sure that the link ends with the separator char
        if href[-1] != URL_SEP_CHAR:
            href = href + URL_SEP_CHAR

        if href in urls:
            # already in the set
            continue

        if domain_name not in href:
            # external link
            if href not in external_urls:
                print(f"[!] External link: {href}")
                external_urls.add(href)
                urls.add(href)
            continue

        print(f"[*] Internal link: {href}")
        internal_urls.add(href)
        urls.add(href)

    return urls

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python html_link_extractor.py <http://Some/URL>', file=sys.stderr)
        sys.exit(1)

    target_url = sys.argv[1]

    # reqs = requests.get(target_url)
    # soup = BeautifulSoup(reqs.text, "html.parser")

    # print("HTML page text is:")
    # print(reqs.text)


    # urls = []
    # for link in soup.find_all("a"):
    #     print(link.get("href"))
    
    all_links = get_all_webpage_links(target_url)
    print("Total # of links found: {}".format(len(all_links)))
    print(2 * '\n')

    print("All links found on webpage \'{}\':".format(target_url))
    for link in all_links:
        assert link[-1] == URL_SEP_CHAR, "URL must end with separator character"
        print(link)
