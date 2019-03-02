import Pyro4
from Pyro4.errors import CommunicationError, PyroError
import random
from time import sleep

@Pyro4.expose
class FrontEnd(object):
	def __init__(self,daemon):
		self.daemon = daemon
		try:
			if (self.read_file() == ""):
				self.timestamp = [0,0,0]
			else:
				timestamp_in_file=self.read_file()
				print(timestamp_in_file)
				my_list = timestamp_in_file.split(",")
				del my_list[-1]
				self.timestamp= list(map(int, my_list))
		except FileNotFoundError:
			self.timestamp = [0,0,0]
		self.connect()

	def connect(self):
		self.server_list=[]
		self.connected_server_list= []
		ns = Pyro4.locateNS()
		self.server_1=ns.lookup("movie_server1")
		self.server_2=ns.lookup("movie_server2")
		self.server_3=ns.lookup("movie_server3")
		self.server_list.append(self.server_1)
		self.server_list.append(self.server_2)
		self.server_list.append(self.server_3)
		
		for server in self.server_list:
			self.connected_server_list.append(Pyro4.Proxy(server))
			Pyro4.Proxy(server).empty_servers()
		for con in self.connected_server_list:
			con.set_servers(self.server_list)
		return  True

	def find_available_server(self):
		for i in range (0, len(self.server_list)):
			#try:
			connect_server = Pyro4.Proxy(self.server_list[i])
			status= connect_server.set_status()
			print("Status: " , status)
			print("Using server ", i+1)
			while (status == "Overloaded" or status == "Offline" ):
				i=i+1
				print(i)
				if (i == 3):
					print("No servers")
					i=0
					self.find_available_server()
				print("changing server to server: ", i+1)
				connect_server = Pyro4.Proxy(self.server_list[i])
				status= connect_server.set_status()

			return connect_server

	
	@Pyro4.oneway
	def shutdown(self):
		print("Shutting down")
		self.daemon.shutdown()
		
	def get_data_from_client(self, data):
		request = data['request']
		user_inp = data['user_inp']
		userid = data['user_id']
		movie=data['movie_name']

		#These are the request the user can perform
		
		if request == "ADD_RATING":
			print("Currently ADDING a new rating")
			results, time = self.find_available_server().add_rating(userid, user_inp,self.timestamp,movie)
			print("Server response: ", results)
			self.timestamp=time
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)

		elif request == "GET_RATING":
			print("Currently GETING rating")
			results, time2 = self.find_available_server().get_rating_by_name(userid,self.timestamp,movie)
			print("Server response: ", results)
			self.timestamp=time2
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)
		
		elif request == "VIEW_RATING":
			print("Currently VIEWING rating")
			results, time4 = self.find_available_server().view_rating(userid,self.timestamp,movie)
			print("Server response: ", results)
			self.timestamp=time4
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)
		
	
		elif request == "GET_AVG":
			print("Currently GETING AVERAGE rating")
			results, time3 = self.find_available_server().get_average_rating(userid,self.timestamp,movie)
			print("Server response: ", results)
			self.timestamp=time3
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)

		elif request == "SET_MOVIE":
			print("Currently SETTING a movie")
			results, time1 = self.find_available_server().set_movie(userid, user_inp,self.timestamp)
			print("Server response: ", results)
			self.timestamp=time1
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)
		
		elif request == "UPDATE_RATING":
			print("Currently UPDATING a rating")
			results, time5 = self.find_available_server().update_rating(userid, user_inp,self.timestamp,movie)
			print("Server response: ", results)
			self.timestamp=time5
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)
		
		elif request == "EXIT":
			for i in self.server_list:
				ser=Pyro4.Proxy(i)
				ser.shutdown()
		else:
			return "No such command"
		
	def write(self):
		text_file = open("timestamp.txt", "w")
		for i in self.timestamp:
			text_file.write(str(i)+",")
		text_file.close()
		
	def read_file(self):
		file_read = open("timestamp.txt", "r")
		return file_read.read()

def main():
	counter =0
	while counter !=5:
		try:
			daemon = Pyro4.Daemon()
			ns = Pyro4.locateNS()
			f=FrontEnd(daemon)
			url = daemon.register(f)
			ns.register("frontend", url)
			print("Listening: ",url)
			daemon.requestLoop()
			print("Exit loop")
			daemon.close()
			f.timestamp=0
			f.write()
			print("Daemon closed")
			break
		except Pyro4.errors.CommunicationError:
			print("Attempt ", counter , " out of 5")
			print("Servers are not found. Sleeping for 10 seconds and trying again1...")
			sleep(10)
			print("Trying to reconnect")
			counter = counter + 1

if __name__ == "__main__":
	main()
