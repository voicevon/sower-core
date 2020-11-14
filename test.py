import serial.tools.list_ports

myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
# print (myports)
for name,chip,detail in myports:
  print(name)
  print(chip)
  print(detail)
# for com in list(serial.tools.list_ports.comports()):
#   print( com)