from typing import get_origin
from bs4 import BeautifulSoup
import re
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from PIL import Image
from io import BytesIO
from pathlib import Path

# To download to some other location, change this. Specify absolute path to download in str format.
# The script will create a folder named 'zen_pencils' at specified path and save the files in it.
# Sample download path format-
# Linux -
# DOWNLOAD_PATH = Path("/home/SomeUser/Desktop/Images")
# Windows -
# DOWNLOAD_PATH = Path("C:\Users\SomeUser\Desktop\Images")
DOWNLOAD_PATH = Path(Path.home(), "Downloads")

HEADERS = {
    'authority': 'www.zenpencils.com',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'referer': 'http://www.zenpencils.com/',
    'accept-language': 'en-GB,en;q=0.9',
}

ARCHIVE_URL = 'https://www.zenpencils.com/archives/'


def get_page(url='https://www.zenpencils.com/'):
    '''Gets the raw html page for the given url'''
    try:
        with closing(get(url=url, headers=HEADERS)) as response:
            if(is_good_response(response, 'html')):
                return response.content
            else:
                return None
    except RequestException as e:
        log_error(str(e))


def get_image(url):
    '''This downloads image and returns the bytes in-memory buffer of the response content; containing the image.'''
    try:
        with closing(get(url=url, headers=HEADERS)) as response:
            if(is_good_response(response, 'image')):
                if(response.content):
                    return BytesIO(response.content)
                else:
                    return get_image(url)
            else:
                print('error while fetching image')
                return None
    except RequestException as e:
        log_error(str(e))


def log_error(e):
    '''Prints the error'''
    print(e)


def is_good_response(response, content_type_expected):
    '''Checks if the response is good and the expected content is received'''
    content_type = response.headers['Content-Type'].lower()
    if(content_type.find(content_type_expected) > -1 and response.status_code == 200):
        return True
    else:
        return False


def save_image(comic_url, comic_name, path):
    '''This saves the image found at the given url with the given name'''
    print(comic_url)
    raw_html = get_page(comic_url)
    bs4_html = BeautifulSoup(raw_html, "html.parser")
    comic_pages = bs4_html.find('div', {'id': 'comic'})
    images_list = comic_pages.find_all('img')
    image_IO = []
    for image in images_list:
        img_url = image['src']
        # image['src'] is of format - //img_url. Adding https as prefix for get request to work.
        img_url = 'https:'+img_url
        image_IO.append(Image.open(get_image(img_url)))
    pdf_filename = comic_name+'.pdf'
    image_IO[0].save(f"{path}/{pdf_filename}", "PDF",
                     quality=100, save_all=True, append_images=image_IO[1:])


def main():
    '''Core of the script'''
    archive_url = ARCHIVE_URL
    raw_html = get_page(url=archive_url)
    bs4_html = BeautifulSoup(raw_html, "html.parser")
    comic_page_list = bs4_html.find_all(
        'span', {'class': 'comic-archive-title'})
    # Remove the last link as it is by default the welcome to zenpencils page link
    comic_page_list = comic_page_list[:-1]

    # Create download folder and download images only if there are images to download.
    if comic_page_list:
        download_folder_name = "zen_pencils"
        download_path = Path(DOWNLOAD_PATH, download_folder_name)
        download_path.mkdir(parents=True, exist_ok=True)
        for comic in comic_page_list:
            comic_name = comic.a.text
            # Replace each space occurence with a single underscore
            comic_name = re.sub(' +', '_', comic_name)
            # Remove . or : with
            comic_name = re.sub('[.,:]', '', comic_name)
            # Change case to lower
            comic_name = comic_name.lower()
            comic_url = comic.a['href']
            save_image(comic_url, comic_name, download_path)


if __name__ == '__main__':
    main()
