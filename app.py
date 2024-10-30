from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'  # Update this line if needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Set a secret key for session management
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Database Models
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Marshmallow Schemas
class TaskSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    category = fields.Str()

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()

tasks_schema = TaskSchema(many=True)
task_schema = TaskSchema()
user_schema = UserSchema()

# Home route
@app.route("/")
def home():
    return "Welcome to the Task Manager API!"

# Task Resource
class TaskResource(Resource):
    def post(self):
        data = request.get_json()
        if not data or 'title' not in data or 'description' not in data or 'category' not in data:
            return {"error": "Invalid input"}, 400
        new_task = Task(
            title=data['title'],
            description=data['description'],
            category=data['category']
        )
        db.session.add(new_task)
        db.session.commit()
        return task_schema.dump(new_task), 201

    def get(self):
        tasks = Task.query.all()
        return tasks_schema.dump(tasks)

# User Registration Resource
class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return {"error": "Invalid input"}, 400
        new_user = User(
            username=data['username'],
            password=data['password']  # Hash this in a real app
        )
        db.session.add(new_user)
        db.session.commit()
        return user_schema.dump(new_user), 201

# User Login Resource
class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return {"error": "Invalid input"}, 400
        user = User.query.filter_by(username=data['username'], password=data['password']).first()
        if user:
            return {"message": "Login successful"}, 200
        return {"error": "Invalid credentials"}, 401

# Add resources to the API
api = Api(app)
api.add_resource(TaskResource, '/task')
api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')

if __name__ == "__main__":
    with app.app_context():  # Set up the application context
        db.create_all()  # Create the database tables
    app.run(debug=True)
