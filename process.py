from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import requests
import json
import sys


# 
# learned a bunch from here
# https://people.wikimedia.org/~bearloga/notes/wdqs-python.html
# but didn't use much of it - SPARQLWrapper seemed to hang reading
# from wikidata, but a straight-up python-requests version just worked
# so didn't spend much time debugging sparqlwrapper
#

url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'

# QUERY:
# look for items that:
# - have property 345 (imdb_id) that matches the one we're looking for
# and 
# - if you find such an item, logo-image is property 154 (logo image)
# and
# - if you find such an item, root around for the wikipedia article
#   (but that article may not exist)
# 
# the wikipedia article stuff is from this SO answer
# https://opendata.stackexchange.com/questions/6050/get-wikipedia-urls-sitelinks-in-wikidata-sparql-query
#
query = ''' 
SELECT ?item ?itemLabel ?logo_image ?article WHERE {{
  ?item wdt:P345 '{0}'.
  OPTIONAL {{
  ?item wdt:P154 ?logo_image.
  }}
  OPTIONAL {{
      ?article schema:about ?item .
      ?article schema:inLanguage "en" .
      ?article schema:isPartOf <https://en.wikipedia.org/> .
    }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
}}
'''
#
# We're just going to hit the sparql endpoint and get back JSON
# http://ramiro.org/notebook/us-presidents-causes-of-death/
#
def getData(movie_id, iteration):
  actual = query.format(movie_id)
  print("%d: Processing %s\n\n" % (iteration, movie_id))
  wditem = requests.get(url, params={'query': actual, 'format': 'json'}).json()
  #print(wditem)

  # We're going to return a mini dataframe here
  # first, let's make one from the JSON results
  results_df = pd.io.json.json_normalize(wditem['results']['bindings'])

  # if it's empty, just hand back a df with the imdb_id and nothing else
  if results_df.empty:
    #print("---Null results on %s---" % (movie_id))
    nullresults = {"imdb_id": movie_id}
    return(pd.DataFrame(nullresults, index=[0]))

  # otherwise, let's put together a fuller dataframe
  # it may be missing values so we'll have to test for that
  results_df['imdb_id'] = pd.Series(movie_id)
  columns = ['imdb_id', 'item.value', 'itemLabel.value']
  if 'logo_image.value' in results_df.columns:
    columns.append('logo_image.value')
  if 'article.value' in results_df.columns:
    columns.append('article.value')

  # select a subset of results_df and return it
  # probably don't need the fillna
  results_df = results_df[columns].fillna('')
  return(results_df)


# main code  - read in input
if len(sys.argv) < 3:
  print("Usage: process.py input.json output.csv")
  exit(-1)

movies = pd.read_json(sys.argv[1])
movie_ids = movies['imdbid'].tolist()

# get an empty dataframe
processed = pd.DataFrame()
for i, movie in enumerate(movie_ids):
  m = getData(movie, i)
  processed = processed.append(m)

combined = pd.merge(movies, processed, left_on="imdbid", right_on="imdb_id", how="inner")

combined.to_csv(sys.argv[2])
