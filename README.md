# Rilevatore-Gas-Incendi-Arduino
Rilevatore di incendi e concentrazioni di gas nocivi realizzato in Arduino e in Python3.
La presenza di fiamme è rilevata dal sensore [Grove Flame Sensor](http://www.seeedstudio.com/wiki/Grove_-_Flame_Sensor), la concentrazione di gas nocivi dal sensore [Grove MQ-2 Gas Sensor](http://www.seeedstudio.com/wiki/Grove_-_Gas_Sensor(MQ2)).
In caso di incendio o concentrazioni anomale di gas viene acceso un led rosso e il piezo dà l'allarme. Vi è anche un bottone per ricalibrare il sensore di gas e un display LCD per avere direttamente sott'occhio le principali informazioni rilevate. Viene infine registrata anche temperatura e umidità dal sensore [Grove Temperature and Humidity Sensor](http://www.seeedstudio.com/wiki/Grove_-_Temperature_and_Humidity_Sensor).

Il tutto è integrato con python3 (con scipy, numpy e matplotlib) che permette di avere grafici sui dati in tempo reale e di salvare i rilevamenti, con data e ora esatte, su un file di testo.
