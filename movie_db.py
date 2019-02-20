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
		self.users_rating_dict = {}
		self.movie_name_dict = movie_name_dict1
		self.movie_rating_dict = movie_rating_dict1
		self.number=number
		self.counter = 0
		self.timestamp = [0,0,0]
		
	""" Server Functions"""

	def set_servers(self, server_list):
		for s in server_list:
			self.server_list.append(Pyro4.Proxy(s))
			

	def get_people_from_servers(self):
		return self.people_dict
		
		
	def get_rating_from_servers(self):
		return self.movie_rating_dict
		
		
	def get_movie_from_servers(self):
		return self.movie_name
	
	def get_user_ratings_from_servers(self):
		return self.users_rating_dict

		
	def get_counter(self):
		return self.counter
	
	
	def set_timestamp_to_servers(self):
		self.timestamp[int(self.number)-1]=self.get_counter()
		return self.timestamp
	

	def get_timestamp_from_servers(self):
		return self.timestamp
		
	def merge_dict(self,x,y):
		self.z = x.copy()
		self.z.update(y)
		return self.z
    
	def get_data_from_server(self,server_number):
		print("SERVER people dict: " ,self.people_dict)
		print("Inside get data funct and the server number is: " , server_number)
		for i in range (0,len(self.server_list)):
			if (i == int(server_number)):
				recv_people_dict = self.server_list[i].get_people_from_servers()
				self.server_list[i].get_timestamp_from_servers()
				self.movie_rating_dict = self.server_list[i].get_rating_from_servers()
				self.movie_name = self.server_list[i].get_movie_from_servers()
				user_rating_recv = self.server_list[i].get_user_ratings_from_servers()
		#self.movie_rating_dict = self.merge_dict(recv_movie_rating_dict,self.movie_rating_dict )
		print("MERGED DICTS: " , self.merge_dict(recv_people_dict,self.people_dict))
		self.people_dict = self.merge_dict(recv_people_dict,self.people_dict)
		self.users_rating_dict =  self.merge_dict(user_rating_recv,self.users_rating_dict)
		return True
	
	def get_status(self):
		return self.status
	
	def set_status(self):
		self.status= random.choice(["Active","Overloaded","Offline"])
		return ''.join(self.status)
	
	def copy_to_servers(self,timestamp_recv):
		print("Received Timestamp: " , timestamp_recv)
		print("Stored here timestamp: " , self.timestamp)
		self.server_with_most_recent_data = max(timestamp_recv)
		self.server_with_most_recent_data_pos = timestamp_recv.index(max(timestamp_recv))
		print("Position of the highest number in the timestamp: " , self.server_with_most_recent_data_pos )
		print("NOW WE ARE ON SERVER: " , int(self.number)-1)
		for i in range(0,len(timestamp_recv)):
			if (timestamp_recv == [0,0,0] and i != int(self.number)-1):
				print("First time but We need an updated version and we will get values from server: ",i)
				self.get_data_from_server(i)
				self.timestamp=timestamp_recv
				break
			elif (timestamp_recv[i] > self.timestamp[i] and i != int(self.number)-1):
				print("We need an updated version and we will get values from server: ",i)
				self.get_data_from_server(i)
				self.timestamp=timestamp_recv
				break
		return True
	
		
		
	""" Movie Functions"""
	
	def get_movie_name_by_id(self, movie_id):
		return self.movie_name_dict.get(str(movie_id))

	def set_movie(self, name, movie_name,timestamp_recv):
		self.copy_to_servers(timestamp_recv)
		if (movie_name not in self.movie_name_dict.values()):
			print("No movie found")
			return "No movie found",self.timestamp
		else:
			
			if name not in self.people_dict:
				print("First time setting movie")
				self.people_dict[name] = [movie_name]
				self.movie_name = movie_name
				print(name, "entered the movie ", movie_name, " as input")
			else:
				print("Choosing different movie")
				for key in self.people_dict.keys():
					if key == name:
						self.people_dict[key] = movie_name
			self.counter = self.counter + 1
			self.set_list = self.set_timestamp_to_servers()
			return movie_name, self.timestamp
	
	def view_rating(self,name,timestamp_recv):
		self.copy_to_servers(timestamp_recv)
		print("These are the your ratings: ")
		return self.users_rating_dict.values(),self.timestamp
		
		
	def update_rating(self,name,list_rating,timestamp_recv):
		print("These are the your ratings: ")
		for iterate_elements in self.users_rating_dict.values():
			print(iterate_elements)
		return
		

	def get_rating_by_id(self, movie_id):
		return self.movie_rating_dict.get(str(movie_id))

	def get_rating_by_name(self, name,timestamp_recv):
		self.copy_to_servers(timestamp_recv)
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
			return rating,self.timestamp
		else:
			return None,self.timestamp

	def get_average_rating(self, name,timestamp_recv):
		self.copy_to_servers(timestamp_recv)
		if name not in self.people_dict:
			return "User not found"
		rating = self.get_rating_by_name(name,timestamp_recv)
		return sum(rating) / len(rating) , self.timestamp

	def add_rating(self, name, rating, timestamp_recv):
		self.copy_to_servers(timestamp_recv)
		print("People dict: " , self.people_dict)
		print("New updated timestamp: ", self.timestamp)
		print("NAME: ", name)
		self.movie_name=''.join((self.people_dict[name]))
		print("MOVIE NAME: " , self.movie_name)
		print(name, " added a rating of ", rating, " for the movie ", self.movie_name)
		found_movie = False

		for movie, movie_name1 in self.movie_name_dict.items():
			if movie_name1 == self.movie_name:
				self.movie_rating_dict[movie].append(rating)
				self.users_rating_dict[name]=rating
				print("Successfully added new rating")
				self.counter = self.counter + 1
				self.set_list = self.set_timestamp_to_servers()
				print("Timestamp array ", self.set_list)
				print("New updated timestamp below: ", self.timestamp)
				return self.get_rating_by_name(name,timestamp_recv), self.timestamp
		if not found_movie:
			return "Couldn't find the movie"


def main(server_number):
	try:
		daemon = Pyro4.Daemon()
		ns = Pyro4.locateNS()
		url = daemon.register(Movie(str(server_number)))
		ns.register("movie_server" + str(server_number), url)
		print("Listening: " , "movie_server" + str(server_number), url)
		daemon.requestLoop()
	except Pyro4.errors.NamingError:
		print("Could not find the name server. Please start the server by typing 'pyro4-ns' in the command line")
		return "Error"


if __name__ == "__main__":
	server_number = sys.argv[1]
	main(server_number)

