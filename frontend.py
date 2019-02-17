import json
import Pyro4
from Pyro4.errors import CommunicationError, PyroError


@Pyro4.expose
class FrontEnd(object):
	def __init__(self):
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
			
		for con in self.connected_server_list:
			con.set_servers(self.server_list)


	def find_available_server(self):
		for i in range (0, len(self.server_list)):
			try:
				connect_server = Pyro4.Proxy(self.server_list[i])
				status= connect_server.get_status()
				print("Status: " , status)
				print("Using server ", i+1)
				if (status == "Overloaded" or status == "Offline"):
					if (i == len(self.server_list) -1):
						print("Run out of servers")
						return
					else:
						print("changing server to server: ", i+2)
						connect_server = Pyro4.Proxy(self.server_list[i+1])
				return connect_server
			except ConnectionRefusedError:
				pass
			except CommunicationError:
				pass
			except PyroError:
				pass
		return None  # todo throw No Remaining Servers exception

	def get_data_from_client(self, data):
		request = data['request']
		user_inp = data['user_inp']
		userid = data['user_id']

		print("com ", request)
		print("inp ", user_inp)
		print("user ", userid)

		if not userid:
			return "No USERID specified"
		
		if request == "ADD_RATING":
			print("Running ADD RATING Function Frontend")
			results = self.find_available_server().add_rating(userid, user_inp)
			print("Frontend results: ", results)
			return str(results)

		elif request == "GET_RATING":
			print("Running GET RATING Function Frontend")
			results = self.find_available_server().get_rating_by_name(userid)
			print("Frontend results: ", results)
			return str(results)
	
		elif request == "GET_AVG":
			print("Running GET AVG Function Frontend")
			results = self.find_available_server().get_average_rating(userid)
			print("Frontend results: ", results)
			return str(results)

		elif request == "SET_MOVIE":
			print("Setting movie frontend")
			results = self.find_available_server().set_movie(userid, user_inp)
			print("Frontend results: ", results)
			return str(results)

		else:
			return "Command not found. Please try again"



def main():
	daemon = Pyro4.Daemon()
	ns = Pyro4.locateNS()
	url = daemon.register(FrontEnd())
	ns.register("frontend", url)
	print("Listening: ")
	daemon.requestLoop()


if __name__ == "__main__":
	main()
