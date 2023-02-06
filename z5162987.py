#Written by Jonathan Williams (z5162987), March 2020
#Assignment assumptions: You can post the same indicator_id multiple times
import sqlite3
import json
import pandas as pd
import requests
import datetime
from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse


#The database schema is found in line 282, in summary:
#Collection stores indicator_id, indicator_value and creation_time
#Collections may have multiple Collection Entries (indicators) 
#Collection_Entry stores country, date, value and a collection_id to reference the parent Collection

app = Flask(__name__)
api = Api(app,
        default='Collections',
        title='Data Service for World Bank Economic Indicators', 
        description='')

worldBankURL = "http://api.worldbank.org/v2/countries/all/indicators/{}?date=2012:2017&format=json&per_page=1000"

#parser for Question 1
PostParser = reqparse.RequestParser()
PostParser.add_argument('indicator_id', required=True)
#parser for Question 3
GetOrderParser = reqparse.RequestParser()
GetOrderParser.add_argument('order_by', type=inputs.regex('^{([+-]((creation_time)|(indicator)|(id)),)*([+-]((creation_time)|(indicator)|(id)))+}$'))
#parser for Question 6
GetTopBottomParser = reqparse.RequestParser()
GetTopBottomParser.add_argument('q', type=inputs.regex('^[+-]?(([1-9][0-9]?)|100)$'))

