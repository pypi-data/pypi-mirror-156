import socket
import serial
class Server:
    """This class create a server"""
    def __init__(self, port,usbport,ip):
        """This function called when an object is created"""
        self.ip = ip
        self.s = None
        self.host = ""
        self.port = port
        self.conn = None
        self.addr = None
        self.usbport = usbport
        self.serial = None
       
    def create(self):
        """This create a Server and bind it with host and ip address """
        try:
            self.s = socket.socket()
        except socket.error as msg:
            print("Creation error "+msg)
        try:
            self.serial = serial.Serial(self.usbport,9600)
        except:
            print("Connect Arduino correctly")
        
        while True:
            try:
                self.s.bind((self.host,self.port))
                break;
            except socket.error as msg:
                print(f"Bind error {msg}")
    def getdata(self):
        """This function getdata from the clent and send it to via usb cable to arduino contiously"""
        while True:
            data = self.conn.recv(1024)
            if  data:
                print(data)
                self.serial.write(data)
            if self.conn.fileno:
                break;

                
    def accept(self):
        """This function accepts the connection requested from client """
        self.s.listen(5)
        self.conn,self.addr = self.s.accept()
        if (self.addr[0] == self.ip):
            self.getdata()
            self.conn.close()
        else:
            self.conn.close()

            
            
