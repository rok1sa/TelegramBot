from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import mysql.connector
import logging
import sys
import flask_login
from flask_sqlalchemy import SQLAlchemy
import psycopg2

print(sys.path)

app = Flask(__name__)
#app = Flask(__name__, template_folder='templates')
CORS(app, origins='*')

# MySQL setup
db_config = {
    "user": "root",
    "password": "PASSWORD",
    "host": "localhost",
    "database": "admin",
    "port": 3306,
}

def connect_to_database():
    try:
        db_connection = mysql.connector.connect(**db_config)
        print('Connected to the database')
        return db_connection
    except mysql.connector.Error as err:
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
        print('Connected to the db in order to implement add_w_t_db func')
        cursor = db_connection.cursor()
        print(f'Adding word to database: {bl_word}')

        insert_query = 'INSERT INTO blacklist (phrase) VALUES (%s)'
        cursor.execute(insert_query, (bl_word,))

        db_connection.commit()
        db_connection.close()
        print(f'Successfully added word: {bl_word}')
    except mysql.connector.Error as err:
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
    except mysql.connector.Error as err:
        logging.error(f'Error removing word from database: {err}')
        return jsonify(error='Error removing word from database'), 500
        #raise
    
def get_blacklist_from_database():
    try:
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
    except mysql.connector.Error as err:
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

@app.route('/')
def index_render():
    return render_template('index.html')

# pdb config  and authorization

PDB_HOST = 'dpg-cnija7ol5elc73fd86jg-a'
PDB_NAME = 'admin_jl2l' # it's the db name, not user name
PDB_USER = 'admin_jl2l_user'
PDB_PASSWORD = 'QoJxbzEakr5pSeXtGVdATWixUGauBO2K'

def connect_to_postgresql():
    try:
        connection = psycopg2.connect(
            dbname=PDB_NAME,
            user=PDB_USER,
            password=PDB_PASSWORD,
            host=PDB_HOST
        )
        print('Connected to the PostgreSQL.')
    except psycopg2.error as e:
        print('Connection to PostgreSQL failed.', e)
    

app.config['DEBUG'] = True

if __name__ == '__main__':
    app.run(debug=True, port=5000)