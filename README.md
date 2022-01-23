# CS-IMC-2021-2022-TP-API

TP réalisé par Ewen QuIMERC'H et Clarence CHARLES

Query 1 and 2 may not work anymore because of the modification of the databases structure. Query 3, 4 and 5 are adapted to the new DB structure.

# Resource deployment
## Infra
Through terraform, using api.tf in the azure console.
Type 
```
terraform validate
terraform plan -out main.plan
terraform apply main.plan
```

Destroy resources with :

```
terraform destroy
```

## Code
CI/CD with github action. Secret added with the "secret" option in github.


# Databases
SQL
tArtist(idArtist, primaryName, birthYear)
tFilm(idFilm, primaryTitle, startYear, runtimeMinutes)
tJob(idArtist, category[enumeration], idFilm)
tFilmGenre(idFilm, idGenre)
tGenre(idGenre, genre)

Neo4J
:Film (averageRating, idFilm, nid, primaryTitle, startYear)
:Artist(birthYear, idArtist, primaryName)


## Example of requests
Category of films where at least one film had at least one performer had different roles (such as actor and director)

```
SELECT g.genre FROM tGenre AS g JOIN (
    SELECT DISTINCT fg.idGenre
    FROM tJob AS j JOIN tFilmGenre AS fg
    ON j.idFilm=fg.idFilm
    GROUP BY j.idArtist, j.idFilm, fg.idGenre
    HAVING COUNT(DISTINCT j.category) > 1
) AS costum ON g.idGenre = costum.idGenre
```

Average rating by category of films

Impossible with the new database structure. See Query 3. 

With another database structure:
SQL
tGenres(tconst, genre)
tNames(nconst, primaryName, birthYear[int])
tPrincipals(nconst,category,tconst)
tTitles(tconst, primaryTitle, startYear[int], averageRating[decimal], runtimeMinutes[int])

This request would have worked:

SELECT g.genre, AVG(t.averageRating) AS avgRating 
FROM tGenres AS g JOIN tTitles AS t ON g.tconst=t.tconst 
WHERE t.averageRating IS NOT NULL 
GROUP BY g.genre







