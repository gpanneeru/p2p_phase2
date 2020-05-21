import socket
import sys
import time
import threading
import random
import hashlib
import ast,os
from progress.bar import IncrementalBar

class FileNodeConnection(threading.Thread):

    def __init__(self,id):
        threading.Thread.__init__(self)
        print("initilaizing filethreadclient")
        self.id = id
        self.file_terminate = threading.Event()

    def writeToFile(self,lines1,filename2,filename3):
        file2 = open(filename2, 'r')
        lines2 = list(file2.readlines())
        file2.close()
        Set = set()
        for line in lines2:
            #if not line == '\n':
            Set.add(line)

        intersection = []
        for line in lines1:
            if line in Set:
                intersection.append(line)
        i=j=0
        file3 = open(filename3,'w+')
        magenta = lambda text: '\033[0;35m' + text + '\033[0m'
        for line in intersection:
            app_l1 = []
            app_l2 = []
            check1 = check2 = False
            while not lines1[i] == line:
                app_l1.append(lines1[i])
                if not lines1[i]=="\n":
                    check1 = True
                #file3.write(lines1[i])
                i+=1
            while not lines2[j] == line:
                app_l2.append(lines2[j])
                if not lines2[i]=="\n":
                    check2 = True
                #file3.write(lines2[j])
                j+=1
            #print("Parts: ",app_l1,app_l2)
            if check1 and check2:
                file3.write("<<<<<<<<<<<< Source\n")
                for app_line in app_l1:
                    file3.write(app_line)
                file3.write("============\n")
                for app_line in app_l2:
                    file3.write(app_line)
                file3.write(">>>>>>>>>>>> Destination\n")
            else:
                for app_line in app_l1:
                    file3.write(app_line)
                for app_line in app_l2:
                    file3.write(app_line)
            file3.write(line)
            i+=1
            j+=1
        while i < len(lines1):
            file3.write(lines1[i])
            i+=1
        while j < len(lines2):
            file3.write(lines2[j])
            j+=1
        file3.close()
        

    def run(self):
        print("starting file thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 10001))
        sock.settimeout(10.0)
        sock.listen(5)
        print("Entering while loop")
        while not self.file_terminate.is_set():
            print("In while loop")
            c, addr = sock.accept()     # Establish connection with client.
            print('Got connection from', addr)
            print("Receiving...")
            data = str(c.recv(1024).decode("utf-8"))
            print("data:",data)
            num_files = int(data)
            for i in range(num_files):
                data = str(c.recv(10).decode('utf-8'))
                print("filebytes: "+data)
                fileb = int(data.split(" ")[0])#endianness may be affecting data transfer
                filenamebytes = int(data.split(" ")[1])
                data = str(c.recv(filenamebytes).decode('utf-8'))
                print("filename received: "+data)
                filename = data
                curb = 0
                print('Getting '+filename+"...")
                bar = IncrementalBar('Percentage of file transferred', max = 100)
                percentage = 0
                path = "/".join(filename.split("/")[:-1])
                destination = self.id + "/" + path
                file_name = filename.split("/")[-1]
                if not os.path.exists(destination+"/"+file_name):
                    if not os.path.exists(destination):
                        os.makedirs(destination)
                    writeto = open(destination+'/'+file_name,'w+')
                    while curb < fileb:
                        sys.stdout.flush()
                        if curb+1024 > fileb:
                            data = str(c.recv(fileb-curb).decode('utf-8'))
                        else:
                            data = str(c.recv(1024).decode('utf-8'))
                        writeto.write(data)
                        next_val = int(100*(curb/fileb))
                        for i in range(next_val - percentage):
                            bar.next()
                        curb += len(data)
                        percentage = next_val
                        #print('\r' + str(curb) + "/" + str(fileb))
                        print("")
                    next_val = int(100*(curb/fileb))
                    for i in range(next_val - percentage):
                        bar.next()
                    curb += len(data)
                    percentage = next_val
                    writeto.close()
                    bar.finish()
                    print('Transfer of '+filename+' successful.')
                else:
                    lines = ""
                    while curb < fileb:
                        sys.stdout.flush()
                        if curb+1024 > fileb:
                            data = str(c.recv(fileb-curb).decode('utf-8'))
                        else:
                            data = str(c.recv(1024).decode('utf-8'))
                        data = str(data.decode('utf-8'))
                        if data:
                            lines += data
                        next_val = int(100*(curb/fileb))
                        for i in range(next_val - percentage):
                            bar.next()
                        curb += len(data)
                        percentage = next_val
                        #print('\r' + str(curb) + "/" + str(fileb))
                        print("")
                    lines = lines.split("\n")[:-1]
                    next_val = int(100*(curb/fileb))
                    for i in range(next_val - percentage):
                        bar.next()
                    curb += len(data)
                    percentage = next_val
                    #print("lines: ",lines)
                    #print("end")
                    lines = [x+"\n" for x in lines]
                    self.writeToFile(lines,destination+"/"+file_name,destination+"/"+file_name)
                    bar.finish()
                    print('Transfer of '+filename+' successful.')
            self.file_terminate.set()
        print("Out of while loop")
        sock.close()
