import os
import secrets
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetPasswordForm, RequestResetForm, TrainingPlanForm, TrainingDiaryForm, ListDiaryForm
from flaskblog.models import User, Date, Exercise, Diet #get db models from models.py
from flask_login import login_user, current_user, logout_user, login_required
import random
#contains all url routes used


#############################################################################GENERAL##########################################################################
#HOME url page
@app.route('/')
@app.route('/home')
def home():
    #TO DEVELOP
    return render_template('home.html')


#ABOUT url page
@app.route('/about')
def about():
    return render_template('about.html', title='About')





#REGISTER url page
@app.route('/register', methods = ['GET', 'POST'])
def register():
    #if you are already login there is no need to come back to the Register url page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    #notifies if the registration was succesful or not
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #encrypts user password
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user) #adds user information to the db
        db.session.commit()
        flash(f'Your account has been created! You are now able to login', 'success')
        return redirect(url_for('login')) #sends user to the login page to login
    return render_template('register.html', title='Register', form=form)





#LOGIN url page
@app.route('/login', methods = ['GET', 'POST'])
def login():
    #if you are already login there is no need to come back to the Login url page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        #notifies if the registration was succesful on the home page
        user = User.query.filter_by(email = form.email.data).first()
        #makes sure the email exsits and the password is well written
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for(next_page)) if next_page else redirect(url_for('home')) #sends user to the home page
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


#LOGOUT url page
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))





def save_picture(form_picture): #to save and sesize picture in a default file directory
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture) #resize picture for storage saving
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

#ACCOUNT url page
@app.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit(): #updates email and username if wanted
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.sex = form.sex.data
        current_user.age = form.age.data
        current_user.objective = form.objective.data
        current_user.inicial_weight = form.inicial_weight.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET': #to see the current values of the post on the update page
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.sex.data = current_user.sex
        form.age.data = current_user.age
        form.objective.data = current_user.objective
        form.inicial_weight.data = current_user.inicial_weight
    #gets user profile pic from the static folder
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form = form)








#############################################################################TRAINING_DIARY##########################################################################
def get_current_day():
    dt = datetime.now()
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return dt

#CURRENT_TRAINING_DIARY url page
@app.route('/training_diary/', methods = ['GET', 'POST'])
@login_required
def training_diary():

    if Exercise.query.filter_by(client=current_user).count() == 0: #can only be access if there is a plan
        flash('Your can only access the diary if you have a training plan!','warning')
        return redirect(url_for('current_plan'))

    form = TrainingDiaryForm()
    form.name.data = current_user.training_plan
    exercise = Exercise.query.filter_by(client=current_user).first() #Select all dates available to see progress
    #(n interessa que um exercicio n seja efetuado, porque e sempre inicializado com 0, logo ira existir desde que um seja selecionado)
    form.dates.choices = [(ind_date.id, ind_date.date_posted.strftime("%d/%b/%Y(%a)")) for ind_date in Date.query.filter_by(day=exercise).all()]
    #if there is no exercise update today, add option to select for today
    if Date.query.filter(Date.date_posted==get_current_day()).filter(Date.day==exercise).first() == None:
        form.dates.choices.append([0, get_current_day().strftime("%d/%b/%Y(%a)") + "-TODAY"])


    if form.select_date.data and form.exercises.data != None:
        counter = 0
        for ind_ex in Exercise.query.filter_by(client=current_user).all(): #get all exercises from the training plan
            if counter > 0:
                form.exercises.append_entry()

            if  form.dates.data == '0' and Date.query.filter(Date.date_posted==get_current_day()).filter(Date.day==ind_ex).first() == None:
            #if is to update today, weight and reps must be inserted
                date = Date.query.filter(Date.day==ind_ex).first()
                form.exercises[counter]["weight"].data = 0
                form.exercises[counter]["reps"].data = 0

            else: #if is not today, only show the information
                get_date = Date.query.filter(Date.id==int(form.dates.data)).first() #only to get the day to see
                date = Date.query.filter(Date.day==ind_ex).filter(Date.date_posted==get_date.date_posted).first()
                form.exercises[counter]["weight"].data = date.weight
                form.exercises[counter]["reps"].data = date.reps

            form.exercises[counter]["exercise"].data = ind_ex.name
            form.exercises[counter]["sets"].data = date.sets
            counter = counter + 1


    if form.submit.data: #if the SUBMIT button was pressed and is TODAY
        counter = 0
        for ind_ex in Exercise.query.filter_by(client=current_user).all(): #get all exercises from the training plan

            if form.exercises[counter]["weight"].data == None:
                flash('You cannot edit previous info, for that go to the Edit Diary!','info')
                return redirect(url_for('training_diary'))

            if Date.query.filter(Date.date_posted==get_current_day()).filter(Date.day==exercise).first() != None: #erase all previous information for the current day
                for item in Date.query.filter(Date.date_posted==get_current_day()).filter(Date.day==exercise).all():
                    db.session.delete(item)
                db.session.commit()

            date = Date.query.filter(Date.day==ind_ex).first() #add new date to the db with the new inputs
            new_date = Date(sets = date.sets, reps = int(form.exercises[counter]["reps"].data), weight = int(form.exercises[counter]["weight"].data), day = ind_ex, date_posted=get_current_day())
            db.session.add(new_date)
            db.session.commit()
            counter = counter + 1
        flash('Your training has been updated!','success')
        return redirect(url_for('edit_diary'))

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('training_diary.html', title='Current Training Diary', image_file=image_file, form=form, legend = 'Current Training Diary')






