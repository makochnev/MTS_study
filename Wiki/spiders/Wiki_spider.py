import scrapy


class WikiSpiderSpider(scrapy.Spider):
    name = "Wiki_spider"
    allowed_domains = ["ru.wikipedia.org"]

    def start_requests(self):
        URL = "https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"
        yield scrapy.Request(url=URL, callback=self.link_parse)

    def link_parse(self, response):
        for link in response.css('div.mw-category-group > ul > li > a::attr(href)').getall():
            yield response.follow(link, callback=self.movie_parse)

        prev_next_pages = response.xpath("*//div[@id='mw-pages']/a/text()").getall()
        prev_next_links = response.xpath("*//div[@id='mw-pages']/a/@href").getall()
        next_page = ''
        for i, page in enumerate(prev_next_pages):
            if page == 'Следующая страница':
                next_page = prev_next_links[i]
                break
        if next_page:
            yield response.follow(next_page, callback=self.link_parse)

    def movie_parse(self, response):
        title = response.xpath("*//span[@class='mw-page-title-main']/text()").get()
        if title.endswith(')'):
            while not title.endswith('('):
                title = title[:-1]
            title = title[:-2]

        director = response.xpath("//*[contains(text(), 'Режиссёр')]/ancestor::tr//span/a/text()").getall()
        if not director:
            director = response.xpath("//*[contains(text(), 'Режиссёр')]/ancestor::tr//span/a/span/text()").getall()
        if not director:
            director = response.xpath("//*[contains(text(), 'Режиссёр')]/ancestor::tr//td/span/text()").getall()
        director = ", ".join(director)

        genre = response.xpath("//*[contains(text(), 'Жанр')]/ancestor::tr//span/a/text()").getall()
        if not genre:
            genre = response.xpath("//*[contains(text(), 'Жанр')]/ancestor::tr//td/span/text()").getall()
        genre = ", ".join(genre)

        release_year = response.xpath("//*[contains(text(), 'Год')]/ancestor::tr//td/a/span/text()").get()
        if not release_year:
            release_year = response.xpath("//*[contains(text(), 'Год')]/ancestor::tr//td/a/text()").get()
        if not release_year:
            release_year = response.xpath("//*[contains(text(), 'Год')]/ancestor::tr//td//span/a/text()").getall()
            release_year = ', '.join(release_year)

        country = response.xpath("//*[contains(text(), 'Стран')]/ancestor::tr//span/a/text()").get()
        if not country:
            country = response.xpath("//*[contains(text(), 'Стран')]/ancestor::tr//a/span/text()").getall()
            country = ', '.join(country)

        yield {
            'title': title,
            'genre': genre,
            'director': director,
            'release_year': release_year,
            'country': country
        }

