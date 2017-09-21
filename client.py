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
            for i, p in enumerate(pendings):
                p['pos'] = i
            pendings.sort(key=lambda x: (x['active'], x['updated_at']), reverse=True)
            self.pendings = pendings
            self.id = str(_id)

        @classmethod
        def new(cls, name, uid, desc, phone):
            c = cls.get_from_uid(uid)
            if c is not None:
                c.desc = desc
                c.pendings.append({
                    'desc': desc,
                    'created_at': datetime.datetime.now(),
                    'updated_at': datetime.datetime.now(),
                    'active': True,
                })
                cls.coll.find_one_and_update({'_id': ObjectId(c.id)}, {
                    "$set": {
                        "desc": desc,
                        "pendings": c.pendings,
                    },
                })
                if phone not in c.phone and phone != "":
                    c.phone.append(phone)
                    cls.coll.find_one_and_update({'_id': ObjectId(c.id)}, {
                        "$push": {
                            "phone": phone,
                        },
                    })
                return c
            d = {
                'name': name,
                'uid': uid,
                'desc': desc,
                'phone': [phone],
                'pendings': [
                    {
                        'desc': desc,
                        'created_at': datetime.datetime.now(),
                        'updated_at': datetime.datetime.now(),
                        'active': True,
                    }
                ],
                'time': datetime.datetime.now(),
            }
            cls.coll.insert_one(d)
            c = Client(name, uid, desc, phone, d['pendings'], str(d['_id']))
            return c

        @classmethod
        def get_from_uid(cls, uid):
            one = cls.coll.find({'uid': uid}).sort([('time', pymongo.DESCENDING)]).limit(1)
            if one.count() == 0:
                return None
            one = one[0]
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
            self.coll.find_one_and_update({'_id': ObjectId(self.id)}, {
                "$set": {
                    "pendings."+str(pos)+".active": False,
                    "pendings."+str(pos)+".updated_at": self.pendings[pos]['updated_at'],
                }
            })

        def reactivate(self, pos):
            self.pendings[pos]['active'] = True
            self.pendings[pos]['updated_at'] = datetime.datetime.now()
            self.coll.find_one_and_update({'_id': ObjectId(self.id)}, {
                "$set": {
                    "pendings." + str(pos) + ".active": True,
                    "pendings." + str(pos) + ".updated_at": self.pendings[pos]['updated_at'],
                }
            })

        def add_pendings(self, desc, active=False):
            new_pending = {
                'desc': desc,
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now(),
                'active': active,
            }
            self.pendings.append(new_pending)
            self.coll.find_one_and_update({'_id': ObjectId(self.id)}, {
                "$push": {"pendings": new_pending}
            })

        @classmethod
        def get_active_pendings(cls):
            # now = datetime.datetime.now()
            # one_day = datetime.timedelta(1)
            # start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            # stop = start + one_day

            pipeline = [
                {'$unwind': {"path": "$pendings", 'includeArrayIndex': 'pos'}},
                {'$match': {'pendings.active': True}},
                # {'$match': {"pendings.created_at": {"$gte": start, "$lt": stop}}},
                {'$sort': {'pendings.updated_at': pymongo.ASCENDING}},
            ]
            l = []
            for d in cls.coll.aggregate(pipeline):
                d['_id'] = str(d['_id'])
                l.append(d)
            return l
    return Client
