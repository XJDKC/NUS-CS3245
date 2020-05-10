import re
import scrapy
from scrapy.selector import Selector
from crawler.items import CrawlerItem
import html2text

class GoogleBlogSpider(scrapy.Spider):
        name = "GoogleBlog"
        allowed_domains = ["ai.googleblog.com", "blog.google"]
        start_urls = []

        def __init__(self):
            super(GoogleBlogSpider, self).__init__()

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
            pattern_string = '^https://blog.google/\S+/\S+/\S+/$'
            self.google_pattern = re.compile(pattern_string)

            GoogleBlogSpider.start_urls.append('https://blog.google')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/chrome/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/android/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/chromebooks/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/google-play/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/wear-os/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/chromecast/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/google-nest/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/google-wifi/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/docs/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/drive/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/gmail/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/pixel/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/pixelbook/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/stadia/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/earth/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/assistant/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/maps/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/search/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/photos/')
            GoogleBlogSpider.start_urls.append('https://blog.google/products/translate/')

            # Add archive pages to start_urls(2020/01-2020/05)
            for year in range(2006, 2021):
                for month in range(1, 13):
                    url = '{}/{:d}/{:0>2d}'.format(prefix, year, month)
                    GoogleBlogSpider.start_urls.append(url)

            self.log(GoogleBlogSpider.start_urls)

        def parse(self, response):
            sel = Selector(response)

            if re.match(self.archive_pattern, response.url):
                # parse archive pages
                posts = sel.xpath("//*/div[@class='post']")

                # parse all posts
                for post in posts:
                    blog_url = post.xpath(".//h2[@class='title']/a/@href").extract_first()
                    yield scrapy.Request(url=blog_url,callback=self.parse)

            elif re.match(self.blog_pattern, response.url):
                # parse blog pages
                item = CrawlerItem()

                post = sel.xpath("//*/div[@class='post']")
                title = post.xpath(".//h2[@class='title']")
                header = post.xpath(".//div[@class='post-header']/div")
                body = post.xpath(".//div[@class='post-body']/div")

                item['url'] = response.url
                item['title'] = title.xpath(".//a/text()").extract_first().strip()
                item['date'] = header.xpath(".//span/text()").extract_first().strip()
                item['authors'] = body.xpath(".//span/text()").extract_first().strip()
                item['content'] = self.converter.handle(body.extract_first().strip())
                item['content'] = item['content'].replace('\n', ' ')
                item['outlinks'] = set()

                urls  = body.xpath(".//*[@href]/@href").extract()
                for url in urls:
                    if self.judge(url):
                        item['outlinks'].add(url)
                        yield scrapy.Request(url=url,callback=self.parse)

                yield item

            elif re.match(self.google_pattern, response.url):
                # parse blog pages from google domain
                item = CrawlerItem()

                title = sel.xpath(".//h1")
                authors = sel.xpath("//*[@class='article-meta__author-name']")
                date = sel.xpath("//*[@class='article-meta__published-at']")
                body = sel.xpath("//*[@class='rich-text']")
                related = sel.xpath("//*[@href]/@href")

                item['outlinks'] = set()

                urls = related.extract()
                for url in urls:
                    if url[0] == '/':
                        url = 'https://blog.google' + url
                        yield scrapy.Request(url=url,callback=self.parse)
                    if self.judge(url):
                        item['outlinks'].add(url)
                        yield scrapy.Request(url=url,callback=self.parse)

                item['url'] = response.url
                item['title'] = title.xpath(".//text()").extract_first().strip()
                item['date'] = date.xpath(".//text()").extract_first().strip().replace('Published', ' ')
                item['authors'] = authors.xpath(".//text()").extract_first()
                item['content'] = ' '.join(body.xpath(".//text()").extract())
                item['authors'] = item['authors'] if item['authors'] else ''
                item['content'] = item['content'].replace('\n', ' ')

                yield item
            else:
                urls = sel.xpath(".//*[@href]/@href").extract()
                for url in urls:
                    if url[0] == '/':
                        url = 'https://blog.google' + url
                        yield scrapy.Request(url=url,callback=self.parse)
                    if self.judge(url):
                        yield scrapy.Request(url=url,callback=self.parse)


        def judge(self, url):
            if re.match(self.archive_pattern, url):
                return True
            elif re.match(self.blog_pattern, url):
                return True
            elif re.match(self.google_pattern, url):
                return True

            return False
