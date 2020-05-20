from node import Node
import time
import os

class Demo():

    def __init__(self):
        self.node = None

    def node_callback(self,event, node, connected_node, data):
        pass

    def connect_with_cached_nodes(self):
        if not self.node:
            print("Use init function to first create and initialize a node before connecting to other nodes")
            return
        try:
            f = open("cache","r")
            for line in f.readlines():
                host,port = line.split(" ")[0],int(line.split(" ")[1])
                if not port==self.node.port:
                    print("Trying to connect with",host+":"+str(port))
                    self.node.connect_with_node(host,port)
        except Exception as e:
            print("Exception:",str(e))


    def init(self):
        try:
            port = int(input(">Please input the port you want to use: "))
            self.node = Node("127.0.0.1", port, self.node_callback)
            self.node.start()
            time.sleep(1)
            self.connect_with_cached_nodes()
            self.node.print_connections()
            time.sleep(1)
        except Exception as e:
            print("Exception:",str(e))

    def show_connections(self):
        self.node.print_connections()

    def add_repo(self,repo_name):
        keywords = input("Please enter the keywords related to the repo(comma separated):")
        keywords = keywords.split(",")
        if not os.path.exists(self.node.id):
            os.mkdir(self.node.id)
        if os.path.exists(self.node.id+"/shared_repo_list"):
            s = open(self.node.id+"/shared_repo_list", 'r').read()
            dict = ast.literal_eval(s)
        else:
            dict = {}
        for keyword in keywords:
            if keyword in dict and repo_name not in dict[keyword]:
                dict[keyword].append(repo_name)
            else:
                dict[keyword] = [repo_name]
        f = open(self.node.id+"/shared_repo_list",'w+')
        f.write( str(dict) )
        f.close()

    def search(self,keyword):
        self.node.send_to_nodes("search "+keyword)

    def request(self,repo_name,node_id):
        for connection in self.node.nodes_inbound+self.node.nodes_outbound:
            if connection.id==node_id:
                connection.send("request "+repo_name)

    def stop(self):
        if self.node:
            self.node.stop()
    
def main():
    print("Welcome to P2P Code Sharing APP")
    string = ""
    demo = Demo()
    while not string=="quit" :
        string = input("> ")
        if string=="init":
            demo.init()
        elif string=="connect":
            demo.connect_with_cached_nodes()
        elif string=="stop":
            demo.stop()
        elif string=="help":
            print("Available Commands: init,connect,show connections,stop,quit")
        elif string=="quit":
            print("Quitting the application")
            demo.stop()
        elif string=="":
            pass
        elif string.startswith("share"):
            repo_name = string.split(" ")[1]
            base_path = os.getcwd()
            demo.add_repo(base_path+"/"+repo_name)
        elif string.startswith("search"):
            keyword = string.split(" ")[1]
            demo.search(keyword)
        elif string.startswith("request"):
            repo_name,node_id = string.split(" ")[1:]
            demo.request(repo_name,node_id)
        elif string=="show connections":
            demo.show_connections()
        else:
            print("Invalid command, use help to see the commands which can be used")

if __name__ == "__main__":
    main()
