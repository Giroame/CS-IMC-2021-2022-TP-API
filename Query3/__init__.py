import logging
from py2neo import Graph
from py2neo.bulk import create_nodes, create_relationships
from py2neo.data import Node
import os
import pyodbc as pyodbc
import azure.functions as func

# Redeployment 2


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed Query 1.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')
    
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


                cursor.execute("SELECT DISTINCT genre FROM tGenre")
                rows = cursor.fetchall()
                for row in rows:
                    dico_genre_film[row[0]] = []

                cursor.execute("SELECT fg.idFilm, g.genre FROM tGenre AS g JOIN tFilmGenre AS fg ON g.idGenre = fg.idGenre")
                rows = cursor.fetchall()
                for row in rows:
                    dico_genre_film[row[1]].append(row[0])
                    # dataString += f"SQL: tconst={row[0]}, primaryTitle={row[1]}, averageRating={row[2]}\n"

                for genre in dico_genre_film:
                    sum, count=0, 0
                    dataString += f"{genre} : "
                    for film in dico_genre_film[genre]:
                        if dico_film_rating[film] != None:
                            sum += dico_film_rating[film]
                            count += 1
                    if count != 0:
                        dataString+= f"averageRating is {round(sum/count,2)}/10\n"


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
