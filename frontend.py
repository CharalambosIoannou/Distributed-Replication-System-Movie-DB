import json
import Pyro4
from Pyro4.errors import CommunicationError, PyroError


@Pyro4.expose
class FrontEnd(object):
    def __init__(self):
        ns = Pyro4.locateNS()
        self.server_uris = [ns.lookup("movie_server1"), ns.lookup("movie_server2"), ns.lookup("movie_server3")]
        server_list = []
        server_status=[]
        for uri in self.server_uris:
            server_list.append([Pyro4.Proxy(uri),Pyro4.Proxy(uri).status()])
        #print(server_list)
        # update server lists
        for s in server_list:
            try:
                s[0].set_servers(self.server_uris)
            except PyroError:
                pass  # ignore the error

        #print(self.server_uris)

    def get_server(self):
        primary_server = True
        for server in self.server_list:
            try:
                actual_server = Pyro4.Proxy(server[0])
                actual_server.set_primary_state(primary_server)
                primary_server = False
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
        command = data['action']
        userid = data['userid']
        input = data['data']
        if not userid:
            return "No USERID specified"
        if command == "ADD":
            print("Running Action Frontend")
            items_to_order = input.split(',')
            if len(items_to_order) > 3 or len(items_to_order) == 0:
                return "Must enter at least 1 item, and no more than 3."
            # deal with batch stuff, to
            results = self.__get_order_server().place_order(userid, items_to_order)

            # todo check length to make sure a server is online.
            return str(results)

        elif command == "GET_RATING":
            print("running delete front end")
            del_index = input
            results = self.__get_order_server().cancel_order(userid, del_index)

            # todo check results to ensure things are fine :D
            return str(results)

        elif command == "GET_AVG":
            print("Running History frontend")
            results = self.__get_order_server().get_order_history(userid)
            print("Frontend results: ", results)
            # todo remove batch processing for this (no CUD needed, only R).
            return str(results)

        else:
            return "Command not found. Please try again"



def main():
    fr=FrontEnd()



if __name__ == "__main__":
    main()
