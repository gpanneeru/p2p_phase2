# Peer2Peer Decentralized Code Sharing application

This is a peer2peer decentralized code sharing application which provides following functionalities:

1. init: Initializes a node with given port
2. connect: Tries to connect with the cached nodes
3. show connections: Shows all the connected nodes to the current node
4. share &lt folder_path>: Adds the current folder to sharing list
5. search <keyword>: Searches and gets result of any repositories related to the keyword
6. request <repository> <node_id>: Requests repo from a specific node which in turn sends all the files in the repository
7. stop: Stops the current node
8. exit: Stops the application

## How to Run:

To start the application, execute the run.sh file by using the following command: `./run.sh` 

The application can be used to create a peer2peer network in a single machine by running the application in different terminals with different ports
