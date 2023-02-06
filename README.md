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
 
### DELETE /collections/{id}
<ul>
  <li>Deletes a collection from the local database given a collection id</li>
</ul>
Example 

### GET /collections
<ul>
  <li>Retrieves all available collections</li>
  <li>"order_by" is a comma separated string value to sort the collection based on the given criteria: id, creation_time, indicator</li>
  <li>In each segment, + indicates ascending order, and - indicates descending order</li>
</ul>
Example

### GET /collections/{id}
<ul>
  <li>Retrieves one collection by its collection id</li>
</ul>
Example

### GET /collections/{id}/{year}/{country}
<ul>
  <li>Retrieves economic indicator value for a given country and a year</li>
</ul>
Example

### GET /collections/{id}/{year}?q=<query>
<ul>
  <li>Retrieve top/bottom N economic indicators for a given year</li>
</ul>
Example 
 