#EDIT_TRAINING_DIARY url page
@app.route('/training_diary/edit', methods = ['GET', 'POST'])
@login_required
def edit_diary():
    form = TrainingDiaryForm()

    form.name.data = current_user.training_plan
    exercise = Exercise.query.filter_by(client=current_user).first() #Select all dates available to see progress
    #(n interessa que um exercicio n seja efetuado, porque e sempre inicializado com 0, logo ira existir desde que um seja selecionado)
    form.dates.choices = [(ind_date.id, ind_date.date_posted.strftime("%d/%b/%Y(%a)")) for ind_date in Date.query.filter_by(day=exercise).all()]


    if  request.method == 'POST' and form.dates.data != 'None' and form.select_date.data:
        counter = 0
        for ind_ex in Exercise.query.filter_by(client=current_user).all(): #get all exercises from the training plan
            if counter > 0:
                form.exercises.append_entry()

            get_day = Date.query.filter(Date.id==form.dates.data).first()
            date = Date.query.filter(Date.day==ind_ex).filter(Date.date_posted==get_day.date_posted).first()

            form.exercises[counter]["exercise"].data = ind_ex.name
            form.exercises[counter]["sets"].data = date.sets
            form.exercises[counter]["weight"].data = date.weight
            form.exercises[counter]["reps"].data = date.reps
            counter = counter + 1


    if form.submit.data:
        counter = 0
        for ind_ex in Exercise.query.filter_by(client=current_user).all(): #get all exercises from the training plan

            get_day = Date.query.filter(Date.id==form.dates.data).first()
            date = Date.query.filter(Date.day==ind_ex).filter(Date.date_posted==get_day.date_posted).first()

            date.sets = form.exercises[counter]["sets"].data
            date.weight = form.exercises[counter]["weight"].data
            date.reps = form.exercises[counter]["reps"].data
            db.session.commit()
            counter = counter + 1
        flash('Your training has been updated!','success')
        return redirect(url_for('training_diary'))

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('training_diary.html', title='Edit Training Diary', image_file=image_file, form=form, legend = 'Edit Training Diary')









