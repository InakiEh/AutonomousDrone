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

def dibujar(mask,color):
  contornos,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  for c in contornos:
    area = cv2.contourArea(c)
    if area > 3000:
      M = cv2.moments(c)
      if (M["m00"]==0): M["m00"]=1
      x = int(M["m10"]/M["m00"])
      y = int(M['m01']/M['m00'])
      nuevoContorno = cv2.convexHull(c)
      cv2.circle(frame,(x,y),7,(0,255,0),-1)
      cv2.putText(frame,'{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
      cv2.drawContours(frame, [nuevoContorno], 0, color, 3)
      if area > 15000:
        color = (255, 255, 255)
      cv2.drawContours(frame, [nuevoContorno], 0, color, 3)

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

rosaBajo = np.array([161, 200, 84],np.uint8) #ultimo valor es la saturacion, valor del medio brillo
rosaAlto = np.array([172, 255, 255],np.uint8)

azulBajo = np.array([94,80,0],np.uint8)
azulAlto = np.array([126,255,255],np.uint8)

redBajo1 = np.array([0,50,20],np.uint8)
redAlto1 = np.array([5,255,255],np.uint8)

redBajo2 = np.array([175,50,20],np.uint8)
redAlto2 = np.array([180,255,255],np.uint8)

verdeBajo = np.array([30,130,90],np.uint8)
verdeAlto = np.array([70,200,200],np.uint8)

font = cv2.FONT_HERSHEY_SIMPLEX

while True:
  ret,frame = cap.read()
  frame = cv2.resize(frame, (width, height))
  if ret == True:
    frameHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    maskrosa = cv2.inRange(frameHSV,rosaBajo,rosaAlto)
    maskazul = cv2.inRange(frameHSV,azulBajo,azulAlto)
    maskRed1 = cv2.inRange(frameHSV,redBajo1,redAlto1)
    maskRed2 = cv2.inRange(frameHSV,redBajo2,redAlto2)
    maskRed = cv2.add(maskRed1,maskRed2)
    maskverde = cv2.inRange(frameHSV,verdeBajo,verdeAlto)

    dibujar(maskrosa,(128,0,255))
    dibujar(maskazul,(255,0,0))
    dibujar(maskverde,(20,255,57))
    dibujar(maskRed,(0,0,255))

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('s'):
      break

cap.release()
cv2.destroyAllWindows()