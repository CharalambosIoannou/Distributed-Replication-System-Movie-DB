import csv
import Pyro4





movie_name_dict1 = {}
movie_rating_dict1 = {}
with open('movies.csv', encoding="utf8") as csv_file:
    counter=0
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:
        if (counter == 0):
            counter+=1
        else:
            movie_name_dict1[row[0]]=row[1][:-7]

with open('ratings.csv', encoding="utf8") as csv_file:
    counter=0
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:        
        if (counter == 0):
            counter+=1
        else:
            movie_id=row[1]
            if (movie_id not in movie_rating_dict1):
                movie_rating_dict1[movie_id] = [float(row[2])]
            else:
                 movie_rating_dict1[movie_id].append(float(row[2]))

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Movie:    
    def __init__(self):        
        self.movie_name_dict= movie_name_dict1
        self.movie_rating_dict= movie_rating_dict1

    def set_movie(self,name,movie_name):
        print(name , "entered the movie ", movie_name, " as input")
        self.movie_name=movie_name
        
        
    def get_name(self):
        return self.movie_name

    def get_movie_name_by_id(self,movie_id):
        return self.movie_name_dict.get(str(movie_id))

    def get_movie_name_by_name(self,movie_name):
        id_found=""
        movie=""
        for movie_id in self.movie_name_dict:
           if (self.get_movie_name_by_id(str(movie_id)) == movie_name):
               id_found=movie_id
        if (id_found !=""):
            movie= self.get_movie_name_by_id(str(id_found))
            return id_found,movie
        else:
            return None

    def get_rating_by_id(self,movie_id):
        return self.movie_rating_dict.get(str(movie_id))

    def get_rating_by_name(self,name):
        print(name, " made a request to get the rating for the movie " , self.movie_name)
        id_found=""
        movie=""
        for movie_id in self.movie_rating_dict:
           if (self.get_movie_name_by_id(str(movie_id)) == self.movie_name):
               id_found=movie_id
        if (id_found !=""):
            rating= (self.get_rating_by_id(str(id_found)))
            return rating
        else:
            return None

    def get_average_rating(self,name):
        rating=self.get_rating_by_name(name)
        return sum(rating) / len(rating)

    def add_rating(self,name, rating):
        print(name, " added a rating of ",rating," for the movie " , self.movie_name)
        found_movie=False
        for movie_id,movie_name in self.movie_name_dict.items():
            if movie_name == self.movie_name:
                self.movie_rating_dict[movie_id].append(rating)
                #print("Successfully added new rating")
                found_movie=True
                return "Successfully added new rating"
        if (found_movie==False):
            return "Couldn't find the movie"



def main():
    """
    Pyro4.Daemon.serveSimple({
    Movie: 'movie',
    }, host="0.0.0.0", port=9090, ns=False, verbose=True)
    """
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()

    url = daemon.register(Movie())

    ns.register("movie" + str(counter), url)

    daemon.requestLoop()

if __name__=="__main__":
    main()
"""
m = Movie()
m.set_movie("Toy Story")
print(m.get_rating_by_name())
print(m.add_rating(1.2))
print(m.get_rating_by_name())
"""
