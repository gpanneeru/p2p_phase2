from node import Node
import time
import os
import re
from os import walk

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

    def add_repo(self,repo_path):
        keywords = set()

        with open(".exclude_patterns") as file:
            excluded_pattern_list = file.readlines()
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

        if not os.path.exists(self.node.id):
            os.mkdir(self.node.id)
        dict = {}
        for keyword in keywords:
            if keyword in dict:
                dict[keyword].append(repo_path)
            else:
                dict[keyword] = [repo_path]
        dict[repo_path.split('/')[-1]] = repo_path
        f = open(self.node.id+"/shared_repo_list",'a+')
        f.write( str(dict) )
        f.close()

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
            repo_path = string.split(" ")[1]
            demo.add_repo(repo_path)
        elif string=="show connections":
            demo.show_connections()
        else:
            print("Invalid command, use help to see the commands which can be used")

if __name__ == "__main__":
    main()
