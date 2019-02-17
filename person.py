import random
import string
import uuid
import Pyro4


class Person:
	def __init__(self):
		self.user_id=uuid.uuid4()
		
		
	def retrieve_rating(self):
		option= self.requests("GET_RATING", self.user_id, "")
		print(option)


	def submit_rating(self):
		inp=float(input("Enter a rating: "))
		option= self.requests("ADD_RATING", self.user_id, inp)
		print(option)

	def get_avg(self):
		option= self.requests("GET_AVG", self.user_id, "")
		print(option)

	def set_movie_name(self):
		inp=input("Enter name of movie: ")
		option= self.requests("SET_MOVIE", self.user_id, inp)
		print(option)

	def requests(self, request, user_id, user_inp):
		data_to_send = {'request' : request, 'user_id' : user_id, 'user_inp' : user_inp}
		ns = Pyro4.locateNS()
		self.server_list = ns.lookup("frontend")
		actual_server = Pyro4.Proxy(self.server_list)
		return actual_server.get_data_from_client(data_to_send)
		


def main():
	person = Person()
	print("Hello,", person.user_id)
	person.set_movie_name()
	while True:
		print("1. Get a movie rating")
		print("2. Add a movie rating")
		print("3. Get a movie average rating")
		print("4. Set a new movie")
		user_inp = int(input("Select an option of what would you like to do: "))
		if (user_inp == 0):
			print ("Thank you come again")
			return
		else:
			if (user_inp == 1):
				person.retrieve_rating()
			elif (user_inp == 2):
				person.submit_rating()
			elif (user_inp == 3):
				person.get_avg()
			elif (user_inp == 4):
				person.set_movie_name()

if __name__== "__main__":
	main()
