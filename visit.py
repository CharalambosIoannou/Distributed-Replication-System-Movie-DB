from movie_db import Movie
from person import Person
import Pyro4

uri = input("Enter the uri of the movie database: ").strip()
movie = Pyro4.Proxy(uri)



harry=Person("Harry")

john=Person("John")
harry.visit(movie)
john.visit(movie)
