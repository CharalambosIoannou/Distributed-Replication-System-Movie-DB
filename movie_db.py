import csv
import random
import sys

import Pyro4



movie_name_dict1 = {}
movie_rating_dict1 = {}
with open('movies.csv', encoding="utf8") as csv_file:
	counter = 0
	reader = csv.reader(csv_file, delimiter=',')
	for row in reader:
		if counter == 0:
			counter += 1
		else:
			movie_name_dict1[row[0]] = row[1][:-7]

with open('ratings.csv', encoding="utf8") as csv_file:
	counter = 0
	reader = csv.reader(csv_file, delimiter=',')
	for row in reader:
		if counter == 0:
			counter += 1
		else:
			movie_id = row[1]
			if movie_id not in movie_rating_dict1:
				movie_rating_dict1[movie_id] = [float(row[2])]
			else:
				movie_rating_dict1[movie_id].append(float(row[2]))


@Pyro4.expose
class Movie(object):
	people_dict = {}
	server_list = []
	timestamp = [0,0,0]

	def __init__(self):
		self.movie_name_dict = movie_name_dict1
		self.movie_rating_dict = movie_rating_dict1
		self.counter = 0
		
	""" Server Functions"""

	def set_servers(self, server_list):
		for s in server_list:
			self.server_list.append(Pyro4.Proxy(s))
			
	def copy_people_to_servers(self, state):
		self.people_dict = state
		
		
	def copy_rating_to_servers(self, state):
		self.movie_rating_dict = state
	
	def copy_data_to_servers(self):
		for s in self.server_list:
			s.copy_people_to_servers(self.people_dict)
			s.copy_rating_to_servers(self.movie_rating_dict)
		return True
	
	def get_status(self):
		result= random.choice(["Active","Overloaded","Offline"])
		return ''.join(result)
	
	
	def create_user(self, user_id, movie):
		self.people_dict[user_id] = [movie]
		
		
	""" Movie Functions"""
	
	def get_movie_name_by_id(self, movie_id):
		return self.movie_name_dict.get(str(movie_id))

	def set_movie(self, name, movie_name):
		if name not in self.people_dict:
			print("First time setting movie")
			self.create_user(name,movie_name)
			print(name, "entered the movie ", movie_name, " as input")
			self.movie_name = movie_name
		else:
			print("Choosing different movie")
			for key in self.people_dict.keys():
				if key == name:
					self.people_dict[key] = movie_name
		
		self.copy_data_to_servers()
		return movie_name


	def get_rating_by_id(self, movie_id):
		return self.movie_rating_dict.get(str(movie_id))

	def get_rating_by_name(self, name):
		if name not in self.people_dict:
			return "User not found"
		self.movie_name=''.join((self.people_dict[name]))
		print(name, " made a request to get the rating for the movie ", self.movie_name)
		
		id_found = ""
		for movie in self.movie_rating_dict:
			if self.get_movie_name_by_id(str(movie)) == self.movie_name:
				id_found = movie
		if id_found != "":
			rating = (self.get_rating_by_id(str(id_found)))
			self.copy_data_to_servers()
			return rating
		else:
			return None

	def get_average_rating(self, name):
		if name not in self.people_dict:
			return "User not found"
		rating = self.get_rating_by_name(name)
		self.copy_data_to_servers()
		return sum(rating) / len(rating)

	def add_rating(self, name, rating):
		if name not in self.people_dict:
			return "User not found"
		print(name, " added a rating of ", rating, " for the movie ", self.movie_name)
		found_movie = False
		for movie, movie_name1 in self.movie_name_dict.items():
			if movie_name1 == self.movie_name:
				self.movie_rating_dict[movie].append(rating)
				# print("Successfully added new rating")
				self.counter = self.counter + 1
				self.copy_data_to_servers()
				return "Successfully added new rating"
		if not found_movie:
			return "Couldn't find the movie"


def main(server_number):
	daemon = Pyro4.Daemon()
	ns = Pyro4.locateNS()
	url = daemon.register(Movie())
	ns.register("movie_server" + str(server_number), url)
	print("Listening: " , "movie_server" + str(server_number), url)
	daemon.requestLoop()


if __name__ == "__main__":
	server_number = sys.argv[1]
	main(server_number)

