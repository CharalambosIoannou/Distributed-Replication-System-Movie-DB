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
	

	def __init__(self,number):
		self.status=""
		#self.people_dict = {}
		self.movie_name = ""
		self.movie_name_dict = movie_name_dict1
		self.movie_rating_dict = movie_rating_dict1
		self.number=number
		self.counter = 0
		self.timestamp = [0,0,0]
		
	""" Server Functions"""

	def set_servers(self, server_list):
		for s in server_list:
			self.server_list.append(Pyro4.Proxy(s))
			
	def copy_people_to_servers(self, dict):
		self.state1=dict
		return self.state1
		
		
	def copy_rating_to_servers(self, state):
		self.movie_rating_dict = state
		
	def get_people_from_servers(self):
		return self.people_dict
		
		
	def get_rating_from_servers(self):
		return self.movie_rating_dict
		
		
	def get_movie(self):
		return self.movie_name
	
	
	def get_counter(self):
		return self.counter
	
	def set_timestamp_to_servers(self):
		self.timestamp[int(self.number)-1]=self.get_counter()
		return self.timestamp
	
	def copy_timestamp_to_servers(self,state):
		self.timestamp=state
	
	def get_timestamp_from_servers(self):
		return self.timestamp
		
	def copy_data_to_servers(self):
		for s in self.server_list:
			s.copy_people_to_servers(self.people_dict)
			s.copy_rating_to_servers(self.movie_rating_dict)
			s.copy_timestamp_to_servers(self.timestamp)
		return True
	
	def get_data_from_server(self,server_number):
		print("Inside get data funct and the server number is: " , server_number)
		for i in range (0,len(self.server_list)):
			if (i == int(server_number)):
				print("Getting data from server: " , server_number)
				test = self.server_list[i].get_people_from_servers()
				self.timestamp = self.server_list[i].get_timestamp_from_servers()
				self.movie_rating_dict = self.server_list[i].get_rating_from_servers()
				self.movie_name = self.server_list[i].get_movie()
				print("People dict f: " , test)
		#print("People dict f: " , self.people_dict)
		return test,self.movie_rating_dict,self.movie_name

	
	def get_status(self):
		return self.status
	
	def set_status(self):
		self.status= random.choice(["Active","Overloaded","Offline"])
		return ''.join(self.status)
	
	
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
		#self.copy_data_to_servers()
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
		#self.copy_data_to_servers()
		return sum(rating) / len(rating)

	def add_rating(self, name, rating, timestamp_recv):
		
		print("Received Timestamp: " , timestamp_recv)
		print("Stored here timestamp: " , self.timestamp)
		self.server_with_most_recent_data = max(timestamp_recv)
		self.server_with_most_recent_data_pos = timestamp_recv.index(max(timestamp_recv))
		print("Position of the highest number in the timestamp: " , self.server_with_most_recent_data_pos )
		for i in range(0,len(timestamp_recv)):
			if (timestamp_recv[i] <= self.timestamp[i]):
				print("We need an updated version")
				self.people_dict,self.movie_rating_dict ,self.movie_name= self.get_data_from_server(self.server_with_most_recent_data_pos)
				self.timestamp=timestamp_recv
				break
		
		print("People dict: " , self.people_dict)
		print("New updated timestamp: ", self.timestamp)
		print("MOVIE NAME: " , self.movie_name)
		print(name, " added a rating of ", rating, " for the movie ", self.movie_name)
		found_movie = False

		for movie, movie_name1 in self.movie_name_dict.items():
			if movie_name1 == self.movie_name:
				self.movie_rating_dict[movie].append(rating)
				print("Successfully added new rating")
				self.counter = self.counter + 1
				self.set_list = self.set_timestamp_to_servers()
				print("Timestamp array ", self.set_list)
				print("New updated timestamp below: ", self.timestamp)
				return self.get_rating_by_name(name), self.timestamp
		if not found_movie:
			return "Couldn't find the movie"


def main(server_number):
	daemon = Pyro4.Daemon()
	ns = Pyro4.locateNS()
	url = daemon.register(Movie(str(server_number)))
	ns.register("movie_server" + str(server_number), url)
	print("Listening: " , "movie_server" + str(server_number), url)
	daemon.requestLoop()


if __name__ == "__main__":
	server_number = sys.argv[1]
	main(server_number)

