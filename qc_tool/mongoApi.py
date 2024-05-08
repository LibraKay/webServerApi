import pymongo
import json


class Mongo_Handler:
    def __init__(self, host, port, db, collection):
        self.conn = pymongo.MongoClient(host, port)
        self.db = self.conn.get_database(db)
        self.collection = self.db.get_collection(collection)
        self.total = self.collection.count_documents({})

    def get_total(self):
        return self.total

    def find_all(self):
        collection_data_cursor = self.collection.find()
        dic = self.handle_data(collection_data_cursor)
        return dic

    def page_query(self, query_filer={}, start=1, length=1, sort="_id"):
        page_record_cursor = self.collection.find(query_filer).limit(length).skip(start).sort([(sort, -1)])
        return self.handle_data(page_record_cursor)

    def handle_data(self, record):
        dic = {}
        data_dic = []
        for item in record:
            item["_id"] = str(item["_id"])
            data_dic.append(item)

        dic["data"] = data_dic
        dic["recordsTotal"] = self.total
        dic["recordsFiltered"] = len(data_dic)
        return dic

    def handler_query(self):
        pass

    def insert_one_data(self, dic):
        try:
            self.collection.insert_one(dic)
            self.total = self.collection.count_documents({})
        except Exception as e:
            print(e)
            return False
        return True

    def update_one_data(self, key, dic):
        try:
            query = {key: dic[key]}
            new_value = {"$set": dic}
            self.collection.update_one(query, new_value)
            self.total = self.collection.count_documents({})
        except Exception as e:
            print(e)
            return False
        return True

if __name__ == '__main__':
    host = "192.168.123.240"
    port = 27017
    database = "airtest"
    collection = "autotest"
    mongodb = Mongo_Handler(host, port, database, collection)
    res = mongodb.page_query(query_filer={"sessionid": "96c233721e5c5f4162abbf990bbdac01"} , length=10, start=0)
    print(res)
    res = mongodb.find_all()
    print(res)
    # mongodb.update_one_data("autotest", )
    # mongodb.insert_one_data({"name": "autotest3"})
    # res = mongodb.find_all()
    # print(res)
    print(1)