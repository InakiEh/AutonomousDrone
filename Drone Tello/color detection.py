import threading
import socket
import cv2
import numpy as np

host = '192.168.10.2'
port = 8889

VS_UDP_IP = '0.0.0.0'
VS_UDP_PORT = 11111

locaddr = (host,port)
tello_address = ('192.168.10.1', 8889)

cap = None

height = 340
width = 480

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('',port))

def recv():
  count = 0
  while True:
    try:
      data, server = sock.recvfrom(1518)
      print(data.decode(encoding="utf-8"))
    except Exception:
      print('\nExit . . .\n')
      break

print('\r\n\r\nTello Python3 Demo.\r\n')
print('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')
print('end -- quit demo.\r\n')

#recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()

sock.sendto('command'.encode(' utf-8 '), tello_address)

sock.sendto('streamon'.encode(' utf-8 '), tello_address)
udp_video_address = 'udp://@' + VS_UDP_IP + ':' + str(VS_UDP_PORT)

if cap is None:
    cap = cv2.VideoCapture(udp_video_address)

if not cap.isOpened():
    cap.open(udp_video_address)


#cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red color
    low_red = np.array([161, 155, 84])
    high_red = np.array([179, 255, 255])

    low_red1 = np.array([0, 50, 20], np.uint8)
    high_red1 = np.array([5, 255, 255], np.uint8)

    low_red2 = np.array([175, 50, 20], np.uint8)
    high_red2 = np.array([180, 255, 255], np.uint8)
    red_mask = cv2.inRange(hsv_frame, low_red, high_red)
    red_mask1 = cv2.inRange(hsv_frame, low_red1, high_red1)
    red_mask2 = cv2.inRange(hsv_frame, low_red2, high_red2)
    rmask = cv2.add(red_mask1, red_mask2)
    red = cv2.bitwise_and(frame, frame, mask=rmask)

    # Blue color
    low_blue = np.array([94, 80, 0])
    high_blue = np.array([126, 255, 255])
    blue_mask = cv2.inRange(hsv_frame, low_blue, high_blue)
    blue = cv2.bitwise_and(frame, frame, mask=blue_mask)

    # Green color
    low_green = np.array([30, 130, 90])
    high_green = np.array([70, 200, 200])
    green_mask = cv2.inRange(hsv_frame, low_green, high_green)
    green = cv2.bitwise_and(frame, frame, mask=green_mask)

    # Pink color
    #low_pink = np.array([130, 115, 205])
    #high_pink = np.array([172, 185, 255])
    low_pink = np.array([152, 113, 90])
    high_pink = np.array([172, 185, 255])
    pink_mask = cv2.inRange(hsv_frame, low_pink, high_pink)
    pink = cv2.bitwise_and(frame, frame, mask=pink_mask)

    # Every color except white
    low = np.array([0, 42, 0])
    high = np.array([179, 255, 255])
    mask = cv2.inRange(hsv_frame, low, high)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    #cv2.imshow("Frame", frame)
    #cv2.imshow("Red", red)
    cv2.imshow("Blue", blue)
    #cv2.imshow("Green", green)
    #cv2.imshow("Pink", pink)
    #cv2.imshow("Result", result)

    key = cv2.waitKey(1)
    if key == 27:
        break