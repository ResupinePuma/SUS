
from sus.networking import Network
from sus.engines.base_engine import Parser, Publication, BadUrlException
from sus.logger import Logger
from lxml import html, etree
import datetime
import json
import pytz

utc = pytz.UTC

log = Logger('reddit')

class Reddit(Parser):
    """
    A class used to parse publications from inserted url of reddit.com
    """

    def __init__(self):
        self.parsed_publications = []
        self.base_url = ""
        self.__namespaces = {'atom': 'http://www.w3.org/2005/Atom'}

    def Prepare_url(self, url: str):
        if not "https://www.reddit.com/" in url[:23] or "https://old.reddit.com/" in url[:23] or "https://reddit.com/" in url[:19]:
            raise BadUrlException("Bad url")
        if url[-1] == "/":
            url == url[:-1]
        return url, url

    def Extract_text(self, xpath_results):
        if type(xpath_results) == list:
            result = ' '.join([self.Extract_text(e) for e in xpath_results])
            return result.strip()
        elif type(xpath_results) in [etree._ElementStringResult, etree._ElementUnicodeResult]:
            # it's a string
            return ' '.join(xpath_results)
        else:
            # it's a element
            text = html.tostring(
                xpath_results, encoding="unicode", method='text', with_tail=True)
            text = text.strip().replace('\n\n', '\n')
            return ' '.join(text.split())

    def GetTitle(self, element: object, **kwargs):
        text = self.Extract_text(element.xpath(
            './atom:title', namespaces=self.__namespaces))
        words = text.split(" ")
        sentenses = text.split(".")
        if len(sentenses) > 0:
            text = sentenses[0]
        else:
            text = words[:10]
        return {"title": text}

    def GetContent(self, element: object, **kwargs):
        html_str = self.Extract_text(element.xpath(
            './atom:content', namespaces=self.__namespaces))
        text = self.Extract_text(html.fromstring(html_str))
        return {"content": text}

    def GetPublishedDate(self, element: object, **kwargs):
        time = element.xpath('./atom:published/text()',
                             namespaces=self.__namespaces)[0]
        time = time.split("+")
        time = "+".join([time[0], time[1].replace(":", "")])
        return {"publishedDate": datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=utc)}

    def GetURL(self, element: object, **kwargs):
        e = element.xpath('./atom:link/@href', namespaces=self.__namespaces)[0]
        url = e
        return {"url": url}

    def GetMedia(self, element: object, **kwargs):
        return {"media": []}

    def ParseOne(self, one_publication: object, **kwargs):
        fields = {}
        methods = [
            self.GetTitle,
            self.GetContent,
            self.GetPublishedDate,
            self.GetURL,
            self.GetMedia
        ]
        for m in methods:
            try:
                fields.update(m(one_publication, **kwargs))
            except Exception as ex:
                log.exception(ex)
        id = one_publication.xpath(
            './atom:id/text()', namespaces=self.__namespaces)[0]
        return id, Publication(**fields)

    def Parse(self, url: str, **kwargs):
        limit_time = datetime.datetime.now().replace(
            tzinfo=utc) - datetime.timedelta(hours=int(kwargs.get("time_limit_hours", 24)))
        last_published = datetime.datetime.now().replace(tzinfo=utc)
        count = int(kwargs.get("count", 0))

        last_id = ""
        cur_count = 0

        self.base_url, url = self.Prepare_url(url)

        session = Network()
        headers = session.headers
        while last_published > limit_time and (count == 0 or cur_count < count):
            response_text = None
            curr_last_published = last_published
            for _ in range(3):
                try:
                    log.info(f"Parsing url: {url}/new/.xml?after={last_id}")
                    response = session.get(
                        f"{url}/new/.xml?after={last_id}", timeout=10)
                    if response.status_code == 200 and "application/atom+xml" in response.headers.get("content-type"):
                        response_text = response.content
                        break
                except Exception as ex:
                    log.exception(ex)

            if not response_text:
                raise Exception(f"Can't get html from url {url}")

            elements_root = etree.XML(response_text)
            elements = elements_root.xpath(
                '//atom:entry', namespaces=self.__namespaces)
            log.info(f"Found {len(elements)} publications, parsing...")
            for e in elements:
                last_id, publ = self.ParseOne(e)
                if not publ:
                    continue

                if publ.publishedDate > limit_time and (count == 0 or cur_count < count):
                    self.parsed_publications.append(publ)
                    cur_count += 1
                curr_last_published = min(
                    curr_last_published, publ.publishedDate)
            last_published = curr_last_published
        log.info(f"Returned {len(self.parsed_publications)} publications")
        return self.parsed_publications


def scrab(request):
    eng = Reddit()
    return eng.Parse(**request)
