from movie_db import Movie
from person import Person

movie= Movie("Toy Story (1995)")
harry=Person("Harry")
john=Person("John")
harry.visit(movie)
john.visit(movie)
