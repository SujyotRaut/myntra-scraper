import json
import scrapy
from scrapy_selenium import SeleniumRequest
from bs4 import BeautifulSoup


class ProductDetailsSpider(scrapy.Spider):
    name = 'product_details'

    SELECTOR_PRODUCT_NAME = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-price-info > h1.pdp-name::text'
    SELECTOR_PRODUCT_BRAND = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-price-info > h1.pdp-title::text'
    SELECTOR_PRODUCT_RATING = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-price-info > div > div > div:nth-child(1)::text'
    SELECTOR_PRODUCT_RATING_COUNT = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-price-info > div > div > div.index-ratingsCount'
    SELECTOR_PRODUCT_CATEGORY = '#mountRoot > div > div > div > main > div.breadcrumbs-container > a:nth-child(7)::text'
    SELECTOR_PRODUCT_DISCOUNT = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-price-info > p.pdp-discount-container > span.pdp-discount'
    SELECTOR_PRODUCT_ORIGINAL_PRICE = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-price-info > p.pdp-discount-container > span.pdp-mrp > s'
    SELECTOR_PRODUCT_DISCOUNTED_PRICE = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-price-info > p.pdp-discount-container > span.pdp-price > strong::text'
    SELECTOR_PRODUCT_TAGS = '#mountRoot > div > div > div > main > div.breadcrumbs-container > a:not(:first-child):not(:last-child)::text'
    SELECTOR_PRODUCT_IMAGES = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.image-grid-container.common-clearfix > div > div > div.image-grid-image::attr(style)'
    SELECTOR_PRODUCT_SIZES = '#sizeButtonsContainer > div.size-buttons-size-buttons > div.size-buttons-tipAndBtnContainer > div.size-buttons-buttonContainer > button > p'
    SELECTOR_PRODUCT_DETAILS = '#mountRoot > div > div > div > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-productDescriptors > div'

    SELECTOR_PRODUCT_REVIEW_CONTAINER = '#detailedReviewsContainer > div.user-review-userReviewWrapper'
    SELECTOR_PRODUCT_REVIEWER_REVIEW = 'div.user-review-main.user-review-showRating > div.user-review-reviewTextWrapper'
    SELECTOR_PRODUCT_REVIEWER_NAME = 'div.user-review-footer.user-review-showRating > div.user-review-left > span:nth-child(1)'
    SELECTOR_PRODUCT_REVIEW_RATING = 'div.user-review-main.user-review-showRating > div.user-review-starWrapper > span'
    SELECTOR_PRODUCT_REVIEW_DATE = 'div.user-review-footer.user-review-showRating > div.user-review-left > span:nth-child(2)'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.product_links = kwargs.get('product_links')


    def start_requests(self):
        if self.product_links:
            with open(self.product_links) as f:
                links = json.loads(f.read())
                for link in links:
                    yield SeleniumRequest(
                        url=str(link['product_link']),
                        callback=self.parse
                    )


    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')

        id = str(response.url).split('/')[-2]
        name = response.css(self.SELECTOR_PRODUCT_NAME).get()
        brand = response.css(self.SELECTOR_PRODUCT_BRAND).get()
        rating = response.css(self.SELECTOR_PRODUCT_RATING).get()
        rating_count = soup.select_one(self.SELECTOR_PRODUCT_RATING_COUNT).text
        sizes = list(map(lambda t: t.text, soup.select(self.SELECTOR_PRODUCT_SIZES)))
        category = response.css(self.SELECTOR_PRODUCT_CATEGORY).get()
        discount = soup.select_one(self.SELECTOR_PRODUCT_DISCOUNT).text
        original_price = soup.select_one(self.SELECTOR_PRODUCT_ORIGINAL_PRICE).text
        discounted_price = response.css(self.SELECTOR_PRODUCT_DISCOUNTED_PRICE).get()
        tags = response.css(self.SELECTOR_PRODUCT_TAGS).getall()
        images = response.css(self.SELECTOR_PRODUCT_IMAGES).getall()
        images = list(map(lambda image: image[23:-3], images))

        # TODO: description
        # description = soup.select_one(self.SELECTOR_PRODUCT_DETAILS).text

        # TODO: colors

        reviews = []
        for review in soup.select(self.SELECTOR_PRODUCT_REVIEW_CONTAINER):
            review_rating = review.select_one(self.SELECTOR_PRODUCT_REVIEW_RATING).text
            review_text = review.select_one(self.SELECTOR_PRODUCT_REVIEWER_REVIEW).text
            reviewer_name = review.select_one(self.SELECTOR_PRODUCT_REVIEWER_NAME).text
            review_date = review.select_one(self.SELECTOR_PRODUCT_REVIEW_DATE).text
            reviews.append({
                'reviewer_name': reviewer_name,
                'review_rating': review_rating,
                'review_date': review_date,
                'review': review_text
            })

        yield {
            'id': id,
            'name': name,
            'brand': brand,
            'sizes': sizes,
            'images': images,
            'rating': rating,
            'rating_count': rating_count,
            'reviews': reviews,
            'category': category,
            'discount': discount,
            # 'description': description,
            'original_price': original_price,
            'discounted_price': discounted_price,
            'tags': tags
        }
