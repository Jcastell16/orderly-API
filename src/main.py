"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Profile
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
