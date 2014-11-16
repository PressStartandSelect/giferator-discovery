'''Find valid pages.

To use the script manually::

    python discover.py 0 100 myfile.txt.gz


The file will contain things like:

page:123456
gif:user_chiefs_eberry29_hushfinger_1410003419.436270/400x286/chiefs_eberry29_hushfinger.gif
jpg:user_chiefs_eberry29_hushfinger_1410003419.436270/400x286/chiefs_eberry29_hushfinger_share.jpg
meta:123456
'''
import gzip
import re
import requests
import string
import sys
import time
import random

DEFAULT_HEADERS = {'User-Agent': 'ArchiveTeam'}


class FetchError(Exception):
    '''Custom error class when fetching does not meet our expectation.'''


def main():
    # Take the program arguments given to this script
    # Normal programs use 'argparse' but this keeps things simple
    start_num = int(sys.argv[1])
    end_num = int(sys.argv[2])
    output_filename = sys.argv[3]  # this should be something like myfile.txt.gz

    assert start_num <= end_num

    print('Starting', start_num, end_num)

    gzip_file = gzip.GzipFile(output_filename, 'wb')

    for shortcode in check_range(start_num, end_num):
        # Write the valid result one per line to the file
        line = '{0}\n'.format(shortcode)
        gzip_file.write(line.encode('ascii'))

    gzip_file.close()

    print('Done')


def check_range(start_num, end_num):
    '''Check if page exists.    '''

    for num in range(start_num, end_num + 1):
        shortcode = num
        url = 'http://giferator.easports.com/gif/{0}'.format(shortcode)
        counter = 0

        while True:
            # Try 20 times before giving up
            if counter > 10:
                # This will stop the script with an error
                raise Exception('Giving up!')

            try:
                text = fetch(url)
            except FetchError:
                # The server may be overloaded so wait a bit
                print('Sleeping... If you see this')
                time.sleep(10)
            else:
                if text:
                    yield 'page:{0}'.format(shortcode)
                    yield 'meta:{0}'.format(shortcode)
                    
                    gif = extract_gif(text)
                    jpg = extract_jpg(text)

                    if gif:
                        yield 'gif:{0}'.format(gif)
                    if jpg:
                        yield 'jpg:{0}'.format(jpg)

                break  # stop the while loop

            counter += 1


def fetch(url):
    '''Fetch the URL and check if it returns OK.

    Returns True, returns the response text. Otherwise, returns None
    '''
    print('Fetch', url)
    response = requests.get(url, headers=DEFAULT_HEADERS)

    # response doesn't have a reason attribute all the time??
    print('Got', response.status_code, getattr(response, 'reason'))

    if response.status_code == 200:
        # The item exists
        if not response.text:
            # If HTML is empty maybe server broke
            raise FetchError()

        return response.text
    elif response.status_code == 404:
        # Does not exist
        return
    else:
        # Problem
        raise FetchError()
        
def extract_gif(text):
    '''Return the GIF from the page.'''
    # Search for something like
    # <meta itemprop="image" content="http://prod-mr-user.storage.googleapis.com/assets/user_chiefs_eberry29_hushfinger_1410003419.436270/400x286/chiefs_eberry29_hushfinger.gif?v=5d058b0d67" />
    match = re.search(r'<meta\s+itemprop="image"\s+content="http://prod-mr-user\.storage\.googleapis\.com/assets/([^"]+)\?v=.*" />', text)

    if match:
        return match.group(1)
        
def extract_jpg(text):
    '''Return the preview JPG from the page.'''
    # Search for something like
    # <meta property="og:image" content="http://prod-mr-user.storage.googleapis.com/assets/user_chiefs_eberry29_hushfinger_1410003419.436270/400x286/chiefs_eberry29_hushfinger_share.jpg?v=5d058b0d67" />
    match = re.search(r'<meta\s+property="og:image"\s+content="http://prod-mr-user\.storage\.googleapis\.com/assets/([^"]+)\?v=.*" />', text)

    if match:
        return match.group(1)

if __name__ == '__main__':
    main()
