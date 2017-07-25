
# Scraping IMDB and Querying Wikidata for movie data

## Why
I mostly watch movies streaming at home, several months after they come out, because I hate movie theaters. (Star Wars excepted)
However, because all of the marketing for a movie has ended by the time they come out on streaming, I don't always remember what I want to watch. 
So, I wanted a spreadsheet of movies.
To get some seed data, I scraped IMDB for the 250 most popular movies of 2013-2017 to keep the name and IMBD_ID of the movies.
Then I queried Wikidata SPARQL to get the Wikidata ID and Wikipedia article for that movie.

## Scraper
This is pretty straightforward - grab a page, use CSS classes to find the 50 links, extract the link and title text for the movie. 
Rather than being clever about finding the next page, just hard-code the first 5 pages of the list into the scraper targets.

This is probably against the IMDB terms of service, but since I stream all of my videos from Amazon and I'm explicitly doing this to find more videos to stream I don't feel that bad. 

To run:
```
scrapy crawl imdbScraper -a year=2017 -o 2017.json
```
Set the year parameter and output file as you so desire.

## Enrich with data from Wikidata
If I was really clever, we'd take the data we just scraped and load it into a local linked data system and do some kind of SPARQL join, but we're going to do the simplest thing possible.
So, for each movie in the dataset, run a SPARQL query to pull out the Wikidata ID, name, logo image if it exists, and english-language wikipedia article if it exists. 
The SPARQL query looks for items that have a property IMDB_ID with a value that matches the ID we have for that movie. 
It should be a reasonably efficient query on the wikidata side, though I don't know exactly how they index.
It's also probably how any federated SPARQL engine works, I don't imagine they're fancy enough to try and send bulk data to remote systems.

To run:
``` 
python process.py 2017.json 2017.csv
```
