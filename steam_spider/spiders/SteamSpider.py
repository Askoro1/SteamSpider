import scrapy
from SteamSpider.items import SteamGame


def gen_steam_start_urls(terms, pages):
    req_info = [(term, page) for term in terms for page in pages]
    link_base = 'https://store.steampowered.com/search?term={0}&page={1}&ignore_preferences=1&category1=998'
    return list(map(lambda x: (x[0], link_base.format(x[0], x[1])), req_info))
    # Указываем category1=998 в url, чтобы показывались только игры


class SteamspiderSpider(scrapy.Spider):
    name = 'SteamSpider'
    allowed_domains = ['store.steampowered.com']

    def start_requests(self):
        for request, url in gen_steam_start_urls(['survival', 'simulator', 'RPG'], [1, 2]):
            yield scrapy.Request(url=url, callback=self.parse_search_results, flags=[request])

    def parse_search_results(self, response):
        game_urls = response.xpath("//div[@id='search_resultsRows']/a/@href").getall()
        for game_url in game_urls:
            if 'agecheck' not in game_url:
                yield scrapy.Request(url=game_url, callback=self.parse_game_page, flags=response.request.flags)

    def parse_game_page(self, response):
        item = SteamGame()
        item.set_request(response.request.flags[0])
        # Название игры
        item['name'] = response.xpath("//div[@id='appHubAppName']/text()").get()
        if item['name'] is not None:
            item['name'] = item['name'].replace('™', '')
            # Категории (указанные в пути)
            item['category'] = response.xpath("//div[@class='blockbg']/a/text()").extract()[1:]
            # Количество отзывов
            item['reviews_count'] = response.xpath("//div[@class='user_reviews_summary_row']/div[@class='summary column']/span[@class='responsive_hidden']/text()").getall()
            if len(item['reviews_count']) == 1:
                item['reviews_count'] = int(''.join(item['reviews_count'][0].strip()[1:-1].split(',')))
            elif len(item['reviews_count']) == 2:
                item['reviews_count'] = int(''.join(item['reviews_count'][1].strip()[1:-1].split(',')))
            elif len(item['reviews_count']) == 0:
                item['reviews_count'] = 0
            # Средняя оценка пользователей
            item['user_score'] = response.xpath("//div[@class='user_reviews_summary_bar']/div[@class='summary_section']/span[@class='game_review_summary positive']/text()").get()
            if item['user_score'] is None:
                item['user_score'] = response.xpath("//div[@class='user_reviews_summary_bar']/div[@class='summary_section']/span[@class='game_review_summary mixed']/text()").get()
            if item['user_score'] is None:
                item['user_score'] = response.xpath("//div[@class='user_reviews_summary_bar']/div[@class='summary_section']/span[@class='game_review_summary negative']/text()").get()
            if item['user_score'] is None:
                item['user_score'] = "Not Rated Yet"
            # День выхода
            item['release_date'] = response.xpath("//div[@class='release_date']/div[@class='date']/text()").get()
            # Первым условием избегаем ситуаций, когда игра не вышла или не анонсирована, так как во всех release_date есть запятая, разделяющая день-месяц и год
            # Вторым условием убираем все игры, которые вышли после 2000 года
            if item['release_date'].find(',') != -1 and \
                    int(item['release_date'].split(', ')[1]) > 2000:
                # Разработчики
                item['developer'] = response.xpath("//div[@id='developers_list']/a/text()").getall()
                # Метки
                item['tags'] = response.xpath("//div[@class='glance_tags popular_tags']/a/text()").getall()
                item['tags'] = [tag.strip() for tag in item['tags']]
                # Цена в рублях
                # Ниже берём такой длинный path, потому что хотим также обработать ситуацию,
                # когда у игры есть демоверсия - информация про неё занесена в тот же виджет, что и цена
                item['price'] = response.xpath("//div[@class='game_area_purchase_game_wrapper']//div[@class='game_purchase_price price']/text()").get()

                if item['price'] is None:  # Значит, сейчас на игру скидка или она бесплатная
                    item['price'] = response.xpath("//div[@class='game_area_purchase_game_wrapper']//div[@class='discount_original_price']/text()").get()
                if item['price'] is None:  # Значит, игра бесплатная
                    item['price'] = response.xpath("//div[@class='game_area_purchase_game ']//div[@class='game_purchase_price price']/text()").get()
                if item['price'] is not None:  # Возможно, есть ещё какие-то необычные кейсы, которые не были учтены выше
                    item['price'] = item['price'].strip().replace('pуб.', 'P')
                    # Платформы
                    item['available_platforms'] = response.xpath("//div[@class='game_area_purchase_game_wrapper']//div[@class='game_area_purchase_platform']").get()
                    if item['available_platforms'] is None:  # Значит, игра бесплатная
                        item['available_platforms'] = response.xpath("//div[@class='game_area_purchase_game ']//div[@class='game_area_purchase_platform']").get()
                    if item['available_platforms'] is not None:
                        item['available_platforms'] = scrapy.Selector(text=item['available_platforms']).xpath("//span/@class").getall()
                        item['available_platforms'] = [platform.replace('platform_img ', '') for platform in item['available_platforms']]
                        yield item
