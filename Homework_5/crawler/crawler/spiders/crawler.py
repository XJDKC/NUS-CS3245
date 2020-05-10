import re
import scrapy
from scrapy.selector import Selector

class GoogleBlogSpider(scrapy.Spider):
        name = "GoogleBlog"
        allowed_domains = ["ai.googleblog.com"]
        start_urls = []

        def __init__(self):
            super(GoogleBlogSpider, self).__init__()

            domain = GoogleBlogSpider.allowed_domains[0]
            prefix = 'https://{}'.format(domain)
            pattern_string = '^%s/\d{4}/\d{2}/?$' % prefix
            self.archive_pattern = re.compile(pattern_string)

            for year in range(2020, 2021):
                for month in range(1, 6):
                    url = '{}/{:d}/{:0>2d}'.format(prefix, year, month)
                    GoogleBlogSpider.start_urls.append(url)
                    self.log('URL: %s' % (url))

            self.log(GoogleBlogSpider.start_urls)

        def parse(self, response):

            if re.match(self.archive_pattern, response.url):
                sel = Selector(response)
                posts = sel.xpath("//*/div[@class='post']")

                for post in posts:
                    blog_url = post.xpath(".//h2[@class='title']/a/@href").extract_first()
                    self.log(blog_url)

                    yield scrapy.Request(url=blog_url,callback=self.parse)
            else:
                # parse blog pages
                title = response.url.split("/")[-1]
                filename = 'data/google-blog-%s' % (title)
                with open(filename, 'wb') as f:
                    f.write(response.body)
                self.log('Saved file %s' % filename)
