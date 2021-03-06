import uuid
import Pyro4
import Pyro4.errors
from time import sleep
import sys


class Person :
	def __init__(self) :
		#connect to the front end server
		self.user_id = uuid.uuid4()
		self.movie_name=""
		counter = 1
		while counter!=5:
			try:
				ns = Pyro4.locateNS()
				self.server = ns.lookup("frontend")
				self.actual_server = Pyro4.Proxy(self.server)
				break
			except Pyro4.errors.CommunicationError:
				print("Attempt ", counter , " out of 5")
				print("Servers are not found. Sleeping for 20 seconds and trying again...")
				sleep(20)
				counter = counter + 1
			
			except Pyro4.errors.NamingError:
				print("Name server could not found. Start name server by opening a terminal and typing 'pyro4-ns'..")
				exit()
			except Pyro4.errors.ConnectionClosedError:
				print("Attempt ", counter , " out of 5")
				print("Servers are not found. Sleeping for 20 seconds and trying again...")
				sleep(20)
				ns = Pyro4.locateNS()
				self.server = ns.lookup("frontend")
				self.actual_server = Pyro4.Proxy(self.server)
				counter = counter +1
				self.actual_server.connect()
				
		
	
	def retrieve_rating(self) :
		response = self.requests("GET_RATING", self.user_id, "")
		if response == "Error" :
			return "Error"
		print(response)
	
	
	def view_rating(self) :
		response = self.requests("VIEW_RATING", self.user_id, "")
		if response == "Error" :
			return "Error"
		print(response)
	
	
	def submit_rating(self) :
		inp = (input("Enter a rating: "))
		while (inp == "" or float(inp) <0 or float(inp) >5):
			print("Rating should be between 0 and 5")
			inp = (input("Enter a rating: "))
		inp = float(inp)
		response = self.requests("ADD_RATING", self.user_id, inp)
		if response == "Error" :
			return "Error"
		print(response)
	
	
	def update_rating(self) :
		inp_movie = input("Enter the movie name that you want to change the rating: ")
		inp_1 = (input("Enter the new rating: "))
		inp_1 = float(inp_1)
		merged_inp = [inp_movie, inp_1]
		while (inp_1 == "" or float(inp_1) <0 or float(inp_1) >5 ):
			print("Rating should be between 0 and 5")
			inp_1 = (input("Enter a rating: "))
		inp_1 = float(inp_1)
		merged_inp = [inp_movie, inp_1]
		response = self.requests("UPDATE_RATING", self.user_id, merged_inp)
		while response == "No movie found" :
			inp_movie = input("No movie found with this name. Please enter the name of a valid movie: ")
			merged_inp = [inp_movie, inp_1]
			response = self.requests("UPDATE_RATING", self.user_id, merged_inp)
		if response == "Error":
			return "Error"
		if (response == "No rating added yet"):
			print("You have to add a rating first")
			return
		if (response == "Rating added again" ):
			print("Update a rating with a value you never entered again")
			return
		print(response)
	
	
	def get_avg(self) :
		response = self.requests("GET_AVG", self.user_id, "")
		if response == "Error" :
			return "Error"
		print(response)
	
	
	def set_movie_name(self) :
		inp = input("Enter name of movie: ")
		response = self.requests("SET_MOVIE", self.user_id, inp)
		while response == "No movie found" :
			inp = input("No movie found with this name. Please enter the name of a valid movie: ")
			response = self.requests("SET_MOVIE", self.user_id, inp)
		if response == "Error" :
			return "Error"
		self.movie_name=response
		print(response)
	
	#this function is called for every client request and this is the case in order to sent the data to the front end
	def requests(self, request, user_id, user_inp) :
		data_to_send = {'request' : request, 'user_id' : user_id, 'user_inp' : user_inp, 'movie_name' : self.movie_name }
		counter = 1
		while counter != 5:
			try:
				if request != "EXIT":
					return self.actual_server.get_data_from_client(data_to_send)
				else:
					self.actual_server.get_data_from_client(data_to_send)
					self.actual_server.shutdown()
					self.actual_server._pyroRelease()
					return "Exit"
			except Pyro4.errors.ConnectionClosedError:
				print("Servers are not found. Sleeping for 20 seconds and trying again...")
				sleep(20)
				try:
					ns = Pyro4.locateNS()
					self.server = ns.lookup("frontend")
					self.actual_server = Pyro4.Proxy(self.server)
					counter = counter +1
					self.actual_server.connect()
				except Pyro4.errors.CommunicationError:
					print("Could not establish connection. Exiting program")
					exit()
			except Pyro4.errors.CommunicationError:
				print("Servers are not found. Sleeping for 20 seconds and trying again...")
				sleep(20)
				ns = Pyro4.locateNS()
				self.server = ns.lookup("frontend")
				self.actual_server = Pyro4.Proxy(self.server)
				counter = counter + 1
				self.actual_server.connect()
		print("No connection could be established")
		exit()

			
			


def main() :
	inp_options = ['0', '1', '2', '3', '4', '5', '6','100']
	person = Person()
	print("Hello,", person.user_id)
	if person.set_movie_name() == "Error" :
		return
	while True :
		print("1. Get a movie rating")
		print("2. Add a movie rating")
		print("3. Get a movie average rating")
		print("4. Change currently selected movie")
		print("5. View your ratings")
		print("6. Update an existing rating")
		print("0. Close current client connection")
		print("100. Close all active servers (Use only in ONE client at the very end when you need to close everything.)")
		user_inp = input("Select an option of what would you like to do: ")
		while user_inp not in inp_options or user_inp == '' :
			print("Enter valid number")
			user_inp = input("Select an option of what would you like to do: ")
		if user_inp == '100' :
			print("Terminating Connection and closing everything.")
			option = person.requests("EXIT", person.user_id, "")
			return option
		else :
			if user_inp == '1' :
				if person.retrieve_rating() == "Error" :
					return
			elif user_inp == '2' :
				if person.submit_rating() == "Error" :
					return
			elif user_inp == '3' :
				if person.get_avg() == "Error" :
					return
			elif user_inp == '4' :
				if person.set_movie_name() == "Error" :
					return
			elif user_inp == '5' :
				if person.view_rating() == "Error" :
					return
			elif user_inp == '6' :
				if person.update_rating() == "Error" :
					return
			elif user_inp == '0':
				print("Terminating Connection.")
				return


if __name__ == "__main__" :
	main()
