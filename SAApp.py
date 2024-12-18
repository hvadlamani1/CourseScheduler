from app import create_app, db
from config import Config
from app.main.models import Course
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import session
import identity

app = create_app(Config)
app.jinja_env.globals.update(Auth=identity.web.Auth)  # Useful in template for B2C
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

sso_auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
    
)
@app.shell_context_processor
def make_shell_context():
    return {'sa': sqla, 'so': sqlo, 'db': db}

def add_courses(*args, **kwargs):
    query = sqla.select(Course)
    if not db.session.scalars(query).first():
        courses = [{'num':'CS2133','title':'C++', 'description': 'Learn to program in C++!', 'dept' : 'Computer Science'},
                   {'num':'RBE1111','title':'Robats', 'description': 'Robots, but bats!', 'dept' : 'Robotics Engineering'},
                   {'num':'ECE1000','title':'Computer computing', 'description': 'Computers exist and they are cool!', 'dept' : 'Eletrical and Computer Engineering'},
                   {'num':'CS6000','title':'Hardest CS Class', 'description': 'Its really that hard!', 'dept' : 'Computer Science'},
                   {'num':'CS5000','title':'Life as a CS Major', 'description': 'Learn to touch grass!', 'dept' : 'Computer Science'},
                   {'num':'MA6900','title':'Meanings of Numbers in Society', 'description': 'Numbers are not just for math!', 'dept' : 'Applied Mathematics'}
                   ]
        for m in courses:
            db.session.add(Course(courseNum = m['num'], courseTitle = m['title'], courseDescription= m['description'], courseDept = m['dept'] ))
        db.session.commit()

@app.before_request
def initDB(*args, **kwargs):
    db.create_all()
    add_courses()

if __name__ == "__main__":
    app.run(debug=True)

