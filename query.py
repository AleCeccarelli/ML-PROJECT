from SPARQLWrapper import SPARQLWrapper, JSON
import json

endpoint_url = "https://query.wikidata.org/sparql"

latitude = 41.902782
longitude = 12.496365

query = """SELECT DISTINCT ?imdbID WHERE {{ 
     ?film wdt:P915 ?place.
     ?film wdt:P345 ?imdbID. 
     SERVICE wikibase:around {{
     ?place wdt:P625 ?locationCoord.
     bd:serviceParam wikibase:center ?loc.
     bd:serviceParam wikibase:radius "5".}}
     VALUES(?loc){{("Point({lon} {lat})"^^geo:wktLiteral)}} 
    }}""".format(lon = longitude, lat = latitude)

def get_results():
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

#results = get_results()
#with open('jsons/queryResult.json', 'w') as outfile:
#    json.dump(results, outfile, indent=4)
