from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, RadioField, SelectField, FieldList, FormField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired #validates user input to make sure every input is well written
from flaskblog.models import User




#RegistrationForm
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    #validation to make sure there is no other account with the same username or email
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')





#LoginForm
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')





#UpdateAccountForm
class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')
    #opcional
    sex = RadioField('Sex', choices=[('value','M'),('value_two','F')])
    age = IntegerField('Age')
    objective = SelectField('Objective', choices=[('value_1','Lose weight'),('value_2','Gain muscle'),('value_3','Increase resistance'), ('value_4','Improve health')])
    inicial_weight = IntegerField('Inicial weight')

    #validation to make sure there is no other account with the same username or email
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')






#ExerciseForm
class ExerciseForm(FlaskForm):
    exercise = StringField('Exercise', validators=[DataRequired()])
    sets = IntegerField('Sets', validators=[DataRequired()])
    reps = IntegerField('Reps', validators=[DataRequired()])
    weight = IntegerField('Weight', validators=[DataRequired()])

    class Meta: # No need for csrf token in this child form
        csrf = False


#TrainingPlanForm
class TrainingPlanForm(FlaskForm):
    name = StringField('Training Plan Name', validators=[DataRequired()])
    exercises = FieldList(FormField(ExerciseForm), min_entries=1)
    add_exercise = SubmitField('+')
    submit = SubmitField('Submit')


#TrainingDiaryForm
class TrainingDiaryForm(FlaskForm):
    name = StringField('Training Plan Name', validators=[DataRequired()])
    dates = SelectField('Select Date',choices=[])
    exercises = FieldList(FormField(ExerciseForm), min_entries=1)
    select_date = SubmitField('Submit Date')
    submit = SubmitField('Submit')






#DietDiaryForm
class DietDiaryForm(FlaskForm):
    day = DateField('Day',format="%d/%b/%Y(%a)")
    weight = IntegerField('Weight', validators=[DataRequired()])
    workout = SelectField('Workout?', validators=[InputRequired()], choices=[(True, 'Yes'), (False, 'No')], coerce=lambda x: x == 'True')
    calories = IntegerField('Calories', validators=[DataRequired()])


#ListDiaryForm
class ListDiaryForm(FlaskForm):
    diary_list = FieldList(FormField(DietDiaryForm), min_entries=1)
    submit = SubmitField('Submit')





#RequestResetForm
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first')


#ResetPasswordForm
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Password Reset')
