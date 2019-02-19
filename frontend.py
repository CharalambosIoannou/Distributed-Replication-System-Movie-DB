import Pyro4
from Pyro4.errors import CommunicationError, PyroError


@Pyro4.expose
class FrontEnd(object):
	def __init__(self):
		self.counter_server_1 = 0
		self.counter_server_2 = 0
		self.counter_server_3 = 0
		self.timestamp = [0,0,0]
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


	def find_available_server(self,query):
		for i in range (0, len(self.server_list)):
			try:
				connect_server = Pyro4.Proxy(self.server_list[i])
				status= connect_server.set_status()
				print("Status: " , status)
				print("Using server ", i+1)
				if (status == "Overloaded" or status == "Offline"):
					if (i == len(self.server_list) -1):
						print("Run out of servers")
						return
					else:
						print("changing server to server: ", i+2)
						connect_server = Pyro4.Proxy(self.server_list[i+1])
						i=i+1
				"""
				if (query == True):
						if (i == 0):
							self.counter_server_1 = self.counter_server_1 + 1
							self.timestamp[0] = self.counter_server_1
						elif (i == 1):
							self.counter_server_2 = self.counter_server_2 + 1
							self.timestamp[1] = self.counter_server_2
						else:
							self.counter_server_3 = self.counter_server_3 + 1
							self.timestamp[2] = self.counter_server_3
					
				print("Timestamp: " , self.timestamp)
				"""
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
		query=False

		print("com ", request)
		print("inp ", user_inp)
		print("user ", userid)

		if not userid:
			return "No USERID specified"
		
		if request == "ADD_RATING":
			print("Running ADD RATING Function Frontend")
			query= True
			#self.counter=self.counter + 1
			results, time = self.find_available_server(query).add_rating(userid, user_inp,self.timestamp)
			print("Frontend results: ", results)
			self.timestamp=time
			print("TimeStamp received from server: ", self.timestamp)
			return str(results)

		elif request == "GET_RATING":
			print("Running GET RATING Function Frontend")
			results = self.find_available_server(query).get_rating_by_name(userid)
			print("Frontend results: ", results)
			return str(results)
	
		elif request == "GET_AVG":
			print("Running GET AVG Function Frontend")
			results = self.find_available_server(query).get_average_rating(userid)
			print("Frontend results: ", results)
			return str(results)

		elif request == "SET_MOVIE":
			print("Setting movie frontend")
			results = self.find_available_server(query).set_movie(userid, user_inp)
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
