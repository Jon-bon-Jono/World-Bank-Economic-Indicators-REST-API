# World-Bank-Economic-Indicators-REST-API

## Running: 
`py z5162987.py`
<p></p>

## Usage:
### POST /collections
<ul>
  <li> Imports a data collection associated with an economic indicator id from http://api.worldbank.org/v2/ </li>
  <li> Stores collection onto a local sqlite database with a unique collection id</li>
  <li> Indicator ids: http://api.worldbank.org/v2/indicators</li>
</ul>
Example

`HTTP operation: POST /collections?indicator_id=NY.GDP.MKTP.CD`

Returns: 201 Created

<pre> { 
    "uri" : "/collections/1", 
    "id" : 1,  
    "creation_time": "2019-04-08T12:06:11Z",
    "indicator_id" : "NY.GDP.MKTP.CD"
} </pre>

### DELETE /collections/{id}
<ul>
  <li>Deletes a collection from the local database given a collection id</li>
</ul>
Example 

`HTTP operation: DELETE /collections/{id}`

Returns: 200 OK

<pre>{ 
    "message" :"The collection 1 was removed from the database!",
    "id": 1
}</pre>
### GET /collections
<ul>
  <li>Retrieves all available collections</li>
  <li>"order_by" is a comma separated string value to sort the collection based on the given criteria: id, creation_time, indicator</li>
  <li>In each segment, + indicates ascending order, and - indicates descending order</li>
</ul>

Example:

`HTTP operation: GET /collections?order_by={+id,+creation_time,+indicator,-id,-creation_time,-indicator}`

Returns: 200 OK

<pre>[ 
   { 
    "uri" : "/collections/1", 
    "id" : 1,  
    "creation_time": "2019-04-08T12:06:11Z",
    "indicator" : "NY.GDP.MKTP.CD"
    },
   { 
    "uri" : "/collections/2", 
    "id" : 2,  
    "creation_time": "2019-05-08T12:16:11Z",
    "indicator" : "2.0.cov.Math.pl_3.all"
   },
   ...</pre>

### GET /collections/{id}
<ul>
  <li>Retrieves one collection by its collection id</li>
</ul>

Example

`HTTP operation: GET /collections/{id}`

Returns

<pre>{  
  "id" : 1,
  "indicator": "NY.GDP.MKTP.CD",
  "indicator_value": "GDP (current US$)",
  "creation_time" : "2019-04-08T12:06:11Z"
  "entries" : [
                {"country": "Arab World",  "date": 2016,  "value": 2500164034395.78 },
                {"country": "Australia",   "date": 2016,  "value": 780016444034.00 },
                ...
   ]
}</pre>

### GET /collections/{id}/{year}/{country}
<ul>
  <li>Retrieves economic indicator value for a given country and a year</li>
</ul>
Example:

`HTTP operation: GET /collections/{id}/{year}/{country}`

Returns: 200 OK

<pre>
{ 
   "id": 1,
   "indicator" : "NY.GDP.MKTP.CD",
   "country": "Arab World", 
   "year": 2016,
   "value": 780016444034.00
}
</pre>

### GET /collections/{id}/{year}?q=\<query\>
<ul>
  <li>Retrieve top/bottom N economic indicators for a given year</li>
</ul>
Example:
`HTTP operation: GET /collections/{id}/{year}?q=&lt;query&gt;`
  
Returns: 200 OK
<pre>{ 
   "indicator": "NY.GDP.MKTP.CD",
   "indicator_value": "GDP (current US$)",
   "entries" : [
                  { 
                     "country": "Arab World",
                     "value": 2500164034395.78
                  },
                  ...
               ]
}</pre>

The <query> is an optional integer parameter which can be either of following:
<ul>
  <li>+N (or simply N) : Returns top N countries sorted by indicator value (highest first)</li>
  <li>-N : Returns bottom N countries sorted by indicator value</li>

 
