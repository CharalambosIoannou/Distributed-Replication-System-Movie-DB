import sys

class Person:
    def __init__(self,name):
        self.name=name

    def visit(self,movie):
        print("Hello,", self.name)
        print("1. Get a movie rating")
        print("2. Add a movie rating")
        print("3. Get a movie average rating")
        user_inp = int(input("Select an option of what would you like to do: "))
        if (user_inp == 1):
            self.retrieve_rating(movie)
        if (user_inp == 2):
            self.submit_rating(movie)
        if (user_inp == 3):
            self.get_avg(movie)
              
        print("Thank you come again")

    def retrieve_rating(self,movie):
        print("Rating for movie ", movie.get_name() ,": ", movie.get_rating_by_name())
        return movie.get_rating_by_name()


    def submit_rating(self,movie):
        inp=float(input("Enter a rating: "))
        movie.add_rating(inp)
        #print("Rating for movie ", movie.get_name() ,": ", movie.get_rating_by_name())
                
    def get_avg(self,movie):
        print(movie.get_average_rating())
