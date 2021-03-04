# Sanduhr
Ein Projekt zum Malen der Uhrzeit in Sand mithilfe von Arduino ESP8266 und Servos.

## Simulation
Um die Funktion der Servoarme und die verwendeten Algorithmen zu testen, wurde eine HTML-Seite mit Canvs und integriertem JavaScript erstellt.

Die Seite [zwei.html](https://htmlpreview.github.io/?https://github.com/geepy/Sanduhr/blob/master/zwei.html) ist der aktuelle Entwicklungsstand.

## Hardware
Als Hardware wird ein [Lolin Wemos D1 Mini](https://www.wemos.cc/en/latest/d1/d1_mini.html) mit [MicroPython](https://micropython.org/) verwendet, der über ein [PCA9685-Multiplexer-Board](https://www.az-delivery.de/products/pca9685-servotreiber) bis zu 16 Servos ansteuern kann.
Drei Servos werden benötigt (linker Arm, rechter Arm, Stift heben/senken).
