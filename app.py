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
    post = db.Column(db.String(200),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    comments = db.relationship('Comments', backref='profile', lazy=True)


class Comments(db.Model):
    commentID = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey(
        'profile.id'), nullable=False)
    username = db.Column(db.String(25), nullable=False)
    comment = db.Column(db.String(200), nullable=False)

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
    comments = Comments.query.all()
    return render_template('Admin_profiles.html', profiles=profiles, comments=comments, profile=profile)


@app.route('/posts', methods=['GET', 'POST'])
def view_all_posts():
    profiles = Profile.query.all()
    
    return render_template('viewAllPosts.html', profiles=profiles)

'''


VIEW SINGLE POST


'''

@app.route('/view/post/<int:profileID>', methods=['GET', 'POST'])
def view_post(profileID):
    profiles = Profile.query.all()
    comments = Comments.query.filter(Comments.id == profileID).all()

    #the magic code line (i spent 2 and a half hours troubleshooting this Josh T_T)
    profile = Profile.query.get_or_404(profileID)
    return render_template('viewPost.html', profiles=profiles, profile=profile, comments=comments)

@app.route('/view/post/<int:profileID>/comment', methods=['GET', 'POST'])
def add_comment(profileID):
    
    profiles = Profile.query.all()
    profile = Profile.query.get_or_404(profileID)
    comments = Comments.query.all()
    #comments = Comments.query.get_or_404(commentID)
    if request.method == 'POST':
        new_comment = Comments(
            id=profileID,
            username=request.form.get('username', '').strip(),
            comment=request.form.get('comment', '').strip(),
            
        )
        db.session.add(new_comment)
        db.session.commit()
        
        return redirect(f'/view/post/{profileID}')
    return render_template('add_comment.html', profiles=profiles, profile = profile, comments = comments)
      
        
    







@app.route('/admin/profiles/deleteButton', methods=['POST'])
def admin_profilesDeleteButton():
    try:
        profileId = request.form.get('profileId', '').strip()
        profile_to_delete = Profile.query.filter_by(id=profileId).first()
        if not profile_to_delete:
            error = f"No profiles found with the specified id found."
            profiles = Profile.query.all()
            return render_template('Admin_profiles.html', profiles=profiles, error=error)
        db.session.delete(profile_to_delete)
        db.session.commit()
        return redirect(url_for('Admin_profiles'))
    except Exception as e:
        error = f"Error deleting profile: {str(e)}"
        profiles = Profile.query.all()
        return render_template('Admin_profiles.html', profiles=profiles, error=error)

@app.route('/admin/profiles/edit', methods=['GET', 'POST'])
def admin_profiles_edit():
    if request.method == 'POST':
        profileID = request.form.get('profileId', '')
        

        if not profileID:
            error = f"No profile id provided."
            profiles = Profile.query.all()
            return render_template('admin_profiles.html', profiles=profiles, error=error)

        profileToUpdate = Profile.query.filter_by(id=profileID).first()

        if not profileToUpdate:
            error = f"No profile found to edit with id = {profileID}."
            profiles = Profile.query.all()
            return render_template('admin_profiles.html', profiles=profiles, error=error)

        try:
            profileToUpdate.username = request.form.get(
                'username', profileToUpdate.username)
            profileToUpdate.email = request.form.get(
                'email', profileToUpdate.email)
            profileToUpdate.post = request.form.get(
                'post', profileToUpdate.post)
            db.session.commit()
            return redirect(url_for('admin_profiles'))
        except Exception as e:
            db.session.rollback()
            error = f"Error writing to database file."
            profiles = Profile.query.all()
            return render_template('admin_profiles.html', profiles=profiles, error=error)

    profileId = request.args.get('profileId')

    if not profileId:
        error = f"No profile id provided."
        profiles = Profile.query.all()
        return render_template('admin_profiles.html', profiles=profiles, error=error)

    profileToEdit = Profile.query.filter_by(id=profileID).first()

    if not profileToEdit:
        error = f"No profile found to edit with id = {profileID}"
        profiles = Profile.query.all()
        return render_template('admin_profiles.html', profiles=profiles, error=error)

    return render_template('profileEdit.html', profile=profileToEdit)

@app.route('/admin/profiles/edit/<int:profileID>', methods=['GET', 'POST'])
def edit_post(profileID):
    profile = Profile.query.get_or_404(profileID)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        post = request.form.get('post', '').strip()

        if not username or not email or not post:
            #flash('Username, Email and Post are required.', 'danger')
            return render_template('profileEdit.html', profile=profile, page_type='input')

        profile.username = username
        profile.email = email
        profile.post = post
        db.session.commit()

        #flash('Post updated successfully!', 'success')
        return redirect(url_for('Admin_profiles', profileID=profileID))

    return render_template('profileEdit.html', profile=profile, page_type='input')


