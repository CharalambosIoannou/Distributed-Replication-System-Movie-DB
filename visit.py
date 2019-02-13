from movie_db import Movie
from person import Person
import Pyro4
import Pyro4.util
import sys

#uri = "PYRO:example.movie@192.168.1.228:16500"
#movie = Pyro4.Proxy(uri)
#movie = Pyro4.Proxy("PYRONAME:mythingy")

ipAddressServer = "10.245.119.161" # TODO add your server remote IP here
movie = Pyro4.core.Proxy('PYRO:movie@' + ipAddressServer + ':9090')

harry=Person("Harry")
john=Person("John")
harry.visit(movie)
john.visit(movie)