#This endpoint handles:
#GET /collections?order_by={+id,+creation_time,+indicator,-id,-creation_time,-indicator}
#POST /collections?indicator_id=NY.GDP.MKTP.CD
@api.route('/collections')
class Collections(Resource):
    #################### Q U E S T I O N   3 ########################
    @api.response(200, 'Successful')
    @api.response(404, 'No collections found')
    @api.doc(description="Question 3 - Retrieve the list of available collections")
    @api.expect(GetOrderParser)
    def get(self):
        args = GetOrderParser.parse_args()
        orderBy = args.get('order_by')
        #transform query parameters into sqlite ORDER BY arguments
        orderBy = orderBy.replace("{", "")
        orderBy = orderBy.replace("}", "")
        orderBy = orderBy.split(",")
        for i in range(0, len(orderBy)):
            if orderBy[i][0] == "+":
                orderBy[i] = orderBy[i].replace("+","")
                orderBy[i] = orderBy[i]+" ASC"
            if orderBy[i][0] == "-":
                orderBy[i] = orderBy[i].replace("-","")
                orderBy[i] = orderBy[i]+" DESC"
            orderBy[i] = orderBy[i].replace("indicator", "indicator_id")
            orderBy[i] = orderBy[i].replace("creation_time", "datetime(creation_time)")
        orderBy = ", ".join(orderBy)
        #connect to db
        conn = sqlite3.connect('z5162987.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys=ON")
        #execute query
        c.execute("SELECT * FROM Collection ORDER BY "+orderBy)
        #if nothing returned by query return 404 error
        if c.rowcount == 0: 
            conn.close()
            return {"message": "There are no collections in the database"}, 404
        #make list of collections
        collectionList = []
        for tup in c.fetchall():
            collection_id, indicator_id, _, creation_time = tup
            curr_collection = {"uri": "/collections/"+str(collection_id),
                          "id": collection_id,
                          "creation_time": creation_time,
                          "indicator": indicator_id
                         }
            collectionList.append(curr_collection)
        conn.close()
        return collectionList, 200


    #################### Q U E S T I O N   1 ########################
    @api.response(201, 'Collections Imported Successfully')
    @api.response(400, 'Invalid parameters')
    @api.response(404, 'Indicator_id not found')
    @api.doc(description="Question 1: Import a collection from the data service")
    @api.expect(PostParser)
    def post(self):
        #get data from the worldbank api
        args = PostParser.parse_args()
        indicator_id = args.get('indicator_id')
        response = requests.get(worldBankURL.format(indicator_id))
        #replace null with "null" to avoid eval's "NameError: name 'null' is not defined" exception
        response_text = response.text.replace("null","\"null\"")
        responseList = eval(response_text)
        #return 404 error if reponse resembles the worldbank api's not found response object
        if 'message' in responseList[0]: 
            return {"message": "The indicator_id {} was not found in the worldbank database".format(indicator_id), 
            "indicator_id": indicator_id}, 404
        #connect to db
        conn = sqlite3.connect('z5162987.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys=ON")

        #responseList[0] is a dict
        #Extract data and insert collection into db
        indicator_id = responseList[1][0]['indicator']['id']
        indicator_value = responseList[1][0]['indicator']['value']
        creation_time = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        c.execute("INSERT INTO Collection VALUES (NULL, '{}','{}','{}')".format(indicator_id, indicator_value, creation_time))
        conn.commit()
        #get the current collection's database id
        c.execute("SELECT last_insert_rowid()")
        collectionId = c.fetchall()
        #insert Collection_Entries into db
        #i is a dict
        for i in responseList[1]:
            #ignore null values
            if i['value'] == "null": continue
            country = i['country']['value']
            date = i['date']
            value = i['value'] 
            c.execute("INSERT INTO Collection_Entry VALUES (NULL, ?,?,?,?)",(collectionId[0][0], country,date,value))
        conn.commit()
        conn.close()
        return {"uri": "/collections/"+str(collectionId[0][0]),
                "id": collectionId[0][0], 
                "creation_time": creation_time, 
                "indicator_id": indicator_id}, 201

#This endpoint handles:
#DELETE /collections/{id}
#GET /collections/{id}
@api.route('/collections/<int:id>')
class Collection(Resource):
    #################### Q U E S T I O N   4 ########################
    @api.response(200, 'Successful')
    @api.response(404, 'Collection Not Found')
    @api.doc(description="Question 4 - Retrieve a collection")
    def get(self, id):
        conn = sqlite3.connect('z5162987.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys=ON")
        #get collection specified by id
        c.execute("SELECT * FROM Collection where id = {}".format(id))
        row = c.fetchone()
        #return 404 error if no collection found
        if row is None: 
            conn.close()
            return {"message": "The collection {} was not found in the database".format(id), "id": id}, 404
        
        #get list of all collection entries in collection
        collection_id, indicator_id, indicator_value, creation_time = row
        c.execute("SELECT * FROM Collection_Entry where collection_id = {}".format(collection_id))
        collectionEntries = []
        for tup in c.fetchall():
            _,_,country, date, value = tup
            collectionEntries.append({"country": country, "date": date, "value": value})
        conn.close()
        return {"id": collection_id,
            "indicator": indicator_id,
            "indicator_value": indicator_value,
            "creation_time": creation_time,
            "entries": collectionEntries
        }, 200
    
    #################### Q U E S T I O N   2 ########################
    @api.response(200, 'Successful')
    @api.response(404, 'Collection Not Found')
    @api.doc(description="Question 2 - Deleting a collection with the data service")
    def delete(self, id):
        #connect to db
        conn = sqlite3.connect('z5162987.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys=ON")
        #delete collection
        c.execute("DELETE FROM Collection WHERE id = {}".format(id))
        conn.commit()
        #check if deletion was unsuccessful
        if c.rowcount == 0:
            conn.close()
            return {"message": "The collection {} was not found in the database".format(id),
                    "id": id}, 404
        else:
            conn.close()
            return {"message": "The collection {} was removed from the database!".format(id), 
                    "id": id}, 200

#This endpoint handles:
#GET /collections/{id}/{year}?q=<query>
@api.route('/collections/<int:id>/<int:year>')
class IndicatorTopBottom(Resource):
    #################### Q U E S T I O N   6 ########################
    @api.response(200, 'Successful')
    @api.response(404, 'Indicator Not Found')
    @api.doc(description="Question 6 - Retrieve top/bottom economic indicator values for a given year")
    @api.expect(GetTopBottomParser)
    def get(self, id, year):
        args = GetTopBottomParser.parse_args()
        #extract n value from query
        nquery = args.get('q')
        n = int(nquery)
        #determine if order will be ascending or descending
        #DESC necessary for positive n, by nature of the way rows are returned in sqlite
        order = 'DESC' if n > 0 else 'ASC'
        #connect to database
        conn = sqlite3.connect('z5162987.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys=ON")
        #query for collection specified by id
        c.execute("SELECT indicator_id, indicator_value FROM Collection WHERE id = {}".format(id))
        #return 404 error if no collection found
        row = c.fetchone()
        if row is None:
            conn.close()
            return {"message": "The collection {} was not found in the database".format(id),
                    "id": id}, 404
        #query for collection entries associated by id
        indicator_id, indicator_value = row
        c.execute("""SELECT country, value FROM Collection_Entry
                    WHERE collection_id = {} AND date = '{}'
                    ORDER BY value {}
                    LIMIT {}
                """.format(id, year, order, abs(n)))
        #return 404 error if no collection entries (indicators) found
        fetchall = c.fetchall()
        if len(fetchall) == 0:
            conn.close()
            return {"message": "No indicators for the year {} were found in the collection {}".format(year,id),
                    "id": id, "year": year}, 404
        #get a list of collection entries that match the year and query
        entries = []
        for tup in fetchall:
            country, value = tup
            entries.append({"country": country, "value": value})
        conn.close()
        return {"indicator": indicator_id,
                "indicator_value": indicator_value,
                "entries": entries
                }

#This endpoint handles:
#GET /collections/{id}/{year}/{country}
@api.route('/collections/<int:id>/<int:year>/<string:country>')
class Indicator(Resource):
    ################### Q U E S T I O N   5 ########################
    @api.response(200, 'Successful')
    @api.response(404, 'Indicator Not Found')
    @api.doc(description="Question 5 - Retrieve economic indicator value for given country and a year")
    def get(self, id, year, country):
        conn = sqlite3.connect('z5162987.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys=ON")
        #query for collection entry specified by parameters, join with Collection table to obtain the indicator_id
        c.execute("""SELECT ce.collection_id, c.indicator_id, ce.country, ce.date, ce.value
            FROM Collection_Entry ce
            INNER JOIN Collection c ON (c.id = ce.collection_id)
            WHERE ce.collection_id = ? AND ce.date = ? AND ce.country = ?""", (id, str(year), country))
        row = c.fetchone()
        #if collection_entry not found, return 404 error
        if row is None: 
            conn.close()
            return {"message": "Economic indicator not found"}, 404
        #return indicator
        collection_id, indicator_id, country, date, value = row
        conn.close()
        return {"id": collection_id,
            "indicator": indicator_id,
            "country": country,
            "year": int(date),
            "value": value
            }, 200
        

if __name__ == '__main__':
    #Create database tables if db doesn't exist
    conn = sqlite3.connect('z5162987.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("""CREATE TABLE IF NOT EXISTS Collection(
            id integer PRIMARY KEY AUTOINCREMENT,
            indicator_id text NOT NULL,
            indicator_value text NOT NULL,
            creation_time text NOT NULL
            )""")
    c.execute("""CREATE TABLE IF NOT EXISTS Collection_Entry(
            id integer PRIMARY KEY AUTOINCREMENT,
            collection_id integer NOT NULL, 
            country text NOT NULL,
            date text NOT NULL,
            value real NOT NULL,
            FOREIGN KEY (collection_id) REFERENCES Collection(id) ON DELETE CASCADE
            )""")
    conn.close()
    app.run(debug=True)



