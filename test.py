import serial.tools.list_ports

myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
# print (myports)
for a,b,c in myports:
  print(a)
  print(b)
  print(c)
# for com in list(serial.tools.list_ports.comports()):
#   print( com)