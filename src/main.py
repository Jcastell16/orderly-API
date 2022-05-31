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
from models import Priority, Status, db, User, Profile, Project, Members, Roles, Columntask, Task
from enum import Enum
import datetime
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
        }),400


@app.route('/newproject', methods=['POST'])
@jwt_required()
def new_project():
    name = request.json.get("name", None)
    due_date = request.json.get("due_date")
    description = request.json.get("description")
    members = request.json.get("members")
    if name is None:
        return jsonify("Please provide a valid name."), 400
    else:
        id= get_jwt_identity()
        newProject = Project()
        newProject.user_id = id
        newProject.name = name
        newProject.start_date= datetime.datetime.utcnow()
        newProject.due_date= due_date
        newProject.status = Status.ENCURSO
        newProject.description = description
        db.session.add(newProject)
        db.session.commit()

        ownersmembers = Members()
        ownersmembers.user_id = id
        ownersmembers.project_id= newProject.id
        ownersmembers.rol= Roles.ADMINISTRADOR
        db.session.add(ownersmembers)
        db.session.commit()

    if len(members) > 0:
        for n in members:
            member = Members()
            member.project_id = newProject.id
            memberuser = User.query.filter_by(email=n["email"]).first()
            member.user_id = memberuser.id
            if n["rol"]== "Usuario":
                member.rol = Roles.USUARIO
            else:
                member.rol = Roles.ADMINISTRADOR
            
            db.session.add(member)
            db.session.commit()
        return jsonify({
            "msg": "projecto grupal registrado"
        }), 200
    else:
        return jsonify({
            "msg": "projecto individual registrado"
        }), 200

        
@app.route('/users/<string:email>', methods=['GET'])
def getUsers(email):
    email = f"%{email}%"
    users = User.query.filter(User.email.like(email)).limit(3).all()   
    if users  is None:
        return jsonify({
            "msg":"No hay coincidencia"
        }), 401
    else:
        request = list(map(lambda user:user.serialize(),users))    
        return jsonify(request), 200 


@app.route('/column/<int:project_id>', methods=['GET'])
def getColumn(project_id):
    column = Columntask.query.filter_by(project_id=project_id).all()
    request = list(map(lambda x: x.serialize(), column))
    return jsonify(request), 200

@app.route('/column', methods=["POST"])
def handleNewColumn():
    name = request.json.get("name", None)
    project_id = request.json.get("project_id", None)
    if name is None:
        return jsonify({"msg": "Please provide a valid name."}), 400
    else:
        newColumn = Columntask()
        newColumn.name = name
        newColumn.project_id = project_id
        db.session.add(newColumn)
        db.session.commit()
        return jsonify({"msg": "Column was successfully created."}), 200

@app.route('/column', methods=["DELETE"])
def handleDeleteColumn():
    columnid = request.json.get("id", None)
    if id is None:
        return jsonify({"msg": "Please provide a valid column."}), 400
    DeleteColumn = Columntask.query.filter_by(id=columnid).first()
    if DeleteColumn is None:
        return jsonify({"msg": "The Column does not exist!."}), 401
    tasks = Task.query.filter_by(columntask_id=columnid).all()
    if len(tasks) > 0:
        for n in tasks:
            db.session.delete(n)
    db.session.delete(DeleteColumn)
    db.session.commit()
    return jsonify({"msg": "Column was successfully delete."}), 200

@app.route('/column', methods=["PATCH"])
def handleUpdateColumn():
    id = request.json.get("id", None)
    name = request.json.get("name", None)
    if name is None:
        return jsonify({"msg": "Please provide a valid name."}), 400
    UpdateColumn = Columntask.query.filter_by(id=id).first()
    if UpdateColumn is None:
        return jsonify({"msg": "The Column does not exist!."}), 401
    else:
        UpdateColumn.name = name
        db.session.add(UpdateColumn)
        db.session.commit()
        return jsonify({"msg": "Column was successfully update."}), 200

@app.route('/profiles', methods=['GET'])
@jwt_required()
def getProfiles():
    id = get_jwt_identity()
    projectsId=[]
    profilesId=[]
    projectMember = Members.query.filter_by(user_id = id).all()
    if len(projectMember) > 0:
        
        for member in projectMember:
            projectId = Members.query.filter_by(project_id = member.project_id).all()
            projectsId.append(projectId)
        for project in projectsId:
            for member in project:
                member_profile = Profile.query.filter_by(user_id = member.user_id).first()
                if member_profile.serialize() in profilesId:
                    continue
                else:
                    if member_profile.user_id != id:
                        profilesId.append(member_profile.serialize())
        print(len(profilesId))
        return jsonify(profilesId), 200
    else:
        return jsonify({
            "msg":"No pertenece a ningun projecto"
        }), 200 

