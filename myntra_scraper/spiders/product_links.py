import scrapy
from scrapy_selenium import SeleniumRequest


class ProductLinksSpider(scrapy.Spider):
    SELECTOR_PRODUCT_LINK = '#desktopSearchResults > div.search-searchProductsContainer.row-base > section > ul > li > a'
    SELECTOR_NEXT_PAGE = '#desktopSearchResults > div.search-searchProductsContainer.row-base > section > div.results-showMoreContainer > ul > li.pagination-next > a'

    name = 'product_links'
    num_of_pages_scraped = 0


    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.url = kwargs.get('url') or 'https://www.myntra.com/men-clothing'
        self.pages = int(kwargs.get('pages') or '1')


    def start_requests(self):
        yield SeleniumRequest(
            url=self.url,
            callback=self.parse
        )


    def parse(self, response):
        image_links = response.css(self.SELECTOR_PRODUCT_LINK)

        for l in image_links:
            url = str(response.urljoin(str(l.attrib['href'])))
            yield { 'product_link': url }

        self.num_of_pages_scraped += 1
        next_page = response.css(self.SELECTOR_NEXT_PAGE)
        if next_page:
            if(self.num_of_pages_scraped < self.pages):
                yield SeleniumRequest(
                    url=str(next_page.attrib['href']),
                    callback=self.parse
                )

