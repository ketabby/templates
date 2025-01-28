from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a unique secret key

# Dummy user data
users = {
    'user1': {'password': 'password123', 'name': 'John Doe'},
    'user2': {'password': 'mypassword', 'name': 'Jane Smith'}
}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['name'] = users[username]['name']
            return redirect(url_for('welcome'))
        else:
            return "Invalid username or password!"
    
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', name=session['name'])
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', name=session['name'])
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('name', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)