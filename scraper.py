import random, string
from elasticsearch import Elasticsearch, helpers

def gen_text(size):
    return "".join( [random.choice(string.ascii_letters) for i in range(size)] )


data = {}


def __serialize(data):
    for i,v in data.items():
        yield {
            "_index" : "searx_data",
            "_type" : "_doc",
            "_source" : v
        }

def WriteData(es, generator):
    success, _ = helpers.bulk(es, generator)

for i in range(1000):
    doc = {i:{
        "text" : gen_text(1024),
        "source" : "abc"
    }}
    data.update(doc)


es = Elasticsearch("127.0.0.1:9200")

WriteData(es, __serialize(data))