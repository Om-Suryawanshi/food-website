import sqlite3

# Basic setup
# Connection
def connect():
    conn = sqlite3.connect('database/testdb.db')
    cursor = conn.cursor()
    return conn, cursor

# Modifications needed are 
# Store the password in hashed form and when the user inputs the password compair the hashes from the input to the db (Currently stored in plain text)

def create_users_table():
    conn, cursor = connect()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print('create_users_table Sucessfull')


def create_table_likedMeals():
    conn, cursor = connect()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS likedMeals (
        id INTEGER PRIMARY KEY,
        username TEXT,
        likedMeals TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print('create_table_likedMeals Successfull')


def insert_user(username, password):
    conn, cursor = connect()
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
    ''', (username, password))
    conn.commit()
    conn.close()

def update_password(username, password):
    conn, cursor = connect()
    # Insert code here
    cursor.execute('''
    REPLACE INTO users (username, password) VALUES (?, ?)
''', (username, password))
    conn.commit()
    conn.close()


def insert_liked_Meals(username, likedMeals):
    conn, cursor = connect()
    cursor.execute('''
    INSERT OR REPLACE INTO likedMeals (username, likedMeals) VALUES (?, ?)
    ''', (username, likedMeals))
    conn.commit()
    conn.close()


def remove_liked_Meals(username, idMeal):
    conn, cursor = connect()
    # Delete rows where the username matches and likedMeals contains the specified idMeal
    cursor.execute('''
    DELETE FROM likedMeals
    WHERE username = ? AND likedMeals LIKE ?
    ''', (username, f'%{idMeal}%'))

    conn.commit()
    conn.close()


def get_user(username):
    conn, cursor = connect()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data


def get_liked_Meals_db(username):
    conn, cursor = connect()
    cursor.execute('SELECT * FROM likedMeals WHERE username = ?', (username,))
    user_liked_meals = cursor.fetchall()
    conn.close()
    return user_liked_meals


def get_all_users():
    conn, cursor = connect()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users


def db():
    create_users_table()
    create_table_likedMeals()

# Create tables
db()


# Insert user data
# insert_user('admin', '1234')

# Insert liked meals
# liked_Meals('admin', '123453,231232')
# liked_Meals('admin', '231233')
# liked_Meals('admin', '343234')

# Retrieve user data
# data = get_user('admin')
# print('User-data',data)

# Retrieve liked meals
# liked_meals = get_liked_Meals('admin')
# print('Liked Meals',liked_meals)

# Remove a liked meal
# remove_liked_Meals('admin', '231232')
# remove_liked_Meals('admin', '343234')

# Retrieve updated liked meals
# updated_liked_meals = get_liked_Meals('admin')
# print('Updated Liked meals',updated_liked_meals)
