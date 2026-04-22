from flask import Flask,render_template,request,redirect,url_for,flash,session
import mysql.connector
from werkzeug.security import generate_password_hash,check_password_hash
import re
import joblib
import numpy as np
import pandas as pd
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk 
nltk.download('punkt_tab')
#save LR model
model=joblib.load('svm1_model_nlp.pkl')

#save scaler
scaler=joblib.load('tfidf1_vectorizer.pkl')

app = Flask(__name__)
app.secret_key = '9945'

#Database connection
def get_db_connection():
    url = os.getenv("DATABASE_URL")

    # split the URL
    import urllib.parse as urlparse
    urlparse.uses_netloc.append("mysql")
    parsed = urlparse.urlparse(url)

    return mysql.connector.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        port=parsed.port
    )
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/starter_page')
def starter_page():
    return render_template('starter-page.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():

    # 🔒 Login check (same as your code)
    if 'user_id' not in session:
        flash("Please login to access the prediction system", "warning")
        return redirect(url_for('register'))

    prediction = None 

    if request.method == 'POST':
        try:
            # ✅ Step 1: Get input (replace all numeric inputs)
            text = request.form['user_input']

            # ✅ Step 2: Lowercase
            text = text.lower()

            # ✅ Step 3: Remove punctuation
            text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)

            # ✅ Step 4: Tokenization
            tokens = word_tokenize(text)

            # ✅ Step 5: Remove stopwords
            stop_words = set(stopwords.words('english'))
            tokens = [word for word in tokens if word not in stop_words]

            # ✅ Step 6: Lemmatization
            lemmatizer = WordNetLemmatizer()
            tokens = [lemmatizer.lemmatize(word) for word in tokens]

            # ✅ Step 7: Join tokens
            clean_text = " ".join(tokens)

            # ✅ Step 8: Vectorize (instead of scaler)
            X_input = scaler.transform([clean_text])

            # ✅ Step 9: Predict (same style)
            prediction =model.predict(X_input)

            # ✅ Step 10: Final output (same logic style)
            result = prediction[0]

            return render_template('predict.html', prediction=result)

        except Exception as e:
            return f"Error: {e}"

    return render_template('predict.html')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format", "danger")
            return redirect(url_for('register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters", "danger")
            return redirect(url_for('register'))    

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email =%s" ,(email,))
        user=cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash (user['password'],password):
            session['user_id']=user['u_id']
            session['username']=user['u_name']
            return redirect(url_for('index'))    
        else:
            flash("Invalid email or password ","danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u_name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # validation INSIDE POST
        if not u_name.strip():
            flash("Username is required", "danger")
            return redirect(url_for('register'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format", "danger")
            return redirect(url_for('register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters", "danger")
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT u_id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            flash("Email already registered", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (u_name, email, password) VALUES (%s, %s, %s)",
            (u_name, email, hashed_password)
        )
        conn.commit()

        cursor.close()
        conn.close()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))

    #  GET request safe
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, port=4000)

