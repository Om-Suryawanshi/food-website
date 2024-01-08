from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from scripts.db import insert_user, get_user, get_all_users, get_liked_Meals_db, insert_liked_Meals, remove_liked_Meals, insert_user_Data, insert_login_log, get_login_log, get_user_data, insert_reset_token, get_username_from_token, update_password
from scripts.check_input import sanitize_input, is_valid_username
from scripts.geo import fetch_geo
from datetime import datetime, timedelta
import uuid
from urllib.parse import unquote

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
                # user_ip = request.remote_addr
                user_ip = request.access_route[-1]
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
                # user_ip = request.remote_addr
                user_ip = request.access_route[-1]
                # Login Log
                query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone = fetch_geo(user_ip)
                insert_user_Data(username, user_ip, user_country, user_region, user_city,
                                 user_zip, user_latitude, user_longitude, user_timezone, user_isp)
                
                insert_login_log(username, user_ip)
                
                # Cookie
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return "Login failed. Please check your credentials."
        else:
            return "Invalid username or password. Please check your input."

    return render_template('login.html')

@app.route('/reset-password', methods=['POST'])
def reset_password():
    if request.method == 'POST':
        username = request.json.get('username')  # Change to json

        # Check if the username exists in your database
        username = session.get('username')
        if username == 'admin':
            user_data = get_user(username)

            if user_data:
                # Generate a unique token and set its expiration time
                reset_token = str(uuid.uuid4())
                reset_token_expiry = datetime.now() + timedelta(minutes=30)

                # Insert the reset token into the reset_tokens table
                insert_reset_token(username, reset_token, reset_token_expiry)

                # Return the token in the JSON response
                return jsonify({'success': True, 'token': reset_token, 'message': 'Password reset link generated successfully.'})
            else:
                return jsonify({'success': False, 'message': 'User not found.'})


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        # Display the password reset form with the token input field
        token = sanitize_input(request.args.get('token'))
        username = get_username_from_token(token)
        return render_template('reset_password.html', token=token, username=username)

    elif request.method == 'POST':
        token = request.form.get('token')
        password = sanitize_input(request.form.get('password'))

        # Check if the token is valid
        username = get_username_from_token(token)

        if username:
            user_ip = request.access_route[-1]
            # Delete the token and update the password
            # delete_token(token)
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            update_password(username, hashed_password, user_ip)
            user_ip = request.access_route[-1]
                # Login Log
            insert_login_log(username, user_ip)
            query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone = fetch_geo(user_ip)
            insert_user_Data(username, user_ip, user_country, user_region, user_city,
                                 user_zip, user_latitude, user_longitude, user_timezone, user_isp)
            return "Your password is reset"
        else:
            return "Invalid or expired token. Please try again."
        
    return "Invalid token"


# @app.route('/token-test')
# def token_user():
#     try:
#         token = request.args.get('token')
#         decoded_token = unquote(token)  # Decode the URL-encoded token
#         username = get_username_from_token(decoded_token)
#         print(f"Token: {token}, Decoded Token: {decoded_token}, Username: {username}")
#         return jsonify({'username': username})
#     except Exception as e:
#         print(f"Error in token_user route: {e}")
#         return jsonify({'error': str(e)})


@app.route('/<string:username>', methods=['GET'])
def user(username):
    if 'username' in session:
        logged_in_username = session['username']

        if logged_in_username == 'admin':
            username = sanitize_input(username)
            liked_meals = get_liked_Meals_db(username)
            user_data = get_user_data(username)
            user_login_info = get_user(username)
            login_log = get_login_log(username)
            meal = [meal[2] for meal in liked_meals]

            return render_template('admin/user_details.html',
                       username=username,
                       loginDetails=user_login_info,
                       liked_meal_ids=meal,  # Pass the likedMeals data
                       loginLog=login_log,
                       userData=user_data)
            
        return redirect(url_for('account'))  # HTTP 403 Forbidden for non-admin users
    else:
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('login'))


# API
@app.route('/add_meal', methods=['POST'])
def add_meal():
    if 'username' in session:
        username = session['username']

        meal_data = request.json  # Extract JSON data from the request body

        if 'idMeal' in meal_data:
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
    else:
        return jsonify({'error': 'User not logged in'})


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
        users = get_all_users() 
        cookies = request.cookies
        return render_template('admin/admin_dashboard.html', users=users, cookies=cookies)
    else:
        return jsonify({'error':'Not an admin'}), 403 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)