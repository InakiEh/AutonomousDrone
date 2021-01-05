import socket
import threading
import cv2
import time
# for tello access
UDP_IP = '192.168.10.1'
UDP_PORT = 8889

VS_UDP_IP = '0.0.0.0'
VS_UDP_PORT = 11111

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(('', UDP_PORT))
# Prepare objects for VideoCapture
cap = None
# Prepare objects for receiving data
response = None

def recv():
    count = 0
    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print('\nExit . . .\n')
            break

thread = threading.Thread(target = recv())
thread.daemon = True
thread.start()

socket.sendto('command'.encode(' utf-8 '), tello_address)

socket.sendto('streamon'.encode(' utf-8 '), tello_address)
udp_video_address = 'udp://@' + VS_UDP_IP + ':' + str(VS_UDP_PORT)

if cap is None:
    cap = cv2.VideoCapture(udp_video_address)
if not cap.isOpened():
    cap.open(udp_video_address)

cap.set(3,640)
cap.set(4,480)

while True:
    ret, frame = cap.read()
    #out.write(frame)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
#out.release()
cv2.destroyAllWindows()
# Stop video streaming
socket.sendto('streamoff'.encode(' utf-8 '), tello_address)
# Landing
#socket.sendto('land'.encode(' utf-8 '), tello_address)