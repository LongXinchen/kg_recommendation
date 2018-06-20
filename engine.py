#!/usr/bin/python
# -*- coding: utf-8 -*
import sys
import urllib2
from datetime import datetime
import time
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF

def search(query):
    #query = "From the Earth to the Moon"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    str1 = '''
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo:<http://dbpedia.org/ontology/>
PREFIX dc:<http://purl.org/dc/terms/>

SELECT distinct ?name ?url ?url2 ?abstract ?work
WHERE  {
  {?work rdf:type dbo:Book ;
rdfs:label ?name ;
   foaf:isPrimaryTopicOf ?url;
  prov:wasDerivedFrom ?url2;
 dbo:abstract ?abstract
   FILTER(lang(?name)="en" &&(lang(?abstract)="en")  && regex(str(?name),"%s")).
 }
  UNION
{?work rdf:type dbo:Film ;
  rdfs:label ?name ;
 foaf:isPrimaryTopicOf ?url;
prov:wasDerivedFrom ?url2;
   dbo:abstract ?abstract
 FILTER(lang(?name)="en" &&(lang(?abstract)="en")  && regex(str(?name),"%s")).
   }

  UNION
{?work rdf:type dbo:VideoGame ;
  rdfs:label ?name ;
 foaf:isPrimaryTopicOf ?url;
prov:wasDerivedFrom ?url2;
   dbo:abstract ?abstract
 FILTER(lang(?name)="en" &&(lang(?abstract)="en")  && regex(str(?name),"%s")).
   }
}
    ''' % (query, query, query) 
    #print str1
    sparql.setQuery(str1)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    return results

def recommend(search_res):
    for result in search_res["results"]["bindings"]:
        if ("work" in result):
            url = result["work"]["value"].encode('ascii', 'ignore').split('/')[-1]
        else:
            url = ''
        break
    #url = 'From_the_Earth_to_the_Moon'
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    str2 = '''
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo:<http://dbpedia.org/ontology/>
    PREFIX dct:<http://purl.org/dc/terms/>
    
    SELECT COUNT(?work) SAMPLE(?work)
            WHERE
            {
                dbr:%s dct:subject ?o .
                ?work dct:subject ?o
                FILTER (?work != dbr:%s ) .
              } 
        GROUP BY ?work
        ORDER BY DESC(COUNT(?work))
        limit 10
    ''' % (url, url) 
          
    #print str2
    sparql.setQuery(str2)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    return results

def create_output(search_res, recommend_res):

    # Create HTML output
    output = []
    output.append('<html><head> <title>search & recommend</title></head>')
    output.append('<body><h2>Search</h2>')
    output.append('<ul>')
    for result in search_res["results"]["bindings"]:
        if ("name" in result):
            name = result["name"]["value"].encode('ascii', 'ignore')
        else:
            name = 'NONE'
        if ("abstract" in result):
            abstract = result["abstract"]["value"].encode('ascii', 'ignore')
        else:
            abstract = ' '
        if ("url" in result):
            url = result["url"]["value"].encode('ascii', 'ignore')
        else:
            url = ' '
        output.append('<li><a href="{}">{}</a>: </1i>'.format(url, name))
        output.append('<p>{}</p>'.format(abstract))
    output.append('</ul>')
    output.append('<body><h2>Recommend</h2>')
    output.append('<ul>')
    for result in recommend_res["results"]["bindings"]:
        if ("callret-1" in result):
            uri = result["callret-1"]["value"].encode('ascii', 'ignore')
            name = uri.split('/')[-1]
            url = "http://en.wikipedia.org/wiki/" +  name
            output.append('<li><a href="{}">{}</a></1i>'.format(url, name))
    output.append('</ul>')
    output.append('</body></html>')
    
    with open("./output.html", 'w') as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    query = sys.argv[1]
    print query
    search_res = search(query)
    recommend_res = recommend(search_res)
    create_output(search_res, recommend_res)
