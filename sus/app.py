from sus.engines import load_engines, engines, base_engine
from sus.logger import Logger
import json, dataclasses, datetime

load_engines()
log = Logger('app')

class Scraper():
    """
    Initnialize sus

    Attributes
    ----------
    time_limit_hours : int
        Time in hours in past until which posts will be analyzed
    id_limit : int
        Id of post when parser needs to be stopped
    count : int
        Number of posts when parser will be stopped

    Methods
    ----------
    parse(url_list)
        Starts parser on every url in list for every engine in engine folder.
        Returns dict {<url from url_list> : <list of Publication dataclasses>}
    
    """
    def __init__(self, **kwargs):
        self.__params = {
            "time_limit_hours" : 24,
            "id_limit" : 0,
            "count" : 0
        }
        self.__params.update(kwargs)


    def parse(self, url_list : list):
        res = {}
        for u in url_list:
            u = u.replace(" ", "")
            for name,eng in engines.items():
                try:
                    request = self.__params
                    request.update({"url" : u})
                    res.update({u : eng.scrab(request)})
                except base_engine.BadUrlException:
                    pass
                except Exception as ex:
                    log.exception(ex)
        return res

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif type(o) == datetime.datetime:
            return o.strftime("%Y-%m-%dT%H:%M:%S%z")
        return super().default(o)

def main():
    i = input('Enter urls from TG, Reddit or RSS channel (delimeter ","): ')
    arr = i.split(",")
    if type(arr) == str: arr = [arr]
    s = Scraper()
    a = s.parse(arr)
    print(json.dumps(a, ensure_ascii=False, cls=EnhancedJSONEncoder))


if __name__ == "__main__":
    main() 