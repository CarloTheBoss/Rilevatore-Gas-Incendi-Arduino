"""
Print plots of temperature-humidity and gas concentration (ppm) 
measured by Arduino and written on a .txt file.
@author Carlo Buccisano
"""

import time
from datetime import datetime
import matplotlib.pyplot as plt

TIME_INTERVAL = 13 # Time interval in seconds between Arduino's measures

gas_names = ["CO", "Smoke", "CH4", "Alcohol", "H2", "Propane", "LPG"]
file_path = "rilevatore.log"

def NotADate(s):
	return (len(s)==0 or "emperature" in s or "ppm" in s or "lame" in s)

# Points to plot:
x = []
ytemp = []
yhum = []
ygas = [ [] for j in range(7) ]

righe=[]
with open(file_path, "r") as f:
	righe = [i.replace('\n', '') for i in f.readlines() \
	           if "alibrat" not in i]

	
i=15 # first lines are random
first_date=""

while i+9 < len(righe):
	# random lines happen:
	if NotADate(righe[i]):
		i+=1
		continue
		
	# Timestamp:
	data_str = righe[i]
	if first_date=="": first_date=data_str
	offset = (datetime.strptime(data_str, "%c") - \
	          datetime.strptime(first_date, "%c")).seconds
	x.append(offset // TIME_INTERVAL)
	i+=1
	
	# Temperature and humidity:
	humidity, temperature = [k.split(' ')[1] for k in righe[i].split('\t')]
	ytemp.append( float(temperature) )
	yhum.append( float(humidity) )
	i+=1
	
	# Gases:
	
	for t in range(len(gas_names)):
		val = righe[i].split(' ')[2]
		ygas[t].append( float(val) )
		i+=1
	
	# Flame 
	i += 1

can_print = (len(x) == len(ytemp) and len(x)==len(yhum) and len(x)>0)
for j in range(7): can_print = can_print and (len(x)==len(ygas[j]))

if not can_print:
	print("Cannot print plot!")
else:
	plt.figure(1)

	# Temperature and humidity graphic:
	plt.subplot(211)
	plt.plot(x, ytemp, 'r', x, yhum, 'b')
	plt.grid(True)
	plt.title("Temperature (°C) and Humidity (%)")
	plt.xlabel("Interval of %d seconds" %(TIME_INTERVAL))
	plt.legend(['Temperature', 'Humidity'])
	plt.axis([0, x[ len(x) - 1], 0 ,max( max(ytemp), max(yhum) )+10 ]) 


	# Gas graphic:
	plt.subplot(212)
	plt.plot(x, ygas[0], 'b', x, ygas[1], 'g', x, ygas[2], 'r',\
			 x, ygas[3], 'y', x, ygas[4], 'k', x, ygas[5], 'c', \
			 x, ygas[6], 'm')
			 
	plt.grid(True)
	plt.title("Gas concentration (ppm)")
	plt.xlabel("Interval of %d seconds" %(TIME_INTERVAL))
	plt.legend(gas_names)
	plt.axis([0, x[ len(x) - 1], 0 ,\
	            max([max(ygas[k]) for k in range(7)])+30 ]) 

	plt.show()
