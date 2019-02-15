import random
import string
import sys
import json

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

    def visit(self,movie):
        print("Hello,", self.userid)
        self.set_movie_name(self.userid,movie)
        print("1. Get a movie rating")
        print("2. Add a movie rating")
        print("3. Get a movie average rating")
        user_inp = int(input("Select an option of what would you like to do: "))
        if (user_inp == 1):
            self.retrieve_rating(self.userid,movie)
        if (user_inp == 2):
            self.submit_rating(self.userid,movie)
        if (user_inp == 3):
            self.get_avg(self.userid,movie)
              
        print("Thank you come again")

    def retrieve_rating(self,name,movie):
        print("Rating for movie ", movie.get_name() ,": ", movie.get_rating_by_name(name))
        return movie.get_rating_by_name(name)


    def submit_rating(self,name,movie):
        inp=float(input("Enter a rating: "))
        movie.add_rating(name,inp)
        #print("Rating for movie ", movie.get_name() ,": ", movie.get_rating_by_name())
                
    def get_avg(self,name,movie):
        print(movie.get_average_rating(name))
        
    def set_movie_name(self,name,movie):
        inp=input("Enter name of movie: ")
        movie.set_movie(self.name,inp)

    def requests(self):
