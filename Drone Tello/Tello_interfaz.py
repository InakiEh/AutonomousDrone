import threading
import socket
import cv2
import numpy as np
import time

# Drone and camera settings variables
host = '192.168.10.2'
port = 8889

VS_UDP_IP = '0.0.0.0'
VS_UDP_PORT = 11111

tello_address = ('192.168.10.1', 8889)

cap = None
frame = None
ret = True
frame_counter = 0

height = 340
width = 480

# Movement Variables
forward = True
last_area = 0
last_color = 0    # 1:Red; 2:Blue; 3:Green; 4:Pink
blue = False
green = False
red = False
pink = False

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', port))

# Colors HSV parameters
low_pink = np.array([161, 200, 84], np.uint8)
high_pink = np.array([172, 255, 255], np.uint8)

low_blue = np.array([94, 80, 0], np.uint8)
high_blue = np.array([126, 255, 255], np.uint8)

low_red1 = np.array([0, 50, 20], np.uint8)
high_red1 = np.array([5, 255, 255], np.uint8)

low_red2 = np.array([175, 50, 20], np.uint8)
high_red2 = np.array([180, 255, 255], np.uint8)

low_green = np.array([30, 130, 90], np.uint8)
high_green = np.array([70, 200, 200], np.uint8)

font = cv2.FONT_HERSHEY_SIMPLEX

# Threads and Functions


def recv():
    count = 0
    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print('\nExit . . .\n')
            break

def draw(mask, color):
    global last_area
    global last_color
    global forward
    global blue
    global green
    global red
    global pink
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        area = cv2.contourArea(c)
        if area > 3000:
            mat = cv2.moments(c)
            if mat["m00"] == 0:
                mat["m00"] = 1
            x = int(mat["m10"]/mat["m00"])
            y = int(mat['m01']/mat['m00'])
            new_contour = cv2.convexHull(c)
            cv2.circle(frame, (x, y), 7, (0, 255, 0), -1)
            cv2.putText(frame, '{},{}'.format(x, y), (x+10, y), font, 0.75, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.drawContours(frame, [new_contour], 0, color, 3)
            if color == (128, 0, 255):
                print("Pink Detected")
                pink = True
                forward = False
            if color == (0, 0, 255):
                print("Red Detected")
                red = True
                forward = False
            if color == (255, 0, 0) and forward is True:
                print("Blue Detected")
                blue = True
                forward = False
            if color == (20, 255, 57) and forward is True:
                print("Green Detected")
                green = True
                forward = False
            if area > 15000:
                color = (255, 255, 255)
                last_area = area
                print(last_area)
            cv2.drawContours(frame, [new_contour], 0, color, 3)


def search():
    global last_area
    global forward
    global blue
    global green
    global red
    global pink
    time.sleep(4)
    sock.sendto('takeoff'.encode(' utf-8 '), tello_address)
    time.sleep(2)
    count = 0
    while count <= 10:
        if last_area >= 15000:
            if blue:
                time.sleep(1)
                sock.sendto('right 180'.encode(' utf-8 '), tello_address)
                time.sleep(2)
                print("Moved left")
                last_area = 0
                blue = False
                forward = False
            if green:
                time.sleep(1)
                sock.sendto('back 150'.encode(' utf-8 '), tello_address)
                time.sleep(2)
                print("Moved back")
                last_area = 0
                green = False
                forward = False
            if red:
                time.sleep(1)
                sock.sendto('up 70'.encode(' utf-8 '), tello_address)
                time.sleep(2)
                print("Going up")
                last_area = 0
                red = False
                forward = False
            if pink:
                time.sleep(1)
                sock.sendto('land'.encode(' utf-8 '), tello_address)
                time.sleep(2)
                print("Landing...")
                last_area = 0
                pink = False
                forward = False
        else:
            sock.sendto('cw 90'.encode(' utf-8 '), tello_address)
            time.sleep(2)
            sock.sendto('up 20'.encode(' utf-8 '), tello_address)
            time.sleep(2)
            sock.sendto('down 20'.encode(' utf-8 '), tello_address)
            time.sleep(2)
            forward = True
            count += 1
    sock.sendto('land'.encode(' utf-8 '), tello_address)


# recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()

# Initial command settings
sock.sendto('command'.encode(' utf-8 '), tello_address)
sock.sendto('streamon'.encode(' utf-8 '), tello_address)
udp_video_address = 'udp://@' + VS_UDP_IP + ':' + str(VS_UDP_PORT)

if cap is None:
    cap = cv2.VideoCapture(udp_video_address)
if not cap.isOpened():
    cap.open(udp_video_address)

searchThread = threading.Thread(target=search)
searchThread.start()

while True:
    #cv2.imwrite('TelloFrames/opencv' + str(frame_counter) + '.png', frame)
    ret, frame = cap.read()
    frame = cv2.resize(frame, (width, height))
    if ret == True:
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        pink_mask = cv2.inRange(frameHSV, low_pink, high_pink)
        blue_mask = cv2.inRange(frameHSV, low_blue, high_blue)
        red_mask1 = cv2.inRange(frameHSV, low_red1, high_red1)
        red_mask2 = cv2.inRange(frameHSV, low_red2, high_red2)
        red_mask = cv2.add(red_mask1, red_mask2)
        green_mask = cv2.inRange(frameHSV, low_green, high_green)

        draw(pink_mask, (128, 0, 255))
        draw(blue_mask, (255, 0, 0))
        draw(green_mask, (20, 255, 57))
        draw(red_mask, (0, 0, 255))

        cv2.imshow('frame', frame)
        frame_counter += 1
        if cv2.waitKey(1) == 27:
            break
"""
# Serial Drone Control 
while True:
    try:
        msg = input("");

        if not msg:
            break

        if 'end' in msg:
            print('...')
            sock.close()
            break

        # Send data
        msg = msg.encode(encoding="utf-8")
        sent = sock.sendto(msg, tello_address)
    except KeyboardInterrupt:
        print('\n . . .\n')
        sock.close()
        break
"""
cap.release()
# out.release()
cv2.destroyAllWindows()
# Stop video streaming
sock.sendto('streamoff'.encode(' utf-8 '), tello_address)
sock.sendto('land'.encode(' utf-8 '), tello_address)
sock.sendto('end'.encode(' utf-8 '), tello_address)
