import scrapy


class RicardoSpider(scrapy.Spider):
    name = "ricardo"

    def start_requests(self):
        urls = [
            'https://auto.ricardo.ch/de/s/moto',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_overview)

    def parse_overview(self, response):
        article_pages = response.css("a.ric-article::attr(href)")
        overview_pages = response.css("div.ric-pagination a::attr(href)")

        # go to article page
        for article_page in article_pages:
            if article_page is not None:
                yield response.follow(article_page, callback=self.parse_article)

        # go to next overview page
        for overview_page in overview_pages:
            if overview_page is not None:
                yield response.follow(overview_page, callback=self.parse_overview)

    def parse_article(self, response):
        attributes = {
            'title': response.css("div.title h1::text").extract_first(),
            'subtitle': response.css("div.title h4.subtitle::text").extract_first(),
            'performance': int(response.css("div.power div.value::text").extract_first().replace(" PS", "")),
            'mileage': float(response.css("div.mileage div.value::text").extract_first().replace("'", "").replace(" km", "")),
            'registration': response.css("div.registration div.value::text").extract_first(),
            'price': float(response.css("div.price span:last-of-type::text").extract_first().replace("'", "")),
            'description': response.css("#article-description::text").extract_first(),
            'location': response.css("div.seller-info address div span::text").extract_first(),
            'image_urls': response.css("#pictures-collection img.lazy-img::attr(src)").extract(),
        }

        details = response.css(".details-list.section-list")
        for item in details.css("div.item"):
            label = item.css("span.label::text").extract_first()
            value = item.css("span.value::text").extract_first()
            attributes.update({label: value})

        environment = response.css(".environment-details-list.section-list")
        for item in environment.css("div.item"):
            label = item.css("span.label::text").extract_first()
            value = item.css("span.value::text").extract_first()
            attributes.update({label: value})

        yield attributes
