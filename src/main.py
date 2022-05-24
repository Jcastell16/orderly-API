"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import Columntask, Task, User, Profile, Project, db
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('FLASK_APP_KEY')
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200


@app.route("/register", methods=["POST"])
def register_user():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    name = request.json.get("name", None)
    lastname = request.json.get("lastname", None)
    if email is None:
        return jsonify("Please provide a valid email."), 400
    if password is None:
        return jsonify("Please provide a valid password."), 400
    if name is None:
        return jsonify("Please provide a valid name."), 400
    if lastname is None:
        return jsonify("Please provide a valid lastname."), 400
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify("User already exists."), 401
    else:
        newuser = User()
        newuser.email = email
        newuser.password = password
        db.session.add(newuser)
        db.session.commit()

        userid = User.query.filter_by(email=email).first()
        if userid:
            newprofile = Profile()
            newprofile.user_id = userid.id
            newprofile.name = name
            newprofile.lastname = lastname
            db.session.add(newprofile)
            db.session.commit()
            return jsonify({"msg": "User account was successfully created."}), 200
        else:
            return jsonify("User wasn't successfully create"), 401


@app.route('/login', methods=['POST'])
def handle_login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email is not None and password is not None:
        user = User.query.filter_by(
            email=email, password=password).one_or_none()
        if user is not None:
            create_token = create_access_token(identity=user.id)
            return jsonify({
                "token": create_token,
                "user.id": user.id,
                "email": user.email
            }), 200
        else:
            return jsonify({
                "msg": "not found"
            }), 404
    else:
        return jsonify({
            "msg": "error"
        }), 400


@app.route('/column', methods=['GET'])
def getColumn():
    column = Columntask.query.all()
    request = list(map(lambda x: x.serialize(), column))
    return jsonify(request), 200


@app.route('/column', methods=["POST"])
def handleNewColumn():
    name = request.json.get("name", None)
    project_id = request.json.get("project_id", None)
    if name is None:
        return jsonify({"msg": "Please provide a valid name."}), 400
    if project_id is None:
        return jsonify({"msg": "Please provide a valid projectid."}), 400
    else:
        newColumn = Columntask()
        newColumn.name = name
        newColumn.project_id = project_id
        db.session.add(newColumn)
        db.session.commit()
        return jsonify({"msg": "Favorite was successfully created."}), 200

@app.route('/column', methods=["DELETE"])
def handleDeleteColumn():
    id = request.json.get("id", None)
    if id is None:
        return jsonify({"msg": "Please provide a valid Column."}), 400
    DeleteColumn = Columntask.query.filter_by(id=id).first()
    if DeleteColumn is None:
        return jsonify({"msg": "The Column does not exist!."}), 401
    db.session.delete(DeleteColumn)
    db.session.commit()
    return jsonify({"msg": "Favorite was successfully delete."}), 200

@app.route('/column', methods=["PUT"])
def handleUpdateColumn():
    idin = request.json.get("id", None)
    name = request.json.get("name", None)
    if name is None:
        return jsonify({"msg": "Please provide a valid name."}), 400
    UpdateColumn = Columntask.query.filter_by(id=idin).first()
    print(name)
    print(UpdateColumn.project_id)
    if UpdateColumn is None:
        return jsonify({"msg": "The Column does not exist!."}), 401
    else:
        Column = Columntask()
        Column.name = name
        Column.name = UpdateColumn.project_id
        db.session.merge(Column)
        db.session.commit()
        return jsonify({"msg": "Favorite was successfully delete."}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
