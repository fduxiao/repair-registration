import pymongo
import datetime
from bson.objectid import ObjectId


def get_client(url='localhost', db_name='pcs', coll_name=None):
    if coll_name is None:
        today = datetime.datetime.now().date()
        coll_name = "%04d-%02d-%02d" % (today.year, today.month, today.day)

    _mongo_client = pymongo.MongoClient(url)
    _db = _mongo_client[db_name]
    client_coll = _db[coll_name]

    class Client:

        mongo_client = _mongo_client
        db = _db
        coll = client_coll

        id: str  # the id in mongo collection
        name: str  # the name of the client
        uid: str  # the unified of the client in real world
        desc: str  # the description
        phone: str  # phone number
        pendings: list  # pendings

        def __init__(self, name, uid, desc, phone, pendings, _id):
            self.name = name
            self.uid = uid
            self.desc = desc
            self.phone = phone
            self.pendings = pendings
            self.id = str(_id)

        @classmethod
        def new(cls, name, uid, desc, phone):
            d = {
                'name': name,
                'uid': uid,
                'desc': desc,
                'phone': phone,
                'pendings': [
                    {
                        'desc': 'start',
                        'created_at': datetime.datetime.now(),
                        'updated_at': datetime.datetime.now(),
                        'active': True,
                    }
                ],
                'finished': False,
                'time': datetime.datetime.now(),
            }
            cls.coll.insert_one(d)
            c = Client(name, uid, desc, phone, d['pendings'], str(d['_id']))
            return c

        @classmethod
        def get_from_uid(cls, uid):
            one = cls.coll.find_one({'uid': uid})
            c = Client(one['name'], one['uid'], one['desc'], one['phone'], one['pendings'], one['_id'])
            return c

        @classmethod
        def get_from_id(cls, _id):
            one = cls.coll.find_one({'_id': ObjectId(_id)})
            c = Client(one['name'], one['uid'], one['desc'], one['phone'], one['pendings'], one['_id'])
            return c

        def deactivate(self, pos):
            self.pendings[pos]['active'] = False
            self.pendings[pos]['updated_at'] = datetime.datetime.now()
            self.coll.find_one_and_update({'_id': ObjectId(self.id)}, {"$set": {"pendings": self.pendings}})

        def reactivate(self, pos):
            self.pendings[pos]['active'] = True
            self.pendings[pos]['updated_at'] = datetime.datetime.now()
            self.coll.find_one_and_update({'_id': ObjectId(self.id)}, {"$set": {"pendings": self.pendings}})

        @classmethod
        def get_works(cls):
            pipeline = [
                {'$match': {'finished': False}},
                {'$unwind': "$pendings"},
                {'$match': {'pendings.active': True}},
                {'$sort': {'pendings.updated_at': -1}},
            ]
            l = []
            for d in cls.coll.aggregate(pipeline):
                d['_id'] = str(d['_id'])
                l.append(d)
            return l
    return Client
