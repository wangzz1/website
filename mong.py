from pymongo import MongoClient

conn = MongoClient('127.0.0.1', 27017)
db = conn.ceshi  #连接ceshi数据库，没有则自动创建
my_set = db.test_set #使用test_set集合，没有则自动创建
def a():
    print(1)
# 添加数据
# my_set.insert({"username":"xiaonuo","password":"yuanbaincheng","age":8})
# 或
# my_set.save({"name":"zhangsan","age":18})

#查询全部
if my_set.find_one({"username":"axiaonuo"}) == None:
    print("账号错误")

for i in my_set.find():
    print(i)
#查询name=zhangsan的
#for i in my_set.find({"name":"zhangsan"}):
#    print(i)
#print(my_set.find_one({"name":"zhangsan"}))

#删除name=lisi的全部记录
#my_set.remove({'name': 'zhangsan'})
#for i in my_set.find():
#    print(i)
#删除name=lisi的某个id的记录
#id = my_set.find_one({"name":"zhangsan"})["_id"]
# my_set.remove(id)

#删除集合里的所有记录
# db.users.remove()　