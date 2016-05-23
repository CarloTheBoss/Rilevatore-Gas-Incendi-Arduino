import serial
import time

ser = serial.Serial('/dev/ttyACM0')
file_path = "rilevatore.log"

with open(file_path, "w") as f:
	while True:
		s = ser.readline().decode().replace("\n", "")
		if "Humidity" in s: 
			print("\n" + time.strftime("%c"))
			f.write("\n" + time.strftime("%c") + "\n")
		print(s)
		f.write(s + "\n")
		f.flush()
