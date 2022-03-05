from sus.networking import Network
from sus.engines.base_engine import Parser, Publication, BadUrlException
from sus.logger import Logger
from lxml import html, etree
import datetime
import json
import pytz

utc = pytz.UTC

log = Logger('telegram')

class Telegram(Parser):
    """
    A class used to parse publications from inserted url of t.me
    """

    def __init__(self):
        self.parsed_publications = []
        self.base_url = ""

    def Prepare_url(self, url):
        if not "https://t.me/" in url[:13]:
            raise BadUrlException("Bad url")
        while url[-1] == "/":
            url = url[:-1]
        url = url.replace("https://t.me/", "").split("/")
        if "s" in url:
            url.remove("s")
        return f"https://t.me/{url[0]}/", f"https://t.me/s/{url[0]}"

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
            text = html.tostring(
                xpath_results, encoding="unicode", method='text', with_tail=True)
            text = text.strip().replace('\n\n', '\n')
            return ' '.join(text.split())

    def GetTitle(self, element: object, **kwargs):
        text = self.Extract_text(element.xpath(
            './/div[contains(@class, "tgme_widget_message_text js-message_text") or contains(@class, "tgme_widget_message_poll_question")]'))
        words = text.split(" ")
        sentenses = text.split(".")
        if len(sentenses) > 0:
            text = sentenses[0]
        else:
            text = words[:10]
        return {"title": text}

    def GetContent(self, element: object, **kwargs):
        text = self.Extract_text(element.xpath(
            './/div[contains(@class, "tgme_widget_message_text js-message_text") or contains(@class, "tgme_widget_message_poll_question")]'))
        return {"content": text}

    def GetPublishedDate(self, element: object, **kwargs):
        time = element.xpath(
            './/a[@class="tgme_widget_message_date"]/time/@datetime')[0]
        time = time.split("+")
        time = "+".join([time[0], time[1].replace(":", "")])
        return {"publishedDate": datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=utc)}

    def GetURL(self, element: object, **kwargs):
        url = "https://t.me/" + \
            element.xpath(
                './/div[@class="tgme_widget_message js-widget_message"]/@data-post')[0]
        return {"url": url}

    def GetMedia(self, element: object, **kwargs):
        # TODO
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
        id = int(fields.get('url', "0").split('/')[-1])
        try:
            return id, Publication(**fields)
        except:
            return 99999999999999999, None

    def Parse(self, url: str, **kwargs):
        limit_time = datetime.datetime.now().replace(
            tzinfo=utc) - datetime.timedelta(hours=int(kwargs.get("time_limit_hours", 24)))
        limit_id = int(kwargs.get("id_limit", 0))
        count = int(kwargs.get("count", 0))

        last_published = datetime.datetime.now().replace(tzinfo=utc)
        last_id, trigger = 99999999999999999, 0
        cur_count = 0

        self.base_url, url = self.Prepare_url(url)

        session = Network()
        headers = session.headers
        headers.update({"content-type": "application/json",
                       "X-Requested-With": "XMLHttpRequest"})
        while last_published > limit_time and trigger != 99999999999999999:
            response_text = None
            curr_last_published = last_published
            for _ in range(3):
                try:
                    log.info(f"Parsing url: {url}?before={last_id}")
                    response = session.post(
                        f"{url}?before={last_id}", headers=headers, timeout=10)
                    if response.status_code == 200 and "application/json" in response.headers.get("content-type"):
                        response_text = response.text
                        break
                except Exception as ex:
                    log.exception(ex)

            if not response_text:
                raise Exception(f"Can't get html from url {url}")

            elements_root = html.fromstring(
                json.loads(response_text), base_url=url)
            elements = elements_root.xpath(
                '//div[@class="tgme_widget_message_wrap js-widget_message_wrap"]')
            log.info(f"Found {len(elements)} publications, parsing...")
            for e in elements:
                curr_last_id, publ = self.ParseOne(e)
                trigger = curr_last_id
                if not publ:
                    continue

                last_id = min(last_id, curr_last_id)

                if last_id < limit_id and last_id != 99999999999999999:
                    break

                if publ.publishedDate > limit_time and (count == 0 or cur_count < count):
                    self.parsed_publications.append(publ)
                    cur_count += 1
                curr_last_published = min(
                    curr_last_published, publ.publishedDate)
            last_published = curr_last_published
        log.info(f"Returned {len(self.parsed_publications)} publications")
        return self.parsed_publications


def scrab(request):
    eng = Telegram()
    return eng.Parse(**request)
