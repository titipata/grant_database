import os
import lxml
from lxml import html
import requests


def download_award_links(url="https://www.nsf.gov/awardsearch/"):
    """
    Download all award links from NSF award page
    """
    page = requests.get(url + 'download.jsp')
    tree = html.fromstring(page.content)
    awards_links = tree.xpath('//div[@class="downloadcontent"]//p[@align="center"]//a/@href')
    awards_links = list(map(lambda l: url+l, awards_links))
    return awards_links

if __name__ == '__main__':
    awards_links = download_award_links() # get all award links
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'nsf_awards.txt'), mode='w') as f:
        for link in awards_links:
            f.write("%s\n" % link)
