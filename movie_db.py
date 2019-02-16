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
	people = {}
	servers = []

	def __init__(self):
		self.movie_name_dict = movie_name_dict1
		self.movie_rating_dict = movie_rating_dict1
		self.status = "Active"

	def set_servers(self, servers):
		for uri in servers:
			self.servers.append(Pyro4.Proxy(uri))
			
	def set_state_people(self, state):
		print("My state has been set to: ", str(state))
		self.people = state
		
		
	def set_state_rating(self, state):
		#print("My state has been set to: ", str(state))
		self.movie_rating_dict = state
	
	def update_backup_servers(self):
		for s in self.servers:
			s.set_state_people(self.people)
			s.set_state_rating(self.movie_rating_dict)
			print("Set state of remote server")
		return True
	
	def get_movie_name_by_id(self, movie_id):
		return self.movie_name_dict.get(str(movie_id))

	def set_movie(self, name, movie_name):

		print(name, "entered the movie ", movie_name, " as input")
		self.movie_name = movie_name
			
		if name not in self.people:
			self.create_user(name,self.movie_name)
		self.update_backup_servers()
		return movie_name


	def get_rating_by_id(self, movie_id):
		return self.movie_rating_dict.get(str(movie_id))

	def get_rating_by_name(self, name):
		if name not in self.people:
			return "User not found"
		self.movie_name=''.join((self.people[name]))
		print(name, " made a request to get the rating for the movie ", self.movie_name)
		
		id_found = ""
		for movie in self.movie_rating_dict:
			if self.get_movie_name_by_id(str(movie)) == self.movie_name:
				id_found = movie
		if id_found != "":
			rating = (self.get_rating_by_id(str(id_found)))
			self.update_backup_servers()
			return rating
		else:
			return None

	def get_average_rating(self, name):
		if name not in self.people:
			return "User not found"
		rating = self.get_rating_by_name(name)
		self.update_backup_servers()
		return sum(rating) / len(rating)

	def add_rating(self, name, rating):
		if name not in self.people:
			return "User not found"
		print(name, " added a rating of ", rating, " for the movie ", self.movie_name)
		
		found_movie = False
		for movie, movie_name in self.movie_name_dict.items():
			if movie_name == self.movie_name:
				self.movie_rating_dict[movie].append(rating)
				# print("Successfully added new rating")
				self.update_backup_servers()
				return "Successfully added new rating"
		if not found_movie:
			return "Couldn't find the movie"


	def get_status(self):
		result= random.choice(["Active","Overloaded","Offline"])
		return ''.join(result)
	
	
	def create_user(self, userid,movie):
		self.people[userid] = [movie]
	



def main(counter):
	daemon = Pyro4.Daemon()
	ns = Pyro4.locateNS()
	url = daemon.register(Movie())
	ns.register("movie_server" + str(counter), url)
	print("Listening: " , "movie_server" + str(counter), url)
	daemon.requestLoop()


if __name__ == "__main__":
	counter_val = sys.argv[1]
	main(counter_val)

