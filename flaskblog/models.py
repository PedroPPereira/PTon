from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #for email and pass reset
from flaskblog import db, login_manager, app
from flask_login import UserMixin
#contains all db entities used

#for login authentication
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



#USER entity
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    training_plan = db.Column(db.String(60))
    #opcional attributes
    sex = db.Column(db.String(1))
    age = db.Column(db.Integer)
    objective = db.Column(db.String(25))
    inicial_weight = db.Column(db.Integer)
    #create a relation between the user and the exercise, diet entities
    exercises = db.relationship('Exercise', backref='client', lazy=True)
    diets = db.relationship('Diet', backref='client_diet', lazy=True)

    def get_reset_token(self, expires_sec = 1800): #for email and pass reset
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token): #for email and pass reset
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"






#EXERCISE entity
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    #foreign key that relates to the user entity
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #create a relation between the exercise and the date entities
    dates = db.relationship('Date', backref='day', lazy='dynamic')

    def __repr__(self):
        return f"Exercise('{self.name}')"


#DATE entity
class Date(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    #foreign key that relates to the exercise entity
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)

    def __repr__(self):
        return f"Date('{self.date_posted}','{self.sets}','{self.reps}','{self.weight}')"





#DIET entity
class Diet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.DateTime, nullable=False)
    workout = db.Column(db.Boolean)
    calories = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    #foreign key that relates to the user entity
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Diet('{self.day}', '{self.calories}', '{self.workout}')"


'''
TO UPDATE DATABASE:
erase site.db
refresh models.py, __init_.py
python
from flaskblog import db
from flaskblog.models import User, Date, Exercise, Diet
db.create_all()
'''
