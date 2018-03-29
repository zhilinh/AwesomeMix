import os
import django

PROJECT_PATH = "D:/41245/Documents/CMU/17-437/awesomemix/"

os.chdir(PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "awesomemix.settings")
django.setup()

from movie.models import Movie, Person


def read_databases():
    person_data = open("./databases/name.basics.tsv/data.tsv", "r")

    lines = person_data.readlines()
    for i in range(1, len(lines)):
        line = lines[i].strip().split("\t")
        try:
            person = Person.objects.get(imdb_id=line[0])
        except:
            person = Person(imdb_id=line[0],
                            name=line[1],
                            birth_year=line[2],
                            death_year=line[3],
                            primary_profession=line[4],
                            known_for_titles=line[5])
            person.save()
    person_data.close()

    crew_data = open("./databases/title.crew.tsv/data.tsv", "r")

    lines = crew_data.readlines()
    for i in range(1, len(lines)):
        line = lines[i].strip().split("\t")
        try:
            movie = Movie.objects.get(imdb_id=line[0])
        except:
            movie = Movie(imdb_id=line[0],
                          directors=line[1],
                          writers=line[2])
            movie.save()
    crew_data.close()

    principals_data = open("./databases/title.principals.tsv/data.tsv", "r")

    lines = principals_data.readlines()
    for i in range(1, len(lines)):
        line = lines[i].strip().split("\t")
        try:
            movie = Movie.objects.get(imdb_id=line[0])
            person = Person.objects.get(imdb_id=line[2])
        except:
            movie = Movie(imdb_id=line[0])
            person = Person(imdb_id=line[2])
            movie.save()
        if line[3] == 'director':
            movie.directors = line[3]
        elif line[3] == 'writer':
            movie.writers = line[3]
        elif line[3] == 'actor' or line[3] == 'actress':
            movie.casts.add(person)
        movie.save()

    principals_data.close()

    rating_data = open("./databases/title.ratings.tsv/data.tsv", "r")

    lines = rating_data.readlines()
    for i in range(1, len(lines)):
        line = lines[i].strip().split("\t")
        try:
            movie = Movie.objects.get(imdb_id=line[0])
        except:
            movie = Movie(imdb_id=line[0])
            movie.save()
        movie.imdb_rating = float(line[1])
        movie.imdb_num_votes = int(line[2])
        movie.save()

    rating_data.close()

if __name__ == '__main__':
    read_databases()