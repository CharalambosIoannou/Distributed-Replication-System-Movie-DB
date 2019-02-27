import csv
import random
import sys
from collections import defaultdict
import Pyro4
import json



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
	

	def __init__(self,number,daemon):
		self.daemon=daemon
		try:
			self.rating_tuples , self.people_dict = self.read_file()
			if (self.people_dict == ""):
				self.rating_tuples = []
			else:
				for i in self.rating_tuples:
					i[2]=float(i[2])
		except FileNotFoundError:
			self.rating_tuples = []
			
		print("1: ", self.rating_tuples)
		print("2: ", self.people_dict)
			
		self.status=""
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
			

	def get_people_from_servers(self):
		return self.people_dict
		
		
	def get_rating_tuples(self):
		return self.rating_tuples
	
		
	def get_counter(self):
		return self.counter
	
	
	def set_timestamp_to_servers(self):
		self.timestamp[int(self.number)-1]=self.get_counter()
		return self.timestamp
	

	@Pyro4.oneway
	def shutdown(self):
		print("Shutting down")
		self.daemon.shutdown()
		
		
	def get_data_from_server(self,server_number):
		tmp = {}
		print("Inside get data funct and the server number is: " , server_number)
		for i in range (0,len(self.server_list)):
			if (i == int(server_number)):
				self.recv_people_dict = self.server_list[i].get_people_from_servers()
				self.copy_tuples = self.server_list[i].get_rating_tuples()
				
		update_elems = [x for x in self.copy_tuples if not x in self.rating_tuples]
		self.rating_tuples = self.rating_tuples + update_elems
		
		if (len(self.people_dict) == 0):
			self.people_dict=self.recv_people_dict
		else:
			tmp={**self.people_dict,**self.recv_people_dict}
			self.people_dict = tmp
		
		print("BEFORE DEL PEOPLE DICT: " , self.rating_tuples)
		if (len(self.rating_tuples) != 0):
			del_elems=[]
			for j in self.rating_tuples:
				if (j[3] == 'del'):
					del_elems.append([j[0],j[1],j[2],'add'])

				
			print("del elems: " , del_elems)
			
			for k in del_elems:
				if k in self.rating_tuples:
					self.rating_tuples.remove(k)
			
			
		print("AFTER DEL PEOPLE DICT: " , self.rating_tuples)

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
		self.counter=self.server_with_most_recent_data
		for i in range(0,len(timestamp_recv)):
			if (timestamp_recv == [0,0,0] and i != int(self.number)-1):
				print("First time but We need an updated version and we will get values from server: ",i)
				self.get_data_from_server(i)
				self.timestamp=timestamp_recv
				break
			elif (self.server_with_most_recent_data > self.timestamp[i] and i ==self.server_with_most_recent_data_pos):
				print("We need an updated version and we will get values from server: ",i)
				self.get_data_from_server(i)
				self.timestamp=timestamp_recv
				break
		self.timestamp=timestamp_recv
		return True
	
		
	def write(self):
		with open("tuples.csv", "w",newline="") as f:
		    writer = csv.writer(f)
		    writer.writerows(self.rating_tuples)
		text_file1 = open("people dict.txt", "w")
		json.dump(self.people_dict,text_file1)
		
   
		
	def read_file(self):
		with open("tuples.csv", 'r') as f:
			data = list(csv.reader(f, delimiter=','))
		file_read1 = open("people dict.txt", "r")
		dict = json.load(file_read1)
		return data , dict
		
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
				self.movie_name = movie_name
			self.counter = self.counter + 1
			self.set_list = self.set_timestamp_to_servers()
			self.write()
			return movie_name, self.timestamp
	
	def view_rating(self,name,timestamp_recv):
		self.copy_to_servers(timestamp_recv)
		temp_rating= []
		print("These are the your ratings: ")
		for i in self.rating_tuples:
			if (i[0] == name and i[3] != 'del'):
				temp_rating.append([i[1],": ",i[2]])
		res= ' '.join(str(r) for v in temp_rating for r in v)
		self.set_list = self.set_timestamp_to_servers()
		self.write()
		return res,self.timestamp
		
		
	def update_rating(self,name,list_rating,timestamp_recv):
		movie_to_change=list_rating[0]
		#self.rating_to_change = list_rating[1]
		self.new_rating = list_rating[1]
		print("These are the your ratings: ")
		print(self.view_rating(name,timestamp_recv))
		count_in_list = 0
		for i in self.rating_tuples:
			if (i[0] == name and i[1]==movie_to_change ):
				self.rating_to_change = i[2]
				self.rating_tuples.append([name, i[1], self.rating_to_change ,'del'])
				self.rating_tuples[count_in_list] = [name, i[1], self.new_rating,'add']
				
				#self.rating_tuples.append()
				break
			count_in_list = count_in_list + 1
		print("new user rat dict: ",self.rating_tuples)
		self.counter = self.counter + 1
		self.set_list = self.set_timestamp_to_servers()
		res= "Successfully changed rating of movie ", movie_to_change," from ", self.rating_to_change, " to ", self.new_rating
		self.write()
		return res,self.timestamp
		

	def get_rating_by_id(self, movie_id):
		return self.movie_rating_dict.get(str(movie_id))

	def get_rating_by_name(self, name,timestamp_recv):
		
		self.copy_to_servers(timestamp_recv)
		print("DICTIONARYYYYYYY: " , self.rating_tuples)
		test_list=[]
		if name not in self.people_dict:
			return "User not found",self.timestamp
		else:
			for key in self.people_dict.keys():
					if key == name:
						current_movie_selected = ''.join(self.people_dict[key])
			
		print(name, " made a request to get the rating for the movie ", current_movie_selected)
		id_found = ""
		for movie in self.movie_rating_dict:
			if self.get_movie_name_by_id(str(movie)) == current_movie_selected:
				id_found = movie
		if id_found != "":
			rating = (self.get_rating_by_id(str(id_found)))
			for i in self.rating_tuples:
					if (i[1] == current_movie_selected and i[3] != 'del'):
						test_list.append(i[2])
			rating = rating + test_list
			self.set_list = self.set_timestamp_to_servers()
			self.write()
			return sorted(rating),self.timestamp
		else:
			return None,self.timestamp

	def get_average_rating(self, name,timestamp_recv):
		self.copy_to_servers(timestamp_recv)
		if name not in self.people_dict:
			return "User not found"
		rating,self.timestamp = self.get_rating_by_name(name,timestamp_recv)
		print("AVERAGE: ",rating)
		avg= "Average: " , sum(rating) / len(rating)
		self.set_list = self.set_timestamp_to_servers()
		self.write()
		return  avg , self.timestamp

	def add_rating(self, name, rating, timestamp_recv):
		#self.users_rating_dict.setdefault(key, []).append(value)
		self.copy_to_servers(timestamp_recv)
		current_movie_selected=""
		for key in self.people_dict.keys():
			if key == name:
				current_movie_selected = ''.join(self.people_dict[key])
		for i in self.rating_tuples:
			if (name == i[0] and i[1] == current_movie_selected):
				print("HERE")
				return "Rating already added" ,self.timestamp
		print(name, " added a rating of ", rating, " for the movie ", current_movie_selected)
		found_movie = False
		
		for movie, movie_name1 in self.movie_name_dict.items():
			if movie_name1 == current_movie_selected:
				self.rating_tuples.append([name, movie_name1, rating,'add'])
				print("Successfully added new rating")
				self.counter = self.counter + 1
				self.set_list = self.set_timestamp_to_servers()
				print("New updated timestamp below: ", self.timestamp)
				self.write()
				return "Successfully added new rating", self.timestamp
	


def main(server_number):
	try:
		daemon = Pyro4.Daemon()
		ns = Pyro4.locateNS()
		m = Movie(str(server_number),daemon)
		url = daemon.register(m)
		ns.register("movie_server" + str(server_number), url)
		print("Listening: " , "movie_server" + str(server_number), url)
		daemon.requestLoop()
		print("Exit loop")
		daemon.close()
		m.people_dict = {}
		m.rating_tuples = []
		m.write()
		print("Daemon closed")
	except Pyro4.errors.NamingError:
		print("Could not find the name server. Please start the server by typing 'pyro4-ns' in the command line")
		return "Error"


if __name__ == "__main__":
	server_number = sys.argv[1]
	main(server_number)

