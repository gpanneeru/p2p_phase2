from node import Node
import time
import os
import re
from os import walk
import json

class CommandController():

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
            print("Connection not successful, node not available")


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

    def add_repo(self,repo_path):
        repo_path = repo_path[:-1] if repo_path[-1]=="/" else repo_path
        keywords = set()

        with open(".exclude_patterns") as file:
            excluded_pattern_list = file.readlines()
        file.close()
        excluded_pattern_list = [x.strip() for x in excluded_pattern_list]

        for (_dirpath, dirnames, filenames) in walk(repo_path):
            for filename in filenames:
                is_match = True
                for pattern in excluded_pattern_list:
                    if re.search(pattern, filename) != None:
                        is_match = False
                        break
                if (is_match):
                    keywords.add(filename)

            for dirname in dirnames:
                is_match = True
                for pattern in excluded_pattern_list:
                    if re.search(pattern, dirname) != None:
                        is_match = False
                        break
                if (is_match):
                    keywords.add(dirname)
                else:
                    dirnames.remove(dirname)

        if not os.path.exists(".nodes/"+ self.node.id):
            os.mkdir(".nodes/"+self.node.id)
        keyword_dict = {}
        for keyword in keywords:
            if keyword in keyword_dict:
                keyword_dict[keyword].append(repo_path)
            else:
                keyword_dict[keyword] = [repo_path]
        repo_name = repo_path.split('/')[-1]
        keyword_dict[repo_name] = [repo_path]
        keyword_file = ".nodes/"+self.node.id+"/shared_repo_list"
        repo_file = ".nodes/"+self.node.id+"/repo_map.json"

        f = open(keyword_file,'a+')
        for entry in keyword_dict.items():
            f.write(str(entry) + "\n")
        f.close()

        with open(repo_file, 'a+') as repo_map_file:
            line = repo_map_file.readline()

        if not line:
            line = dict()
        else:
            line = json.loads(line)

        if repo_name in line.keys():
            line[repo_name].append(repo_path)
        else:
            line[repo_name] = [repo_path]

        with open(repo_file, "w") as repo_map_file:
            repo_map_file.write(json.dumps(line))

    def search(self,keyword):
        self.node.send_to_nodes("search "+keyword)

    def request(self,repo_name,node_id):
        for connection in self.node.nodes_inbound+self.node.nodes_outbound:
            if connection.id==node_id:
                connection.send("request "+repo_name)

    def stop(self):
        if self.node:
            self.node.stop()
    
    def ping(self):
        if self.node:
            self.node.ping(self.node.host, self.node.port)

    def query(self, query_param):
        if self.node:
            self.node.query(query_param)

def main():
    print("Welcome to P2P Code Sharing APP")
    string = ""
    controller = CommandController()
    while not string=="exit" :
        string = input("> ")
        if string=="init":
            controller.init()
        elif string=="connect":
            controller.connect_with_cached_nodes()
        elif string=="stop":
            controller.stop()
        elif string=="help":
            print("Available Commands: \n \
            1. init: initializes a node with given port \n \
            2. connect: Tries to connect with the cached nodes \n \
            3. show connections: Shows all the connected nodes to the current node \n \
            4. share <folder_path>: Adds the current folder to sharing list \n \
            5. search <keyword>: Searches and gets result of any repositories related to the keyword \n \
            6. request <repository> <node_id>: Requests repo from a specific node which in turn sends all the files in the repository \n \
            7. stop: Stops the current node \n \
            8. exit: Stops the application")
        elif string=="exit":
            print("Stopping the application")
            controller.stop()
        elif string=="":
            pass
        elif string.startswith("share"):
            repo_path = string.split(" ")[1]
            controller.add_repo(repo_path)
        elif string.startswith("search"):
            keyword = string.split(" ")[1]
            controller.search(keyword)
        elif string.startswith("request"):
            repo_name,node_id = string.split(" ")[1:]
            controller.request(repo_name,node_id)
        elif string=="show connections":
            controller.show_connections()
        elif string=="ping":
            controller.ping()
        elif string.startswith("query"):
            query_param = string.split(" ")[1]
            controller.query(query_param)
        else:
            print("Invalid command, use help to see the commands which can be used")

if __name__ == "__main__":
    main()
