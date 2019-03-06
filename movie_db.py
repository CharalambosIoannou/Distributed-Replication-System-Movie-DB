import csv
import random
import sys
from collections import defaultdict
import Pyro4
import json
import time


#Read the CSV files and place them in a dictionary
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
	
	#In order to make the system robust i read data (list and dictionary) from file in case the servers closed unexpectedly
	#If there are no files or the files are empty then the list and dictionary are initialized to be empty
	#If the files are found and have data in them then the list and dictionary are set to be the values that i read from the text and csv files
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
		self.org_time=time.time()

		
	""" Server Functions"""
	#This function empties the list of connected servers. This is the case when the servers are force closed and then re opened.
	#If they are reopened then they have a different pyro object. So i empty the existing list and update it with the new Pyro object
	def empty_servers(self):
		self.server_list = []
		
	#This fucntion sends gossip to the server that the client is connected to. It is used for querries only. It sends gossip only if the time difference between
	#the start time of the server and the current time is an even number. This happends because gossip architecure sends updates periodically and not every time
	def gossip(self,timestamp_recv):
		new_time=time.time()
		diff = int(new_time - self.org_time)
		print("DIFF: ", diff)
		active_servers=[]
		goss = False
		print("Received Timestamp: " , timestamp_recv)
		print("Stored here timestamp: " , self.timestamp)
		self.server_with_most_recent_data = max(timestamp_recv) #gets data from the server that has the most updates
		self.server_with_most_recent_data_pos = timestamp_recv.index(max(timestamp_recv))
		print("Position of the highest number in the timestamp: " , self.server_with_most_recent_data_pos )
		print("NOW WE ARE ON SERVER: " , int(self.number)-1)
		attempts=0
		is_active=False
		for i in range (0,len(self.server_list)):
			if (i == self.server_with_most_recent_data_pos):
				while (is_active == False):
					if (attempts==10): #attempt to reconnect to the server with the most updates 10 times by changing the status of the server arbitralily 10 times
						print("No updates received") #status is offline for 10 times so no updates are sent/received
						
						return "No updates received"
					else:
						self.server_list[i].set_status()
						print("new stat: ",self.server_list[i].get_status())
						if (self.server_list[i].get_status() != "Offline"): #get data only if the server is active or overloaded. If its offline then no data are send
							self.counter=self.server_with_most_recent_data
							is_active=True
						else:
							attempts = attempts + 1

		for i in range(0,len(timestamp_recv)):
			if (timestamp_recv == [0,0,0] and i != int(self.number)-1 and diff %2 == 0): #if the difference of the two times are an even number then the updates are sent. This is the case because i send data periodically
				print("GOSSIP TIME")
				print("First time but We need an updated version and we will get values from server: ",i)
				self.get_data_from_server(i)
				self.timestamp=timestamp_recv
				goss=True
				break
			elif (i ==self.server_with_most_recent_data_pos and diff %2 == 0):
				"""self.server_with_most_recent_data > self.timestamp[i] and """
				print("GOSSIP TIME")
				print("We need an updated version and we will get values from server: ",i)
				self.get_data_from_server(i)
				self.timestamp=timestamp_recv
				goss=True
				break
			else:
				print("No updates received")
				self.timestamp=timestamp_recv
				goss=False
			
		if (goss == False):
			return "No updates received"
		
		
	#Insert the connected servers in a list in order to iterate through them later on and get the most recent updates and also their status
	def set_servers(self, server_list):
		for s in server_list:
			self.server_list.append(Pyro4.Proxy(s))
			
	#These are get and set methods where many variables are assigned values and i can access those values from the frontend file or the server file
	def get_people_from_servers(self):
		return self.people_dict
		
		
	def get_rating_tuples(self):
		return self.rating_tuples
	
		
	def get_counter(self):
		return self.counter
	
	
	def set_timestamp_to_servers(self):
		self.timestamp[int(self.number)-1]=self.get_counter()
		return self.timestamp
	
	#this function shuts down the server. This is done in order to have a clean shutdown of the servers, get out of the daemon request loop and empty the files that i use to store data for backup purposes in case a server closes down unexpectedly
	@Pyro4.oneway
	def shutdown(self):
		print("Shutting down")
		self.daemon.shutdown()
		
	#this function gets data from the server that has the most updates
	def get_data_from_server(self,server_number):
		tmp = {}
		print("Inside get data funct and the server number is: " , server_number)
		print("SERVER LIST: ", self.server_list)
		for i in range (0,len(self.server_list)):
			if (i == int(server_number)):
				self.recv_people_dict = self.server_list[i].get_people_from_servers()
				self.copy_tuples = self.server_list[i].get_rating_tuples()
				
		#i join the list that the server aldready has with the list that i receive from the server with the most updates. If the data are alraedy in the list then they are not added again
		update_elems = [x for x in self.copy_tuples if not x in self.rating_tuples]
		self.rating_tuples = self.rating_tuples + update_elems
		
		#here i find the rating that the user changed and change its value to del so that it is not displayed to the user when the ratings are requested
		for k in range (0,len(self.rating_tuples)):
			element1= self.rating_tuples[k]
			for l in range (1,len(self.rating_tuples)):
				element2= self.rating_tuples[l]
				if (element2[0] == element1[0] and element2[1] == element1[1] and element2[2] == element1[2] and element1[3] == 'add' and element2[3]=='del'):
					element1[3]='del'
					
		if (len(self.people_dict) == 0):
			self.people_dict=self.recv_people_dict
		else:
			tmp={**self.people_dict,**self.recv_people_dict} #here i join the dicitonary that i receive from the server with the most updates with the dictionary that is already found in the current server
			self.people_dict = tmp
		
		print("AFTER DEL PEOPLE DICT: " , self.rating_tuples)
		return True
	
	def get_status(self):
		return self.status
	
	#setting the status of the server arbitralily. I choose a status at random from the list
	def set_status(self):
		self.status= random.choice(["Active","Overloaded","Offline"])
		return ''.join(self.status)
	

	#This fucntion sends gossip to the server that the client is connected to. It is used for updates only. It sends forced updates
	#This is done for updates so that the user can update data instalty without waiting for gossip
	def copy_to_servers(self,timestamp_recv):
		active_servers=[]
		print("Received Timestamp: " , timestamp_recv)
		print("Stored here timestamp: " , self.timestamp)
		self.server_with_most_recent_data = max(timestamp_recv)
		self.server_with_most_recent_data_pos = timestamp_recv.index(max(timestamp_recv))
		print("Position of the highest number in the timestamp: " , self.server_with_most_recent_data_pos )
		print("NOW WE ARE ON SERVER: " , int(self.number)-1)
		attempts=0
		is_active=False
		for i in range (0,len(self.server_list)):
			if (i == self.server_with_most_recent_data_pos):
				while (is_active == False):
					if (attempts==10):
						print("No updates received")
						
						return "No updates received"
					else:
						self.server_list[i].set_status()
						print("new stat: ",self.server_list[i].get_status())
						if (self.server_list[i].get_status() != "Offline"):
							self.counter=self.server_with_most_recent_data
							is_active=True
						else:
							attempts = attempts + 1

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
	
	#i write data to file for backup purposes if a server force closes unexpectetly
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
	
	#User sets a movie. Either for the first time or changes the existing movie
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
		
	
	def view_rating(self,name,timestamp_recv,movie):
		#self.copy_to_servers(timestamp_recv)
		gos = self.gossip(timestamp_recv)
		if (gos != "No updates received"):
			self.set_list = self.set_timestamp_to_servers()
		temp_rating= []
		print("These are your ratings: ")
		for i in self.rating_tuples:
			if (i[0] == name and i[3] !='del'):
				temp_rating.append([i[1],": ",i[2]])
		print("temp: ", temp_rating)
		if (len(temp_rating) == 0):
			res="No ratings added by this user"
		else:
			res= ' '.join(str(r) for v in temp_rating for r in v)
		self.set_list = self.set_timestamp_to_servers()
		self.write()
		return res,self.timestamp
		
	#change an existing rating that a user inputed
	def update_rating(self,name,list_rating,timestamp_recv,movie):
		self.copy_to_servers(timestamp_recv)
		movie_to_change=list_rating[0]
		movie_exists=False
		print("here1")
		view_rat , time=self.view_rating(name,timestamp_recv,movie)
		print("rat: ", view_rat)
		if (view_rat== "No ratings added by this user"):
			return "No rating added yet",self.timestamp
		
		for i in self.rating_tuples:
			if (i[1] == movie_to_change and i[2]==list_rating[1] and name == i[0]):
				return "Rating added again",self.timestamp
			
		print("here2")
		for i in self.rating_tuples:
			if (i[1] == movie_to_change and i[3]=='add' and name == i[0]):
				movie_exists=True
				break
			else:
				movie_exists=False
		print("here3")
		if (movie_exists == True):
			#self.rating_to_change = list_rating[1]
			self.new_rating = list_rating[1]
			print("These are your ratings: ")
			print("1")
			count_in_list = 0
			for i in self.rating_tuples:
				if (i[0] == name and i[1]==movie_to_change and i[3] !='del' ):
					self.rating_to_change = i[2]
					self.rating_tuples.append([name, i[1], self.rating_to_change,'del' ])
					self.rating_tuples[count_in_list] = [name, i[1], self.new_rating,'add']
					#self.rating_tuples[count_in_list] = [name, i[1], self.rating_to_change,'del']
					#self.rating_tuples.append([name, i[1], self.new_rating,'add'])
					break
	
				count_in_list = count_in_list + 1
			print("new user rat dict: ",self.rating_tuples)
			self.counter = self.counter + 1
			self.set_list = self.set_timestamp_to_servers()
			res= "Successfully changed rating of movie ", movie_to_change#," from ", self.rating_to_change, " to ", self.new_rating
			self.write()
			return res,self.timestamp
		else:
			return "No movie found",self.timestamp
		

	def get_rating_by_id(self, movie_id):
		return self.movie_rating_dict.get(str(movie_id))

	def get_rating_by_name(self, name,timestamp_recv,movie):
		gos = self.gossip(timestamp_recv)
		if (gos != "No updates received"):
			self.set_list = self.set_timestamp_to_servers()
		
		test_list=[]
		if name not in self.people_dict:
			self.people_dict[name] = [movie]
		current_movie_selected = movie
		print(name, " made a request to get the rating for the movie ", current_movie_selected)
		id_found = ""
		for movie in self.movie_rating_dict:
			if self.get_movie_name_by_id(str(movie)) == current_movie_selected:
				id_found = movie
		if id_found != "":
			rating = (self.get_rating_by_id(str(id_found)))
			for i in self.rating_tuples:
					if (i[1] == current_movie_selected and i[3] !='del'):
						test_list.append(i[2])
			rating = rating + test_list
			self.write()
			return sorted(rating),self.timestamp
		else:
			return None,self.timestamp

	def get_average_rating(self, name,timestamp_recv,movie):
		#self.copy_to_servers(timestamp_recv)
		gos = self.gossip(timestamp_recv)
		if (gos != "No updates received"):
			self.set_list = self.set_timestamp_to_servers()
		if name not in self.people_dict:
			self.people_dict[name] = [movie]
			#return "User not found"
		rating,self.timestamp = self.get_rating_by_name(name,timestamp_recv,movie)
		print("AVERAGE: ",rating)
		avg= "Average: " , round (sum(rating) / len(rating),2)
		self.set_list = self.set_timestamp_to_servers()
		self.write()
		return  avg , self.timestamp

	def add_rating(self, name, rating, timestamp_recv,movie):
		#self.users_rating_dict.setdefault(key, []).append(value)
		self.copy_to_servers(timestamp_recv)
		current_movie_selected=movie
		for i in self.rating_tuples:
			if (name == i[0] and i[1] == current_movie_selected):
				return "This user has already added a rating" ,self.timestamp
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
		print("Exit loop") #when the client disconnectes the files that the data are saved to are cleared
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

