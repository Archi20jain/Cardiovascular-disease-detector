from flask import Flask, render_template, request,redirect,flash, session, url_for
import pickle
import numpy as np
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

# Get the absolute path to the current directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

model=pickle.load(open('model.pkl','rb'))


# In-memory user storage (replace with database in production)
users = {}

# Routes
@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        fields = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                  'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
        
        input_data = []
        for field in fields:
            val = request.form.get(field)
            if val == '' or val is None:
                return render_template('Details.html', pred_text=f'Missing input for {field}', percent=0)
            
            if field == 'oldpeak':
                input_data.append(float(val))
            else:
                input_data.append(int(val))  # Make sure all values except 'oldpeak' are ints

        final = [np.array(input_data)]

        # Use the correct method to get prediction probabilities
        prediction = model.predict_proba(final)  # <-- corrected method: `predict_proba`
        output = '{0:.2f}'.format(prediction[0][1] * 100)

        # if float(output) < 50:  # Assuming threshold for "healthy" is < 0.5
        #     return render_template('progress.html', pred='You have a healthy heart \nprobability: {}'.format(output))
        # else:
        #     return render_template('progress.html', pred='You do not have a healthy heart \nprobability: {}'.format(output))
              
        if float(output) < 50:
             return render_template('progress.html', percentage=output, message='You have a healthy heart')
        else:
             return render_template('progress.html', percentage=output, message='You may have a heart condition')

    
    except Exception as e:
        return render_template('Details.html', pred_text=f"Error occurred: {e}", percent=0)


# @app.route('/predict',methods=['POST','GET'])
# def predict():
#     print(request.form)
#     int_features=[int(x) for x in request.form.values()]
#     final=[np.array(int_features)]
#     print(int_features)
#     print(final)
#     prediction=model.predict_probe(final)
#     output='{0:{1}f}'.format(prediction[0][1],2)
    
#     if output==0:
#         return render_template('Details.html',pred='you have a healthy heart {}'.format(output))
#     else:
#         return render_template('Details.html',pred='you do not have a healthy heart {}'.format(output))

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and check_password_hash(users[email]['password'], password):
            session['user'] = email
            return redirect(url_for('user_page'))
        else:
            return render_template('signin.html', invalid='Incorrect email/password')
        
    return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        if password != confirm_password:
            return render_template('signup.html', incorrect='Password do not match')
            
        if email in users:
            return render_template('signup.html', incorrectEmail='Email already exist')
            
        # Store user data
        users[email] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'mobile': mobile,
            'password': generate_password_hash(password)
        }
        
        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('signin'))
        
    return render_template('signUp.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/userPage')
def user_page():
    if 'user' not in session:
        return redirect(url_for('signin'))
    return render_template('userPage.html')

@app.route('/blog')
def blog():
    return render_template('Blog.html')

@app.route('/prescription')
def prescription():
    return render_template('prescription.html')

@app.route('/nearBy')
def nearBy():
    return render_template('nearBy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/consult')
def consult():
    return render_template('consultDoctor.html')

@app.route('/symptoms')
def symptoms():
    return render_template('checkSymptoms.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/details')
def details():
    return render_template('Details.html')


# @app.route('/result')
# def result():
#     percentage = 76  # Replace this with your logic
#     return render_template('progress.html', percentage=percentage)


if __name__ == '__main__':
    app.run(debug=True) 
    
