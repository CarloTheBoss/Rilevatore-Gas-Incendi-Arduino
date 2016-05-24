"""
Print plots of temperature-humidity and gas concentration (ppm) 
measured by Arduino and read in real-time through serial port.
Also save Arduino's data to a .txt.
@author Carlo Buccisano
"""

import time
import serial
from datetime import datetime
import matplotlib.pyplot as plt

TIME_INTERVAL = 13 # Time interval in seconds between Arduino's measures

gas_names = ["CO", "Smoke", "CH4", "Alcohol", "H2", "Propane", "LPG"]

# File to write
file_path = "rilevatore.log"
file_rows = [] # lines to print to file

# Points to plot:
x = []
ytemp = []
yhum = []
ygas = [ [] for j in range(7) ]

MAX_X = 100 # last point on x axis
MAX_Y = 100 # last point on y axis

# Serial connection to Arduino:
ser = serial.Serial('/dev/ttyACM0')

# Read random stuff, which is always at the beginning
for i in range(15): ser.readline()

first_date = "" # first measure's data, used as offset for the others
mod = 0 # indexes modulus 9
tmp_x, tmp_y = [], [] # temporary arrays to store data

plt.figure(1, figsize = (25, 25))
plt.axis([0, MAX_X, 0, MAX_Y])
plt.ion()

plt.subplot(211)
plt.plot(x, ytemp, 'r', x, yhum, 'b')
plt.grid(True)
plt.title("Temperature (°C) and Humidity (%)")
plt.xlabel("Interval of %d seconds" %(TIME_INTERVAL))
plt.legend(['Temperature', 'Humidity'])

plt.subplot(212)
plt.plot(x, ygas[0], 'b', x, ygas[1], 'g', x, ygas[2], 'r', x, ygas[3],\
              'y', x, ygas[4], 'k', x, ygas[5], 'c', x, ygas[6], 'm')  
plt.grid(True)
plt.title("Gas concentration (ppm)")
plt.xlabel("Interval of %d seconds" %(TIME_INTERVAL))
plt.legend(gas_names)

while True:
	row = ser.readline().decode().replace('\n', '')
	print(row)
	
	if "Humidity" in row: file_rows += [time.strftime("%c")]
	file_rows += [row]

		
	if len(row)==0 or "calibrat" in row:
		mod, tmp_x, tmp_y, file_rows = 0, [], [], []
		continue

	if mod==0: # Temp and hum
		if "Temperature" not in row or "Humidity" not in row: 
			mod, tmp_x, tmp_y, file_rows = 0, [], [], []
			continue
		
		# Add timestamp:
		if first_date=="": first_date=time.strftime("%c")
		offset = (datetime.strptime(time.strftime("%c"), "%c")\
		            - datetime.strptime(first_date, "%c")).seconds
		tmp_x += [(offset // TIME_INTERVAL)]
		
		# Read data:
		humidity, temperature = [k.split(' ')[1] for k in row.split('\t')]
		tmp_y += [float(temperature)] + [float(humidity)]
		mod=1
	
	elif mod<=7: # Gas
		if "ppm" not in row:
			mod, tmp_x, tmp_y, file_rows = 0, [], [], []
			continue

		val = row.split(' ')[2]
		tmp_y += [float(val)]
		mod+=1

	else: # Flame and save datas
		x += [ tmp_x[0] ]
		ytemp += [ tmp_y[0] ]
		yhum += [ tmp_y[1] ]
		for i in range(7): ygas[i] += [ tmp_y[2+i] ]
		
		# Print current lines to file
		
		with open(file_path, "a") as f:
			f.write("\n".join(file_rows))
			f.write("\n")
			f.flush()
		
		plt.subplot(211)
		plt.plot(x, ytemp, 'r', x, yhum, 'b')

		plt.subplot(212)
		plt.plot(x, ygas[0], 'b', x, ygas[1], 'g', x, ygas[2], 'r',\
	             x, ygas[3], 'y', x, ygas[4], 'k', x, ygas[5], 'c', \
	             x, ygas[6], 'm')

		plt.draw()
		plt.pause(0.001)
		mod, tmp_x, tmp_y, file_rows = 0, [], [], []
