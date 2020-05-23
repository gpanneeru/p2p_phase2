import socket
import sys
import time
import threading
import random
import hashlib
import ast,os
from progress.bar import IncrementalBar

class FileNodeConnection(threading.Thread):

    def __init__(self,id1,id2):
        threading.Thread.__init__(self)
        print("Initializing file reading client...")
        self.id = "downloads"
        self.id1 = id1
        self.id2 = id2
        self.file_terminate = threading.Event()

    def writeToFile(self,lines1,filename2,filename3):
        file2 = open(filename2, 'r')
        lines2 = list(file2.readlines())
        file2.close()
        Set = set()
        for line in lines2:
            if not line == '\n':
                Set.add(line.replace("\n",""))

        intersection = []
        for line in lines1:
            line = line.replace("\n","")
            if line in Set:
                intersection.append(line)
        i=j=0
        file3 = open(filename3,'w+')
        magenta = lambda text: '\033[0;35m' + text + '\033[0m'
        for k,line in enumerate(intersection):
            # print(i,j,k)
            app_l1 = []
            app_l2 = []
            check1 = check2 = False
            while not lines1[i].replace("\n","") == line:
                app_l1.append(lines1[i])
                if not lines1[i]=="\n":
                    check1 = True
                #file3.write(lines1[i])
                i+=1
            while not lines2[j].replace("\n","") == line:
                app_l2.append(lines2[j])
                if not lines2[j]=="\n":
                    check2 = True
                #file3.write(lines2[j])
                j+=1
            #print("Parts: ",app_l1,app_l2)
            if check1 and check2:
                file3.write("<<<<<<<<<<<< "+self.id1+"\n")
                for app_line in app_l2:
                    file3.write(app_line)
                file3.write("============\n")
                for app_line in app_l1:
                    file3.write(app_line)
                file3.write(">>>>>>>>>>>> "+self.id2+"\n")
            else:
                if not check1 and not check2:
                    for app_line in app_l1:
                        file3.write(app_line)
                elif app_l1 and check1:
                    for app_line in app_l1:
                        file3.write(app_line)
                elif app_l2 and check2:
                    for app_line in app_l2:
                        file3.write(app_line)
            file3.write(line+"\n")
            i+=1
            j+=1
            # print(i,j,k)
        if i< len(lines1) and j<len(lines2):
            file3.write("<<<<<<<<<<<< "+self.id1+"\n")
            while j < len(lines2):
                file3.write(lines2[j])
                if not lines2[j].endswith("\n"):
                    file3.write("\n")
                j+=1
            file3.write("============\n")
            while i < len(lines1):
                file3.write(lines1[i])
                if not lines1[i].endswith("\n"):
                    file3.write("\n")
                i+=1
            file3.write(">>>>>>>>>>>> "+self.id2+"\n")
        else:
            while i < len(lines1):
                file3.write(lines1[i])
                i+=1
            while j < len(lines2):
                file3.write(lines2[j])
                j+=1
        file3.close()
        

    def run(self):
        # print("starting file thread")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 10001))
        sock.settimeout(10.0)
        sock.listen(5)
        # print("Entering while loop")
        block_size = 4096
        while not self.file_terminate.is_set():
            # print("In while loop")
            c, addr = sock.accept()     # Establish connection with client.
            # print('Got connection from', addr)
            # print("Receiving...")
            data = str(c.recv(5).decode("utf-8"))
            # print("data:",data)
            num_files = int(data)
            for i in range(num_files):
                data = str(c.recv(10).decode('utf-8'))
                # print("filebytes: "+data)
                fileb = int(data.split(" ")[0])#endianness may be affecting data transfer
                filenamebytes = int(data.split(" ")[1])

                data = str(c.recv(filenamebytes).decode('utf-8'))
                # print("filename received: "+data)
                filename = data
                curb = 0
                print('Receiving '+filename+"...")
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
                        if curb+block_size > fileb:
                            data = str(c.recv(fileb-curb).decode('utf-8'))
                        else:
                            data = str(c.recv(block_size).decode('utf-8'))
                        writeto.write(data)
                        next_val = int(100*(curb/fileb))
                        for i in range(next_val - percentage):
                            bar.next()
                        curb += len(data)
                        percentage = next_val
                        #print('\r' + str(curb) + "/" + str(fileb))
                        # print("")
                    # print("Last text:",data)
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
                        if curb+block_size > fileb:
                            data = str(c.recv(fileb-curb).decode('utf-8'))
                        else:
                            data = str(c.recv(block_size).decode('utf-8'))
                        # data = str(data.decode('utf-8'))
                        if data:
                            lines += data
                        next_val = int(100*(curb/fileb))
                        for i in range(next_val - percentage):
                            bar.next()
                        curb += len(data)
                        percentage = next_val
                        #print('\r' + str(curb) + "/" + str(fileb))
                        # print("")
                    lines = lines.split("\n")
                    next_val = int(100*(curb/fileb))
                    for i in range(next_val - percentage):
                        bar.next()
                    curb += len(data)
                    percentage = next_val
                    #print("lines: ",lines)
                    #print("end")
                    for i in range(len(lines)-1):
                        lines[i] = lines[i]+"\n"
                    self.writeToFile(lines,destination+"/"+file_name,destination+"/"+file_name)
                    bar.finish()
                    print('Transfer of '+filename+' successful.')
            self.file_terminate.set()
        print("File reading client closed")
        sock.close()
