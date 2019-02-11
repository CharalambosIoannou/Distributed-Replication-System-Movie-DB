import csv

movie_name_dict = {}
movie_rating_dict = {}

with open('movies.csv', encoding="utf8") as csv_file:
    counter=0
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:
        if (counter == 0):
            counter+=1
        else:
            movie_name_dict[row[0]]=row[1]

with open('ratings.csv', encoding="utf8") as csv_file:
    counter=0
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:        
        if (counter == 0):
            counter+=1
        else:
            movie_id=row[1]
            if (movie_id not in movie_rating_dict):
                movie_rating_dict[movie_id] = [float(row[2])]
            else:
                 movie_rating_dict[movie_id].append(float(row[2]))
                 

def get_movie_name_by_id(movie_id):
    return movie_name_dict.get(str(movie_id))

def get_movie_name_by_name(movie_name):
    id_found=""
    movie=""
    for movie_id in movie_name_dict:
       if (get_movie_name_by_id(str(movie_id)) == movie_name):
           id_found=movie_id
    if (id_found !=""):
        movie= get_movie_name_by_id(str(id_found))
        return id_found,movie
    else:
        return None

def get_rating_by_id(movie_id):
    return movie_rating_dict.get(str(movie_id))

def get_rating_by_name(movie_name):
    id_found=""
    movie=""
    for movie_id in movie_rating_dict:
       if (get_movie_name_by_id(str(movie_id)) == movie_name):
           id_found=movie_id
    if (id_found !=""):
        rating= (get_rating_by_id(str(id_found)))
        return rating
    else:
        return None

def get_average_rating(rating):   
    return sum(rating) / len(rating)

def add_rating(input_movie_name, rating):
    found_movie=False
    for movie_id,movie_name in movie_name_dict.items():
        if movie_name == input_movie_name:
            print(movie_id)
            movie_rating_dict[movie_id].append(rating)
            #print("Successfully added new rating")
            found_movie=True
            return "Successfully added new rating"
    if (found_movie==False):
        return "Couldn't find the movie"
    
        
  
#print(get_movie_name_by_id(5))
#print(get_movie_name_by_id("5"))
#print((get_rating_by_id("5")))
#print(add_rating("Father of the Bride Part II (1995)", 4.3))
#print((get_rating_by_id("5")))
