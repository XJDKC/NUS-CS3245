import re
import scrapy
from scrapy.selector import Selector
from crawler.items import CrawlerItem
import html2text

class GoogleBlogSpider(scrapy.Spider):
        name = "GoogleBlog"
        allowed_domains = ["ai.googleblog.com"]
        start_urls = []

        def __init__(self):
            super(GoogleBlogSpider, self).__init__()

            self.parsed = False
            self.parsed_pages = set()

            # setup html2text converter
            self.converter = html2text.HTML2Text()
            self.converter.ignore_links = True
            self.converter.ignore_images = True

            # setup regex pattern
            domain = GoogleBlogSpider.allowed_domains[0]
            prefix = 'https://{}'.format(domain)
            pattern_string = '^%s/\d{4}/\d{2}/?$' % prefix
            self.archive_pattern = re.compile(pattern_string)
            pattern_string = '^%s/\d{4}/\d{2}/\S+$' % prefix
            self.blog_pattern = re.compile(pattern_string)

            # add archive pages to start_urls(2020/01-2020/05)
            for year in range(2020, 2021):
                for month in range(1, 6):
                    url = '{}/{:d}/{:0>2d}'.format(prefix, year, month)
                    GoogleBlogSpider.start_urls.append(url)
                    self.parsed_pages.add(url)

            self.log(GoogleBlogSpider.start_urls)

        def parse(self, response):
            sel = Selector(response)

            if re.match(self.archive_pattern, response.url):
                # parse archive pages
                posts = sel.xpath("//*/div[@class='post']")

                # parse all posts
                for post in posts:
                    blog_url = post.xpath(".//h2[@class='title']/a/@href").extract_first()

                    if not self.parsed:
                        self.parsed = True
                        self.parsed_pages.add(blog_url)
                        yield scrapy.Request(url=blog_url,callback=self.parse)

            elif re.match(self.blog_pattern, response.url):
                # parse blog pages
                item = CrawlerItem()

                post = sel.xpath("//*/div[@class='post']")
                title = post.xpath(".//h2[@class='title']")
                header = post.xpath(".//div[@class='post-header']/div")
                body = post.xpath(".//div[@class='post-body']/div")

                item['title'] = title.xpath(".//a/text()").extract_first().strip()
                item['date'] = header.xpath(".//span/text()").extract_first().strip()
                item['authors'] = body.xpath(".//span/text()").extract_first().strip()
                item['content'] = self.converter.handle(body.extract_first().strip())
                item['urls'] = []

                urls  = body.xpath(".//*[@href]/@href").extract()
                for url in urls:
                    if re.match(self.blog_pattern, url):
                        item['urls'].append(url)
                        if url not in self.parsed_pages:
                            self.parsed_pages.add(url)
                            yield scrapy.Request(url=url,callback=self.parse)

                yield item
