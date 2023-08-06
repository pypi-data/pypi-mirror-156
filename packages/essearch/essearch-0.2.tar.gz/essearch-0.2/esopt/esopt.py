# elasticsearch的初始化

from pprint import pprint
import ijson
from tqdm import tqdm
from elasticsearch import Elasticsearch

# 以下路径本机和服务器中不同
json_path = ["/data2/dengyunlong/wiki_cn_data.json", "D:/My_Apps/BaiduNetdiskDownload/563w_baidubaike.json"
                                                     "/563w_baidubaike.json"]


# 下面服务器中不需要用户名和密码的设置
def es_start(es_url="http://localhost:9200"):
    global es
    es = Elasticsearch([es_url], timeout=3600)


# 创建索引
def create_mapping(index: str):
    body = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "url": {
                    "type": "text"
                },
                "article": {
                    "type": "text",
                    "analyzer": "ik_smart"
                },
                "wiki_id": {
                    "type": "text"
                }
            }
        }
    }
    es.indices.create(index=index, body=body)


# 插入词条
def insert_entry(idx: str, doc: dict):
    es.index(index=idx, body=doc)


# 将json文件转化成elasticsearch接受的doc，并将其全部插入elasticsearch中
def json_to_doc(source: str, index: str):
    print("source:          ", source)
    with open(source, 'r', encoding='utf-8') as f:
        item_list = list(ijson.items(f, ''))[0]
        for item in tqdm(item_list):
            item_dict = {"wiki_id": item[0], "title": item[1], "url": item[2], "article": item[3]}
            insert_entry(index, item_dict)


def search_entry(index: str, query: str, min_score=0.0, fields=None, source_includes=None, size=10):
    if source_includes is None:
        source_includes = ['title', 'article', 'wiki_id', 'url']
    if fields is None:
        fields = ['title^5', 'article']
    res_list = []
    resp = None
    if index == 'wiki_cn_new':
        resp = es.search(index=index, min_score=min_score, source_includes=source_includes, size=size,
                         query={
                             "multi_match": {
                                 "query": query,
                                 "analyzer": "ik_max_word",
                                 "fields": fields
                             }
                         })
    elif index == 'wiki_cn':
        resp = es.search(index=index, min_score=min_score, source_includes=source_includes, size=size,
                         query={
                             "multi_match": {
                                 "query": query,
                                 "analyzer": "standard",
                                 "fields": fields
                             }
                         })
    for res in resp['hits']['hits']:
        res_list.append(res['_source'])
    return res_list


if __name__ == '__main__':
    es_start()
    create_mapping('wiki_cn_new')
    json_to_doc(json_path[0], 'wiki_cn_new')
    pprint(search_entry(index='wiki_cn_new', query='上海市的语言', source_includes=['title'], min_score=0))
