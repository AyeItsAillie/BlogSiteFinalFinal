from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = 'top-secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profiles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Profile(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(25),nullable=False)
    email = db.Column(db.String(100),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

with app.app_context():
    db.create_all()
    



@app.route('/')
def index():
    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        post = request.form.get('post', '').strip()

    # Validation
        if not username or not email or not post:
            error = "Please fill in all required fields"
            return render_template('profileForm.html', error=error)
        #create new profile in database
        try:
            new_profile = Profile(
            username=username,
            email=email,
            post=post
            )
            db.session.add(new_profile)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error = "An error occured while saving your profile. Please try again."
            return render_template('profileForm.html', error=error)
    
        return render_template(
            'profileSuccess.html',
                username=username,
                email=email,
                post=post,
            )
            
    return render_template('profileForm.html')

@app.route('/admin/profiles')
def admin_profiles():
    profiles = Profile.query.all()
    return render_template('Admin_profiles.html', profiles=profiles)