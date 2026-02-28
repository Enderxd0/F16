#!/usr/bin/env python3
import serial
import time
from evdev import UInput, ecodes as e, AbsInfo

# ==============================
# CONFIGURACIÓN Hay una arduino que envia dos valores de 0 a 1023 separados por coma (A0,A1) 
# ==============================
SERIAL_PORT = "/dev/ttyUSB0"  # Ajustá según tu Arduino
BAUDRATE = 115200

AXIS_MIN = -32768
AXIS_MAX = 32767

# ==============================
# Crear joystick virtual es neseario que este para que el F-16 lo reconozca como un joystick y no como un mouse o teclado y poder usarlo en el juego
# ==============================
abs_info = AbsInfo(
    value=0,
    min=AXIS_MIN,
    max=AXIS_MAX,
    fuzz=0,
    flat=0,
    resolution=0
)

capabilities = {
    e.EV_ABS: {
        e.ABS_X: abs_info,  # A0
        e.ABS_Y: abs_info,  # A1
    }
}

ui = UInput(capabilities, name="Arduino HOTAS Simple", bustype=e.BUS_USB)
print("Joystick virtual creado.")

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

# ==============================
# LOOP PRINCIPAL No borrar cosas sino añadir las funciones
# ==============================
try:
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue

        parts = line.split(",")
        if len(parts) != 2:
            continue

        try:
            a0 = int(parts[0])
            a1 = int(parts[1])
        except ValueError:
            continue

        # Mapeo directo al rango completo de ABS_X/ABS_Y
        ax_x = int((a0 / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)
        ax_y = int((a1 / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)

        ui.write(e.EV_ABS, e.ABS_X, ax_x)
        ui.write(e.EV_ABS, e.ABS_Y, ax_y)
        ui.syn()

except KeyboardInterrupt:
    print("\nSaliendo...")
finally:
    ui.close()
    ser.close()