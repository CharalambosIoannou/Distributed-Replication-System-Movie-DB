import uuid
import Pyro4
import Pyro4.errors
from time import sleep



class Person :
	
	
	def __init__(self) :
		self.user_id = uuid.uuid4()
		Pyro4.config.MAX_RETRIES = 0
	
	
	def retrieve_rating(self) :
		option = self.requests("GET_RATING", self.user_id, "")
		if option == "Error" :
			return "Error"
		print(option)
	
	
	def view_rating(self) :
		option = self.requests("VIEW_RATING", self.user_id, "")
		if option == "Error" :
			return "Error"
		print(option)
	
	
	def submit_rating(self) :
		inp = float(input("Enter a rating: "))
		option = self.requests("ADD_RATING", self.user_id, inp)
		if option == "Error" :
			return "Error"
		print(option)
	
	
	def update_rating(self) :
		inp_movie = input("Enter the movie name that you want to change the rating: ")
		# inp=float(input("Enter the rating you want to change: "))
		inp_1 = float(input("Enter the new rating: "))
		merged_inp = [inp_movie, inp_1]
		option = self.requests("UPDATE_RATING", self.user_id, merged_inp)
		if option == "Error" :
			return "Error"
		print(option)
	
	
	def get_avg(self) :
		option = self.requests("GET_AVG", self.user_id, "")
		if option == "Error" :
			return "Error"
		print(option)
	
	
	def set_movie_name(self) :
		inp = input("Enter name of movie: ")
		option = self.requests("SET_MOVIE", self.user_id, inp)
		while option == "No movie found" :
			inp = input("No movie found with this name. Please enter the name of a valid movie: ")
			option = self.requests("SET_MOVIE", self.user_id, inp)
		if option == "Error" :
			return "Error"
		print(option)
	
	
	def requests(self, request, user_id, user_inp) :
		data_to_send = {'request' : request, 'user_id' : user_id, 'user_inp' : user_inp}
		try :
			if request != "EXIT":
				ns = Pyro4.locateNS()
				self.server_list = ns.lookup("frontend")
				actual_server = Pyro4.Proxy(self.server_list)
				return actual_server.get_data_from_client(data_to_send)
			else:
				ns = Pyro4.locateNS()
				self.server_list = ns.lookup("frontend")
				actual_server = Pyro4.Proxy(self.server_list)
				actual_server.get_data_from_client(data_to_send)
				actual_server.shutdown()
				actual_server._pyroRelease()
				return "Exit"
		except Pyro4.errors.NamingError :
			print("Could not find the name server. Please start the server by typing 'pyro4-ns' in the command line")
			return "Error"
		except Pyro4.errors.CommunicationError :
			print("Servers are not found. Sleeping for 20 seconds and trying again...")
			sleep(20)
			print("Trying to reconnect")
			ns = Pyro4.locateNS()
			self.server_list = ns.lookup("frontend")
			
			actual_server = Pyro4.Proxy(self.server_list)
			#print("Found the Servers. Starting new Session: ")
			#main()
			return actual_server.get_data_from_client(data_to_send)


def main() :
	inp_options = ['0', '1', '2', '3', '4', '5', '6']
	person = Person()
	print("Hello,", person.user_id)
	if person.set_movie_name() == "Error" :
		return
	while True :
		print("1. Get a movie rating")
		print("2. Add a movie rating")
		print("3. Get a movie average rating")
		print("4. Set a new movie")
		print("5. View your ratings")
		print("6. Update an existing rating")
		user_inp = input("Select an option of what would you like to do: ")
		while user_inp not in inp_options or user_inp == '' :
			print("Enter valid number")
			user_inp = input("Select an option of what would you like to do: ")
		
		if user_inp == '0' :
			print("Thank you come again")
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


if __name__ == "__main__" :
	main()
