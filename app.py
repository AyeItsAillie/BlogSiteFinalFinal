from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
app.secret_key = 'top-secret'


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
        if not username or email or not post:
            error = "Please fill in all required fields"
            return render_template('profileForm.html', error=error)
        return render_template(
            'profileSuccess.html',
            username=username,
            email=email,
            post=post
    )
    return render_template('profileForm.html')