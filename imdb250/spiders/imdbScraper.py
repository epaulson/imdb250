import scrapy
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

# to run:
# scrapy crawl imdbScraper -a year=2017 -o 2017.json
class ImdbscraperSpider(scrapy.Spider):
    name = "imdbScraper"
    allowed_domains = ["www.imdb.com"]

    def __init__(self, year=None, *args, **kwargs):
        super(ImdbscraperSpider, self).__init__(*args, **kwargs)
        self.year = year if year else '2017'

    # useful but didn't end up using it, instead just generated the 
    # first 5 URLs, since I only want 250 movies
    # https://stackoverflow.com/questions/35819404/imdb-scrapy-get-all-movie-data
    def start_requests(self):
        year = self.year
        urls = [
            'http://www.imdb.com/search/title?year=%s,%s&title_type=feature&sort=moviemeter,asc&view=simple' % (year, year),
           'http://www.imdb.com/search/title?year=%s,%s&title_type=feature&sort=moviemeter,asc&view=simple&page=2&ref_=adv_nxt' % (year, year),
           'http://www.imdb.com/search/title?year=%s,%s&title_type=feature&sort=moviemeter,asc&view=simple&page=3&ref_=adv_nxt' % (year, year),
           'http://www.imdb.com/search/title?year=%s,%s&title_type=feature&sort=moviemeter,asc&view=simple&page=4&ref_=adv_nxt' % (year, year),
           'http://www.imdb.com/search/title?year=%s,%s&title_type=feature&sort=moviemeter,asc&view=simple&page=5&ref_=adv_nxt' % (year, year)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        table = response.xpath('//div[@class="lister-list"]')
        movies = table.xpath('.//div[@class="col-title"]')
        for movie in movies:
            items = movie.xpath('.//span[@title]/a')
            for item in items:
                target = item.xpath('@href').extract_first()
                title = item.xpath('text()').extract_first()
                #print("target is %s" % target)
                fulltarget= response.urljoin(target)
                #print("Full target is %s" % (fulltarget))
                #print("title is %s" % title)
                (_, _, imdbid, rest) = target.split('/')
                #print("imdbid is %s" % (imdbid))
                yield({"title": title, "fulltarget": fulltarget, "imdbid": imdbid})
            pass 
