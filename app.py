#!/usr/bin/env python3
from flask import *
from client import *
from uuid import uuid4

Client = get_client('localhost')

app = Flask(__name__)
app.secret_key = str(uuid4())


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/front/<path:path>')
def front(path):
    return render_template(path)


@app.route('/new', methods=['POST'])
def new():
    j = request.get_json()
    client = Client.new(j['name'], j['uid'], j['desc'], j['phone'])
    session['id'] = client.id
    return jsonify(client.__dict__)


@app.route('/find/<uid>', methods=['POST', 'GET'])
def find(uid):
    client = Client.get_from_uid(uid)
    session['id'] = client.id
    return jsonify(client.__dict__)


def get_the_client():
    _id = session.get('id', None)
    if _id is None:
        abort(406)
    client = Client.get_from_id(_id)
    return client


@app.route('/pendings/list')
def pendings_list():
    client = get_the_client()
    return jsonify(client.pendings)


@app.route('/pendings/client')
def pendings4client():
    client = get_the_client()
    return render_template("pendings.html", pendings=client.pendings)


@app.route('/pendings/reactivate/<int:pos>', methods=['POST'])
def reactivate(pos):
    client = get_the_client()
    client.reactivate(pos)
    return ""


@app.route('/pendings/deactivate/<int:pos>', methods=['POST'])
def deactivate(pos):
    client = get_the_client()
    client.deactivate(pos)
    return ""


@app.route('/works')
def works():
    return jsonify(Client.get_works())

if __name__ == '__main__':
    app.secret_key = "123456"
    app.run(debug=True)
