import csv

movie_name_dict1 = {}
movie_rating_dict1 = {}
with open('movies.csv', encoding="utf8") as csv_file:
    counter=0
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:
        if (counter == 0):
            counter+=1
        else:
            movie_name_dict1[row[0]]=row[1]

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
                 


class Movie:    
    def __init__(self,movie_name):
        self.movie_name=movie_name
        self.movie_name_dict= movie_name_dict1
        self.movie_rating_dict= movie_rating_dict1
        
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

    def get_rating_by_name(self):
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

    def get_average_rating(self):
        rating=self.get_rating_by_name()
        return sum(rating) / len(rating)

    def add_rating(self, rating):
        found_movie=False
        for movie_id,movie_name in self.movie_name_dict.items():
            if movie_name == self.movie_name:
                self.movie_rating_dict[movie_id].append(rating)
                #print("Successfully added new rating")
                found_movie=True
                return "Successfully added new rating"
        if (found_movie==False):
            return "Couldn't find the movie"
"""
m = Movie("Toy Story (1995)")
print(m.get_rating_by_name())
print(m.add_rating(1.2))
print(m.get_rating_by_name())
"""