#############################################################################TRAINING_PLAN##########################################################################
#NEW_TRAINING_PLAN url page
@app.route('/training_plan/new', methods = ['GET', 'POST'])
@login_required
def training_plan():

    if Exercise.query.filter_by(client=current_user).count(): #if there is already a training plan there is no need for another
        flash('You already have a training plan!','warning')
        return redirect(url_for('current_plan'))

    form = TrainingPlanForm()
    if form.validate_on_submit() and form.submit.data: #if the SUBMIT button was pressed
        current_user.training_plan = form.name.data
        for idx, data in enumerate(form.exercises.data): #iterate every exercise and put it in the db
            exercise = Exercise(name = data["exercise"], client=current_user)
            db.session.add(exercise) #adds user information to the db
            db.session.commit()
            date = Date(sets = data["sets"], reps = data["reps"], weight = data["weight"], day = exercise, date_posted=get_current_day())
            db.session.add(date)
            db.session.commit()
        flash('Your training has been created!','success')
        return redirect(url_for('current_plan'))

    if form.add_exercise.data: #if the ADD EXERCISE button was pressed
        form.exercises.append_entry()
        flash('Added exercise!','info')

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('training_plan.html', title='New Training Plan', image_file=image_file, form=form)




#CURRENT_PLAN url page
@app.route('/training_plan/current', methods = ['GET'])
@login_required
def current_plan():

    if Exercise.query.filter_by(client=current_user).count() == 0: #can only be access if there is a plan
        flash('Your can only access the current plan if you have one!','warning')
        return redirect(url_for('training_plan'))

    form = TrainingPlanForm()
    form.name.data = current_user.training_plan

    counter = 0
    for ind_ex in Exercise.query.filter_by(client=current_user).all(): #gets all exercises from the user
            date = Date.query.filter_by(day = ind_ex).first()
            if counter > 0:
                form.exercises.append_entry()
            form.exercises[counter]["exercise"].data = ind_ex.name
            form.exercises[counter]["sets"].data = date.sets
            form.exercises[counter]["reps"].data = date.reps
            counter = counter + 1

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('current_plan.html', title='Current Training Plan', image_file=image_file, form=form)





#DELETE TRAINING PLAN url page
@app.route('/training_plan/delete', methods = ['POST'])
@login_required
def delete_plan():
    current_user.training_plan = "None"
    exercise = Exercise.query.filter_by(client=current_user).all()
    for item in exercise:
        date = Date.query.filter_by(day = item).all()
        for i in date:
            db.session.delete(i)
        db.session.delete(item)
    db.session.commit()
    flash('Your training plan has been deleted!', 'success')
    return redirect(url_for('training_plan'))











#############################################################################DIET_DIARY##########################################################################
#DIET_DIARY url page
@app.route('/diet_diary', methods = ['GET', 'POST'])
@login_required
def diet_diary():
    form = ListDiaryForm()

    if form.submit.data:
        counter = 0
        for ind_diet in Diet.query.filter_by(client_diet=current_user).all(): #get all exercises from the training plan
            ind_diet.workout = form.diary_list[counter]["workout"].data
            ind_diet.calories = form.diary_list[counter]["calories"].data
            ind_diet.weight = form.diary_list[counter]["weight"].data
            db.session.commit()
            counter = counter + 1
        flash('Your diet diary has been updated!','success')
        return redirect(url_for('diet_diary'))


    elif request.method == 'GET':
        #if there is no diet info for today
        if Diet.query.filter(Diet.day==get_current_day()).filter(Diet.client_diet==current_user).first() == None:
            diet = Diet(day = get_current_day(), workout = False, calories = 0, weight = 0, client_diet = current_user)
            db.session.add(diet)
            db.session.commit()

        counter = 0
        for ind_diet in Diet.query.filter_by(client_diet=current_user).all(): #get all exercises from the training plan
            if counter > 0:
                form.diary_list.append_entry()

            form.diary_list[counter]["day"].data = ind_diet.day.strftime("%d/%b/%Y(%a)")
            form.diary_list[counter]["workout"].data = ind_diet.workout
            form.diary_list[counter]["calories"].data = ind_diet.calories
            form.diary_list[counter]["weight"].data = ind_diet.weight
            counter = counter + 1

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('diet_diary.html', title='Diet Diary', image_file=image_file, form=form)
