from flask import Flask, render_template, redirect, url_for, flash , jsonify , session , sessions
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from datetime import timedelta , datetime
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
import secrets
from PIL import Image
import json
import os
import json


load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120))
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile_picture = db.Column(db.String(100), default='default.jpg')
    
    def get_profile_picture_url(self):
        if not self.profile_picture or self.profile_picture == 'default.jpg':
            return url_for('static', filename='profile_pics/default.jpg')
        else:
            return url_for('static', filename=f'profile_pics/{self.profile_picture}')



class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Name"})
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=15)], render_kw={"placeholder": "Phone Number"})
    email = StringField(render_kw={"placeholder": "Email"})
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Save Changes')
    
    
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Name"})
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=15)], render_kw={"placeholder": "Phone Number"})
    email = StringField(render_kw={"placeholder": "Email"})
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder": "Password"})
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField('Register')
    
    def validate_phone_number(self, phone_number):
        existing_user_phone = User.query.filter_by(
            phone_number=phone_number.data).first()
        if existing_user_phone:
            raise ValidationError(
                'That phone number is already registered. Please use a different one.')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


def save_profile_picture(form_picture):
    print(f'Form picture: {form_picture}')
    if isinstance(form_picture, str):
        
        return form_picture

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    
    profile_pics_folder = os.path.join(app.root_path, 'static/profile_pics')
    if not os.path.exists(profile_pics_folder):
        os.makedirs(profile_pics_folder)
    print(f'Picture path: {picture_path}')
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn






class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=5, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def home():
    
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            # session['last_seen'] = datetime.now()
            # login_user(user)
            return redirect(url_for('home_page'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)



@app.route('/profile_edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        try:
            # session['last_seen'] = datetime.now()
            form.populate_obj(current_user) 

           
            if form.profile_picture.data:
                picture_file = save_profile_picture(form.profile_picture.data)
                current_user.profile_picture = picture_file

           
            print(f'Form data: {form.data}')
            print(f'User object: {current_user}')

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile_edit'))

        except Exception as e:
            db.session.rollback()  
            flash('An error occurred while updating the profile. Please try again.', 'danger')
            print(f'Error updating profile: {e}')

    return render_template('profile_edit.html', form=form)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('home_page'))


@app.route('/home')
def home_page():
    with open('static/location.json') as f:
        data = json.load(f)
    return render_template('home.html', data=data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user_username = User.query.filter_by(username=form.username.data).first()
        if existing_user_username:
            flash('That username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(
            name=form.name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            username=form.username.data,
            password=hashed_password
        )
        if form.profile_picture.data:
            print("Form picture before saving:", form.profile_picture.data)
            picture_file = save_profile_picture(form.profile_picture.data)
            print("Picture file after saving:", picture_file)
            new_user.profile_picture = picture_file
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data

        if form.profile_picture:
            picture_file = save_profile_picture(form.profile_picture.data)
            current_user.profile_picture = picture_file

        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form)

@app.route('/api/locations')
def get_locations():
    with open('./static/location.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)



@app.route('/destination/<string:destination_name>')
def destination_page(destination_name):
    with open('./static/location.json', 'r') as f:
        data = json.load(f)

    destination = next((loc for loc in data if loc['name'].lower() == destination_name.lower()), None)

    if destination:
        return render_template('destination_page.html', destination=destination)
    else:
       
        return render_template('error_page.html', message='Destination not found')



with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
