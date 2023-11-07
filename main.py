from flask import Flask, render_template, request, redirect, url_for, session, jsonify, redirect
from flask_bcrypt import Bcrypt
from db import insert_user, get_user, get_all_users, get_liked_Meals_db, insert_liked_Meals, remove_liked_Meals, insert_user_Data, insert_login_log, get_login_log, get_user_data
from check_input import sanitize_input, is_valid_username
from geo import fetch_geo

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
                # Hash Password
                hashed_password = bcrypt.generate_password_hash(
                    password).decode('utf-8')
                user_ip = request.remote_addr
                # Login Log
                insert_login_log(username, user_ip)
                # Enable After Live Upload
                query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone = fetch_geo(user_ip)
                insert_user_Data(username, user_ip, user_country, user_region, user_city,
                                 user_zip, user_latitude, user_longitude, user_timezone, user_isp)
                # Create new User
                insert_user(username, hashed_password, user_ip)
                # Cookie
                session['username'] = username  # Set new login data
                return redirect(url_for('index'))

            else:
                return "Invalid username or password. Please check your input."

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()  # Clear the session data
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username'))
        password = sanitize_input(request.form.get('password'))

        if username and password:
            # # Validate username
            user_data = get_user(username)

            # user_data[2] == enc pass
            if user_data and bcrypt.check_password_hash(user_data['password'], password):
                # Successful login
                user_ip = request.remote_addr
                # Login Log
                insert_login_log(username, user_ip)
                # Cookie
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return "Login failed. Please check your credentials."
        else:
            return "Invalid username or password. Please check your input."

    return render_template('login.html')

# Password Reset / Forgot Password 
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        # Display the password reset form with a token input field
        return render_template('reset_password.html', token=request.args.get('token'))

    if request.method == 'POST':
        # Validate the token, check expiration, and update the password
        token = request.form.get('token')
        new_password = request.form.get('new_password')

        # Verify the token (e.g., check it against a database)


# user/admin
@app.route('/user/<string:username>', methods=['GET'])
def user(username):
    if 'username' in session:
        # User is logged in, display their account page
        logged_in_username = session['username']

        if logged_in_username == 'admin':
            username = sanitize_input(username)
            liked_meals = get_liked_Meals_db(username)
            user_data = get_user_data(username)
            user_login_info = get_user(username)
            login_log = get_login_log(username)
            meal = [meal[2] for meal in liked_meals]

            return jsonify({
                'loginDetails': user_login_info,
                'likedMeals': meal,
                'loginLog': login_log,
                'userData': user_data,
            })
        return jsonify({
            'error': 'Not a admin'
        })
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))


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


@app.route('/remove_liked_meals', methods=['POST'])
def remove_liked_meals():
    meal_data = request.json

    if 'idMeal' in meal_data:
        username = session.get('username')
        idMeal = meal_data['idMeal']

        # Check if the meal is already liked by the user
        liked_meals = get_liked_Meals_db(username)
        meal = [meal[2] for meal in liked_meals]

        if idMeal in meal:
            remove_liked_Meals(username, idMeal)
            return jsonify({'message': 'Meal removed Successfully'})
        else:
            return jsonify({'message': 'Meal Not in liked meals'})
    else:
        return jsonify({'error': 'Invalid request data'})
    

# admin
@app.route('/admin/dashboard')
def admin_dashboard():
    username = session.get('username')
    if username == 'admin':
        users = get_all_users()  # Create a function to retrieve all users from the database
        cookies = request.cookies
        return render_template('admin/admin_dashboard.html', users=users, cookies=cookies)
    else:
        return 'Only admin'


if __name__ == '__main__':
    app.run(host='192.168.0.4', port=80, debug=True)
    # app.run(debug=True)