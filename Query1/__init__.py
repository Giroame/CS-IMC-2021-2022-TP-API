import logging
from py2neo import Graph
from py2neo.bulk import create_nodes, create_relationships
from py2neo.data import Node
import os
import pyodbc
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

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
    try:
        logging.info("Test de connexion avec py2neo...")
        graph = Graph(neo4j_server, auth=(neo4j_user, neo4j_password))
        graph.run("MATCH (n:Test) RETURN n")

        try:
            logging.info("Test de connexion avec pyodbc...")
            with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
        except:
            errorMessage = "Erreur de connexion a la base SQL"
    except:
        errorMessage = "Erreur de connexion a la base Neo4j"
        
    
    if name:
        nameMessage = f"Hello, {name}!"
    else:
        nameMessage = "Le parametre 'name' n'a pas ete fourni lors de l'appel."
    
    if errorMessage is None:
        return func.HttpResponse(nameMessage + errorMessage, status_code=500)

    else:
        finalMessage = nameMessage + "Connexions réussies a Neo4j et SQL!"
        return func.HttpResponse(finalMessage + " Connexions réussies a Neo4j et SQL!")