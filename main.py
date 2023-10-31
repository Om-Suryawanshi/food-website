from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from db import insert_user, get_user, get_all_users, get_liked_Meals_db, insert_liked_Meals, remove_liked_Meals
from check_input import sanitize_input, is_valid_username

app = Flask(__name__)
bcrypt = Bcrypt(app)
# Replace with a strong, randomly generated secret key
app.secret_key = 'your_secret_key_here'
app.static_folder = 'static'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/account')
def account():
    if 'username' in session:
        # User is logged in, display their account page
        username = session['username']

        return render_template('account.html', username=username)
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username'))
        password = sanitize_input(request.form.get('password'))

        if username and password:
            # Validate username and password  place it after username if needed - and is_valid_password(password)
            if is_valid_username(username):
                # Check if the username already exists
                existing_user = get_user(username)

                if existing_user:
                    return "Registration failed. Username already exists. <a href='/register'>Try again</a>"

                # If the username is unique and the input is valid, insert the new user
                hashed_password = bcrypt.generate_password_hash(
                    password).decode('utf-8')
                insert_user(username, hashed_password)
                # return "Registration successful. <a href='/login'>Login</a>"
                session['username'] = username  # Set new login data
                return redirect(url_for('index'))

            else:
                return "Invalid username or password. Please check your input."

    return render_template('register.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     session.clear()  # Clear the session data
#     if request.method == 'POST':
#         username = sanitize_input(request.form.get('username'))
#         password = sanitize_input(request.form.get('password'))

#         if username and password:
#             # Validate username and password
#             user_data = get_user(username)

#             if user_data and user_data[2] == password:
#                 # return f"Login successful, welcome {username}!"
#                 session['username'] = username
#                 return redirect(url_for('index'))
#             else:
#                 return "Login failed. Please check your credentials."
#         else:
#             return "Invalid username or password. Please check your input."

#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()  # Clear the session data
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username'))
        password = sanitize_input(request.form.get('password'))

        if username and password:
            # Validate username and password
            user_data = get_user(username)

            if user_data and bcrypt.check_password_hash(user_data[2], password):
                # Successful login
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return "Login failed. Please check your credentials."
        else:
            return "Invalid username or password. Please check your input."

    return render_template('login.html')


# admin
@app.route('/admin/dashboard')
def admin_dashboard():
    users = get_all_users()  # Create a function to retrieve all users from the database
    cookies = request.cookies
    return render_template('admin/admin_dashboard.html', users=users, cookies=cookies)


# Logout
@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('login'))


# API
@app.route('/add_meal', methods=['POST'])
def add_meal():
    meal_data = request.json  # Extract JSON data from the request body

    if 'idMeal' in meal_data:
        username = session.get('username')
        idMeal = meal_data['idMeal']

        # Check if the meal is already liked by the user
        liked_meals = get_liked_Meals_db(username)
        meal = [meal[2] for meal in liked_meals]

        if idMeal in meal:
            return jsonify({'message': 'Meal already liked'})
        else:
            # Insert the liked meal into the database
            insert_liked_Meals(username, idMeal)
            return jsonify({'message': 'Meal added successfully'})
    else:
        return jsonify({'error': 'Invalid request data'})


@app.route('/get_liked_meals', methods=['GET'])
def get_liked_meals():
    # Retrieve liked meals from the data store
    username = session.get('username')
    liked_meals = get_liked_Meals_db(username)

    # Extract the third value from each liked meal
    meal = [meal[2] for meal in liked_meals]

    return jsonify({'likedMeals': meal,
                    'username': username})


if __name__ == '__main__':
    app.run(host='192.168.0.4', port=80, debug=True)
    # app.run(debug=True)
