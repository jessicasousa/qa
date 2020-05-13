import json
import re
import pandas as pd
import random
import pickle
import copy
import unicodedata
import rdflib
from rdflib import URIRef, RDFS
from sparql_builder import sparql_build
from sparql_builder import constants

data_path = 'pandas_data/'
graph = rdflib.Graph()
graph.parse("data/movieontology.ttl", format="ttl")


entities_dict = pickle.load( open( "entities_dict.p", "rb" ) )
with open(data_path+"movies_df.dat", "rb") as f:
    movies = pickle.load(f)
with open(data_path+"series_df.dat", "rb") as f:
    series = pickle.load(f)
with open(data_path+"person_df.dat", "rb") as f:
    person = pickle.load(f)    
with open(data_path+"production_company_df.dat", "rb") as f:
    company = pickle.load(f)


def get_uri_from_movie_serie(title):
    results = movies.loc[movies['title']==title]
    if not results.empty:
        return "movie", results["uri"].tolist()
    else:
        results = series.loc[series['title']==title]
        return "serie", results["uri"].tolist()

def get_company_uri(name):
    results = company.loc[company['name']==name]
    return results["uri"].tolist()


def get_person_uri(birth_name):
    df = person.loc[person["birthName"]==birth_name]
    results = []
    for index, row in df.iterrows():
        staff_pos = re.search(r"\w*_*-*\w*$", row["type"], re.IGNORECASE).group()
        results.append([row["uri"], staff_pos])
    try:
      n1,n2=birth_name.split(' ')
      birth_name2=n2+', '+n1
      df = person.loc[person["birthName"]==birth_name2]
      for index, row in df.iterrows():
          staff_pos = re.search(r"\w*_*-*\w*$", row["type"], re.IGNORECASE).group()
          results.append([row["uri"], staff_pos])
      print('uris:',results)    
    except ValueError:
      return results
    return results


def get_relations(text):
	relations = text.split('*')[1]
	#relations_list = relations.split(')')
	relations_list = re.findall('\(.*?\)',relations)
	return relations_list


def clean_word(palavra):

    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)

def especify_entities(entities):
  for ent in entities:
    if(ent['entity']=='genre_name' or ent['entity']=='staff_ent' or ent['entity']=='property_ent'):
      ent['entity'] = entities_dict[clean_word(ent['value'])]
    if(ent['entity']=='filme_serie'):
      ent['entity'] = entities_dict[clean_word(ent['value'])]
    if(ent['entity']=='awards'):
      ent['entity'] = entities_dict[clean_word(ent['value'])]
    if(ent['entity']=='title'):
      ent['entity'] = clean_word(ent['value'])
    if(ent['entity']=='people_names'):
      pass    

    

  return entities


def get_relations_queries(rasa_entities):
  relations = []
  text = rasa_entities['text']
  entities = rasa_entities['entities']
  for i in range(len(entities)):
    for j in range(len(entities)):
      if(i!=j):
        relations.append(text+'|'+entities[i]['value']+'|'+entities[j]['value'])
  return relations


def get_rdfs_label( subject, lang="pt-br"):
    subject = URIRef(subject)
    labels = []
    # setup the language filtering
    if lang is not None:
        if lang == "":  # we only want not language-tagged literals

            def langfilter(l):
                return l.language is None

        else:

            def langfilter(l):
                return l.language == lang

    else:  # we don't care about language tags

        def langfilter(l):
            return True

    for label in graph.objects(subject, RDFS.label):
        if langfilter(label):
            #labels.append(str(label))
            return str(label)
    return labels
