from flask import Flask
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
import os
from attendance import ab as attendance_bp
from performance import pb as performance_bp
#from leaves import lb as leaves_bp
from models import db
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


db_role = os.getenv('DB_ROLE', 'admin')

# Configure your database URI
if db_role == 'employee':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://employee:employee@db:3306/employee_management_system'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:mthree@db:3306/employee_management_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, to disable warnings

# Initialize the database with the app
db.init_app(app)
# Register the attendance blueprint
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(performance_bp, url_prefix='/performance')
#app.register_blueprint(leaves_bp, url_prefix='/leaves')

@app.route('/')
def hello():
    return "work!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all tables (if they don't exist)
    app.run(debug=True, host='0.0.0.0', port=5000)
