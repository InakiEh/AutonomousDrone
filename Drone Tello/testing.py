import socket
import threading
import time

class Tello:
    def __init__(self):
        self.ip = '192.168.10.1'
        self.command_port = 8889
        self.address = (self.ip, self.command_port)
        self.response = None
        self.overtime = 3

        self.lock = threading.RLock()

        self.video_port = 11111

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.socket.bind(('', self.command_port))

        # init command and video stream

        self.receive_thread = threading.Thread(target = self.receive_response)
        self.receive_thread.daemon = True


        self.socket.sendto(b'command', self.address)
        print('sent: command')
        last_send = time.time()

        self.receive_thread.start()

        while self.response != b'OK':
            if time.time() - last_send >= self.overtime:
                self.socket.sendto(b'command', self.address)
                print('sent: command')
                last_send = time.time()

        # video stream

        self.video_socket.bind(('', self.video_port))

        self.receive_video_thread = threading.Thread(target = self.receive_video_data)
        self.receive_video_thread.daemon = True
        self.receive_video_thread.start()

        self.socket.sendto(b'streamon', self.address)
        print('sent: streamon')



    def receive_response(self):
        while True:
            with self.lock:
                self.response, ip = self.socket.recvfrom(3000)
                if self.response:
                        print(str(self.response))

    def receive_video_data(self):
        self.video_data = None
        while True:
            with self.lock:
                data, ip = self.video_socket.recvfrom(2048)
                if data:
                    print(str(data))


    def send_command(self, command):
        self.socket.sendto(command.encode('utf-8'), self.address)

    #control command:

    def takeoff(self):
        self.send_command('takeoff')

    def land(self):
        self.send_command('land')


drone = Tello()

drone.takeoff()
time.sleep(2)
drone.land()
