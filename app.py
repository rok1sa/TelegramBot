from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_cors import CORS
import mysql.connector
import logging
import sys
import flask_login
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os

print(sys.path)

app = Flask(__name__)
#app = Flask(__name__, template_folder='templates')
CORS(app, origins='https://telegrambot-krvu.onrender.com/')


user_db = os.getenv('USER')
password_db = os.getenv('PASSWORD')
host_db = os.getenv('HOST')
name_db = os.getenv('DATABASE_NAME')
port_db = os.getenv('PORT')

db_config = {
    "user": user_db,
    "password": password_db,
    "host": host_db,
    "database": name_db,
    "port": port_db
}

def connect_to_database():
    try:
        db_connection = psycopg2.connect(**db_config)
        print('Connected to the database')
        return db_connection
    except psycopg2.Error as err:
        print(f"Error connecting to the database: {err}")
        raise

db_connection = connect_to_database()
if db_connection:
    print('Test Database connection successful')
else:
    print('Test Failed to connect to the database')

##remove and add word to db funcs
def add_word_to_database(bl_word):
    try:
        db_connection = connect_to_database()
        cursor = db_connection.cursor()
        print(f'Adding word to database: {bl_word}')

        insert_query = 'INSERT INTO blacklist (phrase) VALUES (%s)'
        cursor.execute(insert_query, (bl_word,))

        db_connection.commit()
        db_connection.close()
        print(f'Successfully added word: {bl_word}')
    except psycopg2.Error as err:
        print(f'Error adding word to the database: {err}')
        raise  # Re-raise the exception to indicate a critical error

def remove_word_from_database(bl_word):
    try:
        db_connection = connect_to_database()
        cursor = db_connection.cursor()
        print(f'Removing word from the database: {bl_word}')

        delete_query = 'DELETE FROM blacklist WHERE phrase = %s'
        cursor.execute(delete_query, (bl_word,))

        db_connection.commit()
        db_connection.close()
        print(f'Successfully removed word: {bl_word}')
    except psycopg2.Error as err:
        logging.error(f'Error removing word from database: {err}')
        return jsonify(error='Error removing word from database'), 500
        #raise
    
def get_blacklist_from_database():
    tryЖ
        db_connection = connect_to_database()
        if db_connection:
            cursor = db_connection.cursor()
            cursor.execute('SELECT phrase FROM blacklist')
            print('cursor was executed')
            blacklist = [row[0] for row in cursor.fetchall()]
            db_connection.close()
            print('Blacklist:', blacklist)  # Print the fetched blacklist
            return blacklist
        else:
            print('Database connection failed.')
            return []
    except Exception as e:
        print('An error occurred while fetching blacklist:', e)
        return []

# Test get_blacklist_from_database()
#show_blacklist = get_blacklist_from_database()
#print('Blacklist:', show_blacklist)



@app.route('/')
def index():
    # Fetch the blacklist from the database
    blacklist = get_blacklist_from_database()
    #word = "example"
    print('Blacklist:', blacklist)  # Print the fetched blacklist
    return render_template('index.html', blacklist=blacklist)



@app.route('/add_word', methods=['POST', 'GET'])
def add_word():
    try:
        if request.method == 'POST':   
            word = request.form.get('word')
            print('Adding word:', word)
            add_word_to_database(word)
            return jsonify(success=True)
        else:
            print('Request method was not POST')
        return jsonify(error='Invalid request method')
    except Exception as e:
        print('An error occurred:', e)
        return jsonify(error='An error occurred while processing the request')


@app.route('/remove_word', methods=['GET', 'POST'])
def remove_word():
    if request.method == 'POST':
        word = request.form.get('word')
        remove_word_from_database(word)
        return jsonify(success=True)
    return jsonify(error='Invalid request method')

app.logger.setLevel(logging.DEBUG)

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server error: %s', error)
    return render_template('error.html'), 500

logging.basicConfig(level=logging.DEBUG)

def example_index():
    name = 'Example'
    print('Name: ', name)
    return render_template('index.html', name=name)

def remove_item_from_database(item):
    try:
        db_connection = connect_to_database()
        cursor = db_connection.cursor()
        delete_query = 'DELETE FROM blacklist WHERE phrase = %s'
        cursor.execute(delete_query, (item,))
        db_connection.commit()
        db_connection.close()
        print(f'Successfully removed item: {item}')
    except psycopg2.Error as err:
        logging.error(f'Error removing word from database: {err}')
        print(f'Error removing item from the database: {err}')
        raise

@app.route('/remove_item/<item>', methods=['DELETE'])
def remove_item(item):
    remove_item_from_database(item)
    return jsonify(success=True)

remove_item_from_database('test1');

@app.route('/get_blacklist')
def get_blacklist():
    blacklist = get_blacklist_from_database()
    return jsonify(blacklist=blacklist)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/')
def index_render():
    return render_template('index.html')

app.config['DEBUG'] = True

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
