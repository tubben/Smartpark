# IoT project application BETA

from flask import g, Flask, render_template, request, json
import random
import platform
import sqlite3
from sqlite3 import Error
import urllib.request
import urllib.parse
import random
from random import *


app = Flask(__name__)

DATABASE = "C:\\sqlite3\\mydatabase1.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        #db.row_factory = make_dicts
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

#create connection to local database
def create_connection(db_file):
    global conn 
    conn = None

    try: 
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e: 
        print(e)
    
    return conn 

#commands to create a new table in SQLite3
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def select_all_tasks(conn):
    global spotsAvailable
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM parkingSpots")

    rows = cur.fetchall()
    rowsStr = str(rows)
    a = rowsStr[1:-1]
    a= a.replace("(","")
    a= a.replace(")","")
    a= a.replace("'","")
    a= a.replace(",","")
    a= a.replace(" ","")

    place=1
    
    for i in range(5):
        spots[i]= a[place:-11+place]
        place = place + 2
    spots[5]=a[-1:]
    spotsAvailable=str(spots)
    spotsAvailable= spotsAvailable.replace("[","")
    spotsAvailable= spotsAvailable.replace("]","")
    spotsAvailable= spotsAvailable.replace("'","")
    spotsAvailable= spotsAvailable.replace('"',"")
    spotsAvailable= spotsAvailable.replace(',',"")
    spotsAvailable= spotsAvailable.replace(" ","")
    #spotsColor = spotsColor.split(',')
    #print(spotsColor)
    print(spotsAvailable)

    

#main where connection and create table are called 
def main():
    global database
    global spots
    spots = [None]*6
    database = r"C:\\sqlite3\\mydatabase1.db"

    sql_create_parkingSpots_table = """CREATE TABLE IF NOT EXISTS parkingSpots (
    ID VARCHAR(20),
    Availability VARCHAR(20)); """
    
    conn = create_connection(database)

    if conn is not None:
        create_table(conn,sql_create_parkingSpots_table)
    else: 
        print("Error! Cannot create the database connection")

    with app.app_context():

        sql = "DELETE FROM parkingSpots;"
        #print(sql)

        #execute sql commands
        db = get_db()
        db.execute(sql)
        db.commit()
        

        for i in range(6):
            spotID = i
            newAvailability = 0
            
            sql = "INSERT INTO parkingSpots (ID, Availability) VALUES('%d', '%d')"%(spotID, newAvailability)
            #print(sql)

            #execute sql commands
            db = get_db()
            db.execute(sql)
            db.commit()
    
    

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/")
def standard():
    return render_template("home.html")

@app.route('/post',methods = ["POST"])
def post():
    global besked
    global newAvailability
   
    besked = request.data

   # print(besked)

    beskedStr = str(besked)

    beskedClean = beskedStr.replace('b','')
    beskedClean = beskedClean.replace("'","")

    #print(beskedClean)

    fullList = beskedClean.split(":")

    for i in range(12):
        if i>1 and i%2==0:
            temp = fullList[i]
            spotID = int(temp)
        elif i == 0: 
            temp = fullList[i]
            spotID = int(temp)
        else: 
            temp = fullList[i]
            newAvailability = int(temp)
         #create SQL command

        if i%2==1 or i == 1:
            #print(spotID)
            sql = "UPDATE parkingSpots SET Availability = %d WHERE ID = %d" %(newAvailability, spotID)
            #print(sql)

            #execute sql commands
            db = get_db()
            db.execute(sql)
            db.commit()
    conn = create_connection(database)
    select_all_tasks(conn)

    return ''
    

@app.route('/postet')
def postet():
    
    return besked

@app.route("/monitoring")
def monitoring():

    return render_template("monitoring.html", spotsAvailable=json.dumps(spotsAvailable))


if __name__ == "__main__":
    main()   
    app.run(host='0.0.0.0', port=5050, debug=False)