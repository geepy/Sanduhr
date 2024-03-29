# Sanduhr
Ein Projekt zum Malen der Uhrzeit in Sand mithilfe von Arduino ESP8266 und Servos.

**_Work in Progress_**

## Simulation
Um die Funktion der Servoarme und die verwendeten Algorithmen zu testen, wurde eine HTML-Seite mit Canvs und integriertem JavaScript erstellt.

Die Seite [index.html](https://htmlpreview.github.io/?https://github.com/geepy/Sanduhr/blob/master/index.html) ist der aktuelle Entwicklungsstand der Simulation.

## Hardware
Als Hardware wird ein [Lolin Wemos D1 Mini](https://www.wemos.cc/en/latest/d1/d1_mini.html) mit [MicroPython](https://micropython.org/) verwendet, der über ein [PCA9685-Multiplexer-Board](https://www.az-delivery.de/products/pca9685-servotreiber) bis zu 16 Servos ansteuern kann.
Drei Servos werden benötigt (linker Arm, rechter Arm, Stift heben/senken).
Zusätzlich spannt der D1 Mini ein WLAN-Netz auf, über das die Hardware angesteuert werden kann (so wird z.B. die zu zeichnende Uhrzeit als Parameter an den HTML-Server übergeben)
Der HTML-Server liefert auch die Simulation-Seite aus, so dass die Simulation "portabel" ist.

# Software
Die Simulations-Software wurde mechanisch in Python-Code konvertiert. Die Hardware-Treiber (pca9685.py) und die HTML-Oberfläche in server.py.

# Verweise
Das Projekt wurde durch die folgenden Quellen inspiriert:
+ [FabLab Nürnberg PlotClock](https://github.com/fablabnbg/plotclock)
+ [Making Of A Sea Shell Sand Clock](https://mcuoneclipse.com/2016/11/23/making-of-sea-shell-sand-clock/)
+ [Heise Sanduhr 2.0, vertrieben durch Elektor](https://www.youtube.com/watch?v=YRU9UTVA9bU&t=391s) (leider nicht mehr erhältlich)
+ [Sanduhr 3.0](https://www.heise.de/ratgeber/Sanduhr-3-0-Plotter-Uhr-mit-leuchtenden-Ziffern-4256954.html)
