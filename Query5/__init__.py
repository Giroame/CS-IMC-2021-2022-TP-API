import logging
from py2neo import Graph
from py2neo.bulk import create_nodes, create_relationships
from py2neo.data import Node
import os
import pyodbc as pyodbc
import azure.functions as func

# Redeployment 2

def get_param(req, name):
    var = ""
    var = req.params.get(name)
    if not var:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            var = req_body.get(name)
    return var



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed Query 1.')

    name = get_param('name')
    genre = get_param('genre')
    
    server = os.environ["TPBDD_SERVER"]
    database = os.environ["TPBDD_DB"]
    username = os.environ["TPBDD_USERNAME"]
    password = os.environ["TPBDD_PASSWORD"]
    driver= '{ODBC Driver 17 for SQL Server}'

    neo4j_server = os.environ["TPBDD_NEO4J_SERVER"]
    neo4j_user = os.environ["TPBDD_NEO4J_USER"]
    neo4j_password = os.environ["TPBDD_NEO4J_PASSWORD"]

    if len(server)==0 or len(database)==0 or len(username)==0 or len(password)==0 or len(neo4j_server)==0 or len(neo4j_user)==0 or len(neo4j_password)==0:
        return func.HttpResponse("Au moins une des variables d'environnement n'a pas été initialisée.", status_code=500)
        
    errorMessage = ""
    dataString = ""
    ## Average rating by category of films
    try:

        # Cypher
        logging.info("Test de connexion avec py2neo...")
        graph = Graph(neo4j_server, auth=(neo4j_user, neo4j_password))
        print("Connexion reussie !")

        dico_film_rating={}
        dico_genre_film={}

        films = graph.run("MATCH (t:Film) RETURN t.idFilm, t.averageRating")

        for film in films:
            dico_film_rating[film['t.idFilm']]=film['t.averageRating']

        try:
            # SQL
            logging.info("Test de connexion avec pyodbc...")
            with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
                cursor = conn.cursor()

                request = f"SELECT g.genre, costum.avgRunTimeMinute  FROM tGenre AS g JOIN ( \
                                    SELECT AVG(f.runtimeMinutes) AS avgRunTimeMinute, fg.idGenre \
                                    FROM tFilm AS f JOIN tFilmGenre AS fg \
                                    ON f.idFilm=fg.idFilm \
                                    GROUP BY fg.idGenre \
                                ) AS costum ON g.idGenre = costum.idGenre \
                                    WHERE g.genre='{genre}'"
                cursor.execute(request) 
                rows = cursor.fetchall()
                for row in rows:
                    dataString += f"Genre: {row[0]}, duration: {row[1]} min\n"



        except:
            errorMessage = "Erreur de connexion a la base SQL"
    except:
        errorMessage = "Erreur de connexion a la base Neo4j"
        
    
    if name:
        nameMessage = f"Hello, {name}!\n"
    else:
        nameMessage = "Le parametre 'name' n'a pas ete fourni lors de l'appel.\n"
    
    if errorMessage != "":
        return func.HttpResponse(dataString + nameMessage + errorMessage, status_code=500)

    else:
        return func.HttpResponse(dataString + nameMessage + " Connexions réussies a Neo4j et SQL!")
