#!/usr/bin/env python3
from flask import *
from client import *
from uuid import uuid4
from functools import wraps

Client = get_client('localhost')

app = Flask(__name__)
app.secret_key = str(uuid4())


# frontend wildcard
@app.route('/front/<path:path>')
def front(path):
    return render_template(path)


# client part
# the index for login
@app.route('/')
def hello_world():
    return render_template('index.html')


# new client registration
@app.route('/new', methods=['POST'])
def new():
    j = request.get_json()
    client = Client.new(j['name'], j['uid'], j['desc'], j['phone'])
    session['id'] = client.id
    return jsonify(client.__dict__)


# get from stu. no.
@app.route('/find/<uid>', methods=['POST', 'GET'])
def find(uid):
    client = Client.get_from_uid(uid)
    session['id'] = client.id
    return jsonify(client.__dict__)


# get client detail from session
def get_the_client():
    _id = session.get('id', None)
    if _id is None:
        abort(406)
    client = Client.get_from_id(_id)
    return client


@app.route('/pendings/client')
def pendings4client():
    client = get_the_client()
    pendings = client.pendings
    if request.is_json:
        return jsonify(pendings)
    return render_template("pendings.html", pendings=pendings)


@app.route('/client/pendings/add', methods=['POST'])
def client_pendings_add():
    client = get_the_client()
    j = request.get_json()
    desc = j['desc']
    is_active = j.get('active', False)
    client.add_pendings(desc, is_active)
    return ""


@app.route('/client/pendings/reactivate/<int:pos>', methods=['POST'])
def client_reactivate(pos):
    client = get_the_client()
    client.reactivate(pos)
    return ""


@app.route('/client/pendings/deactivate/<int:pos>', methods=['POST'])
def client_deactivate(pos):
    client = get_the_client()
    client.deactivate(pos)
    return ""


# administrators
def check_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if True:  # judge whether one is an admin
            pass
        else:
            abort(406)
        return f(*args, **kwargs)
    return wrapper


@app.route('/active')
@check_admin
def active():
    return jsonify(Client.get_active_pendings())


@app.route('/jobs')
@check_admin
def jobs():
    return render_template('active.html', pendings=Client.get_active_pendings())


@app.route('/admin/pendings/reactivate', methods=['POST'])
@check_admin
def admin_reactivate():
    j = request.get_json()
    client = Client.get_from_id(j['id'])
    client.reactivate(j['pos'])
    return ""


@app.route('/admin/pendings/deactivate', methods=['POST'])
@check_admin
def admin_deactivate():
    j = request.get_json()
    client = Client.get_from_id(j['id'])
    client.deactivate(j['pos'])
    return ""


if __name__ == '__main__':
    app.secret_key = "123456"
    app.run(debug=True, host="0.0.0.0")
