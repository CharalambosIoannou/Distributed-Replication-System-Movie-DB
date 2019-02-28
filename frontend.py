import Pyro4
from Pyro4.errors import CommunicationError, PyroError
import random
from time import sleep

@Pyro4.expose
class FrontEnd(object):
	def __init__(self,daemon):
		self.daemon = daemon
		
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
			# except ConnectionRefusedError:
			# 	print("Servers are not found. Sleeping for 20 seconds and trying again...")
			# 	sleep(20)
			# 	print("Trying to reconnect")
			# 	self.find_available_server()
			# except CommunicationError:
			# 	print("Servers are not found. Sleeping for 20 seconds and trying again...")
			# 	sleep(20)
			# 	print("Trying to reconnect")
			# 	self.find_available_server()
			# except PyroError:
			# 	print("Servers are not found. Sleeping for 20 seconds and trying again...")
			# 	sleep(20)
			# 	print("Trying to reconnect")
			# 	self.find_available_server()
			# except Pyro4.errors.CommunicationError:
			# 	print("Servers are not found. Sleeping for 20 seconds and trying again...")
			# 	sleep(20)
			# 	print("Trying to reconnect")
			# 	self.find_available_server()
			# 	#return
		

	
	@Pyro4.oneway
	def shutdown(self):
		print("Shutting down")
		self.daemon.shutdown()
		
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
			results, time = self.find_available_server().add_rating(userid, user_inp,self.timestamp)
			print("Frontend results: ", results)
			self.timestamp=time
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)

		elif request == "GET_RATING":
			print("Running GET RATING Function Frontend")
			results, time2 = self.find_available_server().get_rating_by_name(userid,self.timestamp)
			print("Frontend results: ", results)
			self.timestamp=time2
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)
		
		elif request == "VIEW_RATING":
			print("Running VIEW RATING Function Frontend")
			results, time4 = self.find_available_server().view_rating(userid,self.timestamp)
			print("Frontend results: ", results)
			self.timestamp=time4
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)
		
	
		elif request == "GET_AVG":
			print("Running GET AVG Function Frontend")
			results, time3 = self.find_available_server().get_average_rating(userid,self.timestamp)
			print("Frontend results: ", results)
			self.timestamp=time3
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)

		elif request == "SET_MOVIE":
			print("Setting movie frontend")
			results, time1 = self.find_available_server().set_movie(userid, user_inp,self.timestamp)
			
			print("Frontend results: ", results)
			self.timestamp=time1
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)
		
		elif request == "UPDATE_RATING":
			print("Running UPDATE RATING Function Frontend")
			results, time5 = self.find_available_server().update_rating(userid, user_inp,self.timestamp)
			print("Frontend results: ", results)
			self.timestamp=time5
			print("TimeStamp received from server: ", self.timestamp)
			self.write()
			return str(results)
		
		elif request == "EXIT":
			for i in self.server_list:
				ser=Pyro4.Proxy(i)
				ser.shutdown()

		else:
			return "Command not found. Please try again"
		
		
		
		

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
			print("Servers are not found. Sleeping for 10 seconds and trying again...")
			sleep(10)
			print("Trying to reconnect")
			counter = counter + 1

if __name__ == "__main__":
	main()
