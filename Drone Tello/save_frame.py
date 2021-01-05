import socket
import threading
import cv2
import time

UDP_IP = '192.168.10.1'
UDP_PORT = 8889

VS_UDP_IP = '0.0.0.0'
VS_UDP_PORT = 11111

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
count = 0
while True:
    cv2.imwrite('TelloFrames/opencv'+str(count)+'.png', frame)     # save frame as JPEG file
    ret, frame = cap.read()
    print('Read a new frame: ', ret)
    cv2.imshow('frame', frame)
    count += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()