import socket
import sys
import time
import threading
import random
import hashlib
import ast,os,math
from filenodeconnection import FileNodeConnection
import json

class NodeConnection(threading.Thread):
    """The class NodeConnection is used by the class Node and represent the TCP/IP socket connection with another node. 
       Both inbound (nodes that connect with the server) and outbound (nodes that are connected to) are represented by
       this class. The class contains the client socket and hold the id information of the connecting node. Communication
       is done by this class. When a connecting node sends a message, the message is relayed to the main node (that created
       this NodeConnection in the first place).
       
       Instantiates a new NodeConnection. Do not forget to start the thread. All TCP/IP communication is handled by this 
       connection.
        main_node: The Node class that received a connection.
        sock: The socket that is assiociated with the client connection.
        id: The id of the connected node (at the other side of the TCP/IP connection).
        host: The host/ip of the main node.
        port: The port of the server of the main node."""

    def __init__(self, main_node, sock, id, host, port):
        """Instantiates a new NodeConnection. Do not forget to start the thread. All TCP/IP communication is handled by this connection.
            main_node: The Node class that received a connection.
            sock: The socket that is assiociated with the client connection.
            id: The id of the connected node (at the other side of the TCP/IP connection).
            host: The host/ip of the main node.
            port: The port of the server of the main node."""

        super(NodeConnection, self).__init__()

        self.host = host
        self.port = port
        self.main_node = main_node
        self.sock = sock
        self.terminate_flag = threading.Event()
        self.file_terminate = False
        # Variable for parsing the incoming json messages
        self.buffer = ""

        # The id of the connected node
        self.id = id
        self.dict = {}

        self.main_node.debug_print("NodeConnection.send: Started with client (" + self.id + ") '" + self.host + ":" + str(self.port) + "'")

    def send(self, data):
        """Send the data to the connected node. The data should be of the type string. A terminating string (-TSN) is
           used to make sure, the node is able to process the messages that are send."""
           
        try:
            data = data + "-TSN"
            self.sock.sendall(data.encode('utf-8'))

        except Exception as e:
            self.main_node.debug_print("NodeConnection.send: Unexpected error:", sys.exc_info()[0])
            self.main_node.debug_print("Exception: " + str(e))
            self.terminate_flag.set()

    # This method should be implemented by yourself! We do not know when the message is
    # correct.
    # def check_message(self, data):
    #         return True

    # Stop the node client. Please make sure you join the thread.
    def stop(self):
        """Terminates the connection and the thread is stopped."""
        self.terminate_flag.set()


    def get_ready_to_receive_files(self):
        # print("In get ready")
        fileclient = FileNodeConnection(self.main_node.id)
        fileclient.start()

    def senddata(self,file_name,path,sock,repo):
        try:
            filehandle = open(path+file_name,'r')
        except IOError:
            sock.send('ABORT SEND'.encode('utf-8'))
            print('File ' +str(path+file_name)+ ' not found; not sending...')
        else:
            #writes 8 byte header consisting of:
            #length of file in kb (4b)
            #length of filename (4b)

            numbytes = len(open(path+file_name,'r').read())
            #amount of KB (1024) to receive, written to 4-byte integer
            filename = repo + file_name if repo else file_name
            filenamebytes = len(filename)
            print("Number of bytes in filename:",filenamebytes)
            print("Number of bytes in file data:",numbytes)
            print('Sending '+str(path+file_name)+'...')
            sending = str(numbytes).zfill(6)+" "+str(filenamebytes).zfill(3)
            sock.send(sending.encode('utf-8'))
            data = filename
    #        print("filename: "+data)
            sock.send(data.encode('utf-8'))
            while True:
                data = filehandle.read(4096)
                if not data:
                    break
                sock.send(data.encode('utf-8'))
            filehandle.close()
            print('Send complete for '+filename)

    def getListOfFiles(self,dirName):
        # create a list of file and sub directories 
        # names in the given directory 
        listOfFile = os.listdir(dirName)
        allFiles = list()
        # Iterate over all the entries
        for entry in listOfFile:
            # Create full path
            fullPath = os.path.join(dirName, entry)
            # If entry is a directory then get the list of files in this directory 
            if os.path.isdir(fullPath):
                allFiles = allFiles + self.getListOfFiles(fullPath)
            else:
            	if not "/." in fullPath and self.id not in fullPath and "__" not in fullPath:
                	allFiles.append(fullPath)
        return allFiles

    def sendrepo(self,repo):
        # print("In send repo function")
        repo_name = repo.split("/")[-1]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 10001))
        if os.path.isfile(repo):
            sock.send("00001".encode('utf-8'))
            name = repo.split("/")[-1]
            self.senddata(name, repo.replace(name,""),sock,"")
        else:
            # print("Repo Available, not file")
            #total_files = sum([len(files) for r, d, files in os.walk(repo)])
            files = self.getListOfFiles(repo)
            sock.send(str(len(files)).zfill(5).encode('utf-8'))
            print("Total files:",len(files))
            for file in files:
                path = file.split(repo_name)[0]+repo_name
                file_name = repo_name.join(file.split(repo_name)[1:])
                self.senddata(file_name,path,sock,repo_name)

    def load_repos(self):
        if os.path.exists(".nodes/"+ self.main_node.id):
            repos = set()
            f = open(".nodes/"+self.main_node.id+"/shared_repo_list",'r')
            for line in f.readlines():
                line = line.strip("() \n")
                key = line.split(",")[0].strip("''")
                values_string = line.split(",")[1].strip().replace("['","").replace("']","")
                #print(key,keyword,values_string)
                #if key==keyword:
                #    repos.add(values_string)
                self.dict[values_string.split("/")[-1]] = values_string
            f.close()
            return ",".join(repos)

    def get_repos(self,keyword):
        if os.path.exists(".nodes/"+ self.main_node.id):
            repos = set()
            f = open(".nodes/"+self.main_node.id+"/shared_repo_list",'r')
            for line in f.readlines():
                line = line.strip("() \n")
                key = line.split(",")[0].strip("''")
                values_string = line.split(",")[1].strip().replace("['","").replace("']","")
                # print(key,keyword,values_string)
                if key==keyword:
                    repos.add(values_string)
                    #self.dict[values_string.split("/")[-1]] = values_string
            f.close()
            return ",".join(repos)
        # folder = self.main_node.id+"/shared_repo_list"
        # if os.path.exists(folder):
        #     s = open(folder, 'r').read()
        #     dict = ast.literal_eval(s)
        #     if keyword in dict:
        #         print("Repos available:",dict[keyword])
        #         for name in dict[keyword]:
        #             self.dict[name.split("/")[-1]] = name
        #         return ",".join(dict[keyword])
        return ""

    # Required to implement the Thread. This is the main loop of the node client.
    def run(self):
        """The main loop of the thread to handle the connection with the node. Within the
           main loop the thread waits to receive data from the node. If data is received 
           the method node_message will be invoked of the main node to be processed."""
        self.sock.settimeout(10.0)          
 
        while not self.terminate_flag.is_set():
            line = ""

            try:
                line = self.sock.recv(4096) 

            except socket.timeout:
                self.main_node.debug_print("NodeConnection: timeout")

            except Exception as e:
                self.terminate_flag.set()
                self.main_node.debug_print("NodeConnection: Socket has been terminated (%s)" % line)
                self.main_node.debug_print(e)

            if line != "":
                try:
                    # BUG: possible buffer overflow when no -TSN is found!
                    self.buffer += str(line.decode('utf-8')) 

                except Exception as e:
                    print("NodeConnection: Decoding line error | " + str(e))

                # Get the messages by finding the message ending -TSN
                index = self.buffer.find("-TSN")
                while index > 0:
                    message = self.buffer[0:index]
                    # print("message received:",message)
                    if message.startswith("request"):
                        self.load_repos()
                        repo_name = message.split(" ")[1]
                        repo_file = ".nodes/"+self.main_node.id+"/repo_map.json"
                        cur_dir = os.getcwd()
                        filepath = cur_dir+"/"+repo_name
                        with open(repo_file, 'r') as repo_map_file:
                            line = repo_map_file.readline()
                            line = json.loads(line)
                            filepath = line[repo_name][0]
                            # print(filepath)
                        if os.path.exists(filepath):
                            #print("Sending "+repo_name+" to "+self.id)
                            print("Ready to send")
                            self.send("Sending "+repo_name)
                        else:
                            self.send("Cannot Send "+repo_name+", file/folder doesn't exist")
                    if message.startswith("Sending"):
                        repo_name = message.split(" ")[1]
                        self.get_ready_to_receive_files()
                        print("Ready to receive")
                        self.send("ready to receive "+repo_name)
                    if message.startswith("ready to receive"):
                        repo_name = message.split(" ")[-1]
                        self.sendrepo(self.dict[repo_name])
                    if message.startswith("Cannot"):
                        print(message)
                    if message.startswith("search_result"):
                        results = message.split(" ")[-1]
                        if results:
                            print("Results from Node:",self.id)
                            for i,result in enumerate(results.split(",")):
                                result = result[:-1] if result[-1]=="/" else result
                                print(str(i+1)+". "+result.split("/")[-1])
                    if message=="PINGER":
                        self.send("PONGER")
                    if message=="PONGER":
                        self.main_node.heart_beat = True
                    if message.startswith("search "):
                        keyword = message.split(" ")[1]
                        repos = self.get_repos(keyword)
                        self.send("search_result "+repos)
                    elif message[:4] == "pkt:":
                        message = message[4::]
                        json_packet = json.loads(message)
                        if json_packet["command"] == "ping":
                            self.main_node.pong(json_packet)
                        elif json_packet["command"] == "query":
                            self.main_node.query_hit(json_packet)
                        self.main_node.forward_packet(json_packet)
                    self.buffer = self.buffer[index + 4::]

                    self.main_node.message_count_recv += 1
                    self.main_node.node_message(self, message)

                    index = self.buffer.find("-TSN")

            time.sleep(0.01)

        # IDEA: Invoke (event) a method in main_node so the user is able to send a bye message to the node before it is closed?

        self.sock.settimeout(None)
        self.sock.close()
        self.main_node.debug_print("NodeConnection: Stopped")

    def __str__(self):
        return 'NodeConnection: {}:{} <-> {}:{} ({})'.format(self.main_node.host, self.main_node.port, self.host, self.port, self.id)

    def __repr__(self):
        return '<NodeConnection: Node {}:{} <-> Connection {}:{}>'.format(self.main_node.host, self.main_node.port, self.host, self.port)
