import json
import Pyro4
from Pyro4.errors import CommunicationError, PyroError


@Pyro4.expose
class FrontEnd(object):
	def __init__(self):
		ns = Pyro4.locateNS()
		self.server_uris = [ns.lookup("movie_server1"), ns.lookup("movie_server2"), ns.lookup("movie_server3")]
		self.server_list = []
		server_status=[]
		for uri in self.server_uris:
			self.server_list.append(Pyro4.Proxy(uri))
		#print(server_list)
		# update server lists
		for s in self.server_list:
			try:
				s.set_servers(self.server_uris)
			except PyroError:
				pass  # ignore the error

	#print(self.server_uris)

	def get_server(self):
		primary_server = True
		for i in range (0, len(self.server_uris)):
			try:
				actual_server = Pyro4.Proxy(self.server_uris[i])
				status= actual_server.get_status()
				print("Status: " , status)
				if (status == "Overloaded" or status == "Offline"):
					
					if (i == len(self.server_uris) -1):
						print("Run out of servers")
						return
					else:
						print("changing server: ", i )
						actual_server = Pyro4.Proxy(self.server_uris[i+1])
				return actual_server
			except ConnectionRefusedError:
				pass
			except CommunicationError:
				pass
			except PyroError:
				pass
		return None  # todo throw No Remaining Servers exception

	def process_command(self, data):
		print("Frontend data: ", data)
		command = data['request']
		input = data['data']
		userid = data['userid']

		print("com ", command)
		print("inp ", input)
		print("user ", userid)

		if not userid:
			return "No USERID specified"
		
		if command == "ADD_RATING":
			print("Running ADD RATING Function Frontend")
			results = self.get_server().add_rating(userid,input)
			# todo check length to make sure a server is online.
			print("Frontend results: ", results)
			return str(results)

		elif command == "GET_RATING":
			print("Running GET RATING Function Frontend")
			results = self.get_server().get_rating_by_name(userid)
			print("Frontend results: ", results)
			return str(results)
	
		elif command == "GET_AVG":
			print("Running GET AVG Function Frontend")
			results = self.get_server().get_average_rating(userid)
			print("Frontend results: ", results)
			return str(results)

		elif command == "SET_MOVIE":
			print("Setting movie frontend")
			results = self.get_server().set_movie(userid,input)
			print("Frontend results: ", results)
			# todo remove batch processing for this (no CUD needed, only R).
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
