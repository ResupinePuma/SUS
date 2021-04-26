
from sus.networking import Network
from sus.engines.base_engine import Parser, Publication, BadUrlException
from sus.logger import Logger
from lxml import html,etree
import datetime, json
import pytz

utc=pytz.UTC

log = Logger('rss')

class RSS(Parser):
    """
    A class used to parse publications from inserted url

    """
    def __init__(self):
        self.parsed_publications = []
        self.base_url = ""
        self.__namespaces = {'xmlns:atom':'http://www.w3.org/2005/Atom'}

    def Prepare_url(self, url):
        session = Network()
        response = session.head(f"{url}", timeout=10)
        if response.status_code == 200 and ("rss" in response.headers.get("content-type") or "xml" in response.headers.get("content-type")):
            return url, url
        else:
            raise BadUrlException("Maybe not rss feed")
        return url, url

    def Extract_text(self, xpath_results):
        if type(xpath_results) == list:
            # it's list of result : concat everything using recursive call
            result = ' '.join([self.Extract_text(e) for e in xpath_results])
            return result.strip()
        elif type(xpath_results) in [etree._ElementStringResult, etree._ElementUnicodeResult]:
            # it's a string
            return ' '.join(xpath_results)
        else:
            # it's a element
            text = html.tostring(xpath_results, encoding="unicode", method='text', with_tail=True)
            text = text.strip().replace('\n\n', '\n')
            return ' '.join(text.split())

    def GetTitle(self, element : object, **kwargs):
        text = self.Extract_text(element.xpath('./title', namespaces=self.__namespaces))
        words = text.split(" ")
        sentenses = text.split(".")
        if len(sentenses) > 0:
            text = sentenses[0]
        else:
            text = words[:10]        
        return {"title" : text}

    def GetContent(self, element : object, **kwargs):
        html_str = self.Extract_text(element.xpath('./description', namespaces=self.__namespaces))
        text = self.Extract_text(html.fromstring(html_str))
        return {"content" : text}

    def GetPublishedDate(self, element : object, **kwargs):
        time = element.xpath('./pubDate/text()', namespaces=self.__namespaces)[0]
        try:
            time = datetime.datetime.strptime(time, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=utc)
        except:
            time = datetime.datetime.strptime(time, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=utc)
        return {"publishedDate" : time}

    def GetURL(self, element : object, **kwargs):    
        e = element.xpath('./link/text()', namespaces=self.__namespaces)[0]  
        url = e
        return {"url" : url}

    def GetMedia(self, element : object, **kwargs):
        # TODO
        return {"media" : []}

    def ParseOne(self, one_publication : object, **kwargs):
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
        return Publication(**fields)
    
    def Parse(self, url : str, **kwargs):
        limit_time = datetime.datetime.now().replace(tzinfo=utc) - datetime.timedelta(hours=int(kwargs.get("time_limit_hours", 24)))
        last_published = datetime.datetime.now().replace(tzinfo=utc)
        count = int(kwargs.get("count", 0))

        last_id = ""
        cur_count = 0

        self.base_url, url = self.Prepare_url(url)

        session = Network()
        headers = session.headers
        response_text = None
        curr_last_published = last_published
        for _ in range(3):
            try:
                log.info(f"Parsing url: {url}")
                response = session.get(f"{url}", timeout=10)
                if response.status_code == 200 and ("rss" in response.headers.get("content-type") or "xml" in response.headers.get("content-type")):
                    response_text = response.content
                    break
            except Exception as ex:
                log.exception(ex)

        if not response_text:
            raise Exception(f"Can't get rss from url {url}")
        
        elements_root = etree.XML(response_text) #, base_url=url
        elements = elements_root.xpath('//item', namespaces=self.__namespaces)
        log.info(f"Found {len(elements)} publications, parsing...")
        for e in elements:
            publ = self.ParseOne(e)
            if not publ:
                continue
            
            if publ.publishedDate > limit_time and (count == 0 or cur_count < count):
                self.parsed_publications.append(publ)
                cur_count+=1
            curr_last_published = min(curr_last_published, publ.publishedDate)
        log.info(f"Returned {len(self.parsed_publications)} publications")  
        return self.parsed_publications

def scrab(request):
    eng = RSS()
    return eng.Parse(**request)


    
