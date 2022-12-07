import scrapy


class SteamGame(scrapy.Item):
    name = scrapy.Field()
    category = scrapy.Field()
    reviews_count = scrapy.Field()
    user_score = scrapy.Field()
    release_date = scrapy.Field()
    developer = scrapy.Field()
    tags = scrapy.Field()
    price = scrapy.Field()
    available_platforms = scrapy.Field()
    __request = scrapy.Field()

    def get_request(self):
        return self.__request

    def set_request(self, req):
        self.__request = req
