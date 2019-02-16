import random
import string
import sys
import json

import Pyro4


class Person:
	def __init__(self):
		self.userid = self.__gen_user_id()
		print(self.userid)
		# now connect to the server

	def __gen_user_id(self):
		""" Generate user ID """
		my_ID = ""
		for i in range(1, 20):
			my_ID += random.choice(string.ascii_uppercase)
		return my_ID

	def visit(self,user_inp,movie):
		if (user_inp == 1):
			self.retrieve_rating(movie)
		elif (user_inp == 2):
			self.submit_rating(movie)
		elif (user_inp == 3):
			self.get_avg(movie)

	

		
	def retrieve_rating(self, movie):
		#print("Rating for movie ", movie.get_name(),": ", movie.get_rating_by_name(userid))
		#return movie.get_rating_by_name(userid)
		option= self.requests("GET_RATING", self.userid, "")
		print(option)


	def submit_rating(self, movie):
		inp=float(input("Enter a rating: "))
		#movie.add_rating(userid, inp)
		#print("Rating for movie ", movie.get_name() ,": ", movie.get_rating_by_name())
		option= self.requests("ADD_RATING", self.userid, inp)
		print(option)

	def get_avg(self, movie):
		#print(movie.get_average_rating(userid))
		option= self.requests("GET_AVG", self.userid, "")
		print(option)

	def set_movie_name(self,userid):
		inp=input("Enter name of movie: ")
		#movie.set_movie(self.userid,inp)
		option= self.requests("SET_MOVIE", self.userid, inp)
		print(option)

	def requests(self,request,userid,data):
		data_to_send = {'request': request, 'userid': userid, 'data': data }
		#data_json_encoded = json.dumps(data_to_send)
		ns = Pyro4.locateNS()
		self.server_uri = ns.lookup("frontend")
		actual_server = Pyro4.Proxy(self.server_uri)
		recv = actual_server.process_command(data_to_send)
		return recv


def main():
	exit_status = False
	prog = Person()
	print("Hello,", prog.userid)
	movie=prog.set_movie_name(prog.userid)
	while not exit_status:
		print("1. Get a movie rating")
		print("2. Add a movie rating")
		print("3. Get a movie average rating")
		user_inp = int(input("Select an option of what would you like to do: "))
		if (user_inp == 0):
			print ("Thank you come again")
			return
		else:
			prog.visit(user_inp,movie)

if __name__== "__main__":
	main()