@app.route('/projects', methods=['GET'])
@jwt_required()
def getProjects():
    try:
        project_list= []
        id = get_jwt_identity()
        projectMember= Members.query.filter_by(user_id=id).all()
        if len(projectMember) > 0:
            for n in projectMember:
                projects = Project.query.filter_by(id= n.project_id).first()
                project_list.append(projects)
            request= list(map(lambda project:project.serialize(), project_list))
            return jsonify(request), 200
        else:
            return jsonify({"msg":"No pertenece a ningun projecto"}), 200
    except Exception as e:
        print(e)

@app.route('/projectmember/<int:project_id>', methods=['GET'])
@jwt_required()
def getMemberProjects(project_id):
    try:
        members= []
        projectMember= Members.query.filter_by(project_id=project_id).all()
        print(projectMember)
        for n in projectMember:
            users= User.query.filter_by(id=n.user_id).first()
            members.append(users)
        request= list(map(lambda project:project.serialize(), members))
        return jsonify(request), 200

    except Exception as e:
        print(e)

@app.route('/profile', methods=['GET'])
@jwt_required()
def getProfile():
    id = get_jwt_identity()
    profileUser = Profile.query.filter_by(user_id= id).first()
    request = profileUser.serialize()  
    return jsonify(request), 200

@app.route('/membertask', methods=['GET'])
@jwt_required()
def getTasks():
    id = get_jwt_identity()
    ownerTask = Task.query.filter_by(user_id= id, check_in=False).limit(10).all()
    request= list(map(lambda profiles:profiles.serialize(), ownerTask))    
    return jsonify(request), 200

@app.route('/profile', methods=['PUT'])
@jwt_required()
def editProfile():
    id = get_jwt_identity()
    name = request.json.get("name")
    lastname = request.json.get("lastname")
    description = request.json.get("description")
    photo = request.json.get("photo")
    gender = request.json.get("gender")

    profile_update = Profile.query.filter_by(user_id=id).first()
    if profile_update is None:
        return jsonify({"msg":"Profile not found"}), 404
    try:
        if name is not None and lastname is not None:
            profile_update.name = name  
            profile_update.lastname = lastname
        else:
            profile_update.description = description
            profile_update.photo = photo
            profile_update.gender = gender
            db.session.commit()
            return jsonify(profile_update.serialize()), 200
    except Exception as error:
        db.session.rollback()
        return  jsonify(error.args)


@app.route('/task', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
def handle_task():
    user_id = get_jwt_identity()
    if request.method == 'POST':
        project_id = request.json.get("project_id", None)
        name = request.json.get("name", None)
        columntask_id= request.json.get("columntask_id", None)
        if project_id is not None and name is not None and columntask_id is not None:
            task =Task(name = name, user_id = user_id, project_id = project_id, columntask_id= columntask_id, start_date=datetime.datetime.utcnow())
            try:
                db.session.add(task)
                db.session.commit()
                return jsonify(task.serialize()), 200
            except Exception as error:
                db.session.rollback()
                return jsonify(error.args), 500
        else:
            return jsonify({
            "msg": "ocurrio un error"
            }), 400

    if request.method == 'GET':
        tasks = Task.query.all()
        tasks = list(map(lambda task: task.serialize(),tasks))
        return jsonify(tasks),200 
    

    if request.method == 'DELETE':
        id = request.json.get("id", None)
        if id is None:
            return jsonify("ocurrio un error"), 404
        deletetask= Task.query.filter_by(id=id).first()
        if deletetask is None:
            return jsonify("ocurrio un error"), 400
        try:
            db.session.delete(deletetask)
            db.session.commit()
            return jsonify(deletetask.serialize()),200
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args),500
    
    if request.method == 'PUT':
        """
        verificar los datos del objeto
        realizar un query a la base de datos si el id de la tarea existe
        pasar el objeto a la base de datos 
        crear una instancia del objeto a crear
        """
        body= request.json
        print(body)
        if not body.get("id"):
            return jsonify("ocurrio un error"), 400
        if not body.get("name"):
            return jsonify("ocurrio un error"),400
        if not body.get("description"):
            return jsonify("ocurrio un error"), 400
        if not body.get("priority"):
            return jsonify("ocurrio un error"),400
        if not body.get("due_date"):
            return jsonify("ocurrio un error"),400



        update_task= Task.query.filter_by(id=body.get("id")).one_or_none()
        print(update_task)
        update_task.description= body.get("description")
        update_task.name=body.get("name")
        update_task.priority= body.get("priority")
        update_task.due_date= body.get("due_date")
        try:
            db.session.commit()
            return jsonify(update_task.serialize()),201
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)
        

    




# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
