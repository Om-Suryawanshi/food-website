from flask import Flask, render_template, request, redirect, url_for, session, jsonify, redirect, flash
from flask_bcrypt import Bcrypt
from db import insert_user, get_user, get_all_users, get_liked_Meals_db, insert_liked_Meals, remove_liked_Meals, insert_user_Data, insert_login_log
from check_input import sanitize_input, is_valid_username
import requests

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
                # query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone = fetch_geo(user_ip)
                # insert_user_Data(username, user_ip, user_country, user_region, user_city,
                #                  user_zip, user_latitude, user_longitude, user_timezone, user_isp)
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
            # Validate username
            user_data = get_user(username)

            if user_data and bcrypt.check_password_hash(user_data[2], password):
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
# @app.route('/reset_password', methods=['GET', 'POST'])
# def reset_password():
#     if request.method == 'GET':
#         # Display the password reset form with a token input field
#         return render_template('reset_password.html', token=request.args.get('token'))

#     if request.method == 'POST':
#         # Validate the token, check expiration, and update the password
#         token = request.form.get('token')
#         new_password = request.form.get('new_password')

#         # Verify the token (e.g., check it against a database)
#         if is_valid_reset_token(token):
#             # Update the user's password with the new_password
#             username = get_username_by_reset_token(token)
#             update_password(username, new_password)

#             # Invalidate the token (mark it as used)
#             mark_reset_token_as_used(token)

#             flash("Password reset successful. You can now log in with your new password.")
#             return redirect(url_for('login'))
#         else:
#             flash("Invalid or expired token. Please request another password reset.")
#             return redirect(url_for('reset_password'))

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


def fetch_geo(user_ip):
    ip_api_url = f"http://ip-api.com/json/{user_ip}"
    response = requests.get(ip_api_url)
    ip_data = response.json()

    # Extract relevant geolocation data
    query_status = ip_data.get('status')
    user_country = ip_data.get('country')
    user_region = ip_data.get('regionName')
    user_city = ip_data.get('city')
    user_zip = ip_data.get('zip')
    user_latitude = ip_data.get('lat')
    user_longitude = ip_data.get('lon')
    user_isp = ip_data.get('isp')
    user_timezone = ip_data.get('timezone')
    return query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone



# admin
@app.route('/admin/dashboard')
def admin_dashboard():
    users = get_all_users()  # Create a function to retrieve all users from the database
    cookies = request.cookies
    return render_template('admin/admin_dashboard.html', users=users, cookies=cookies)


if __name__ == '__main__':
    app.run(host='192.168.0.4', port=80, debug=True)
    # app.run(debug=True)
