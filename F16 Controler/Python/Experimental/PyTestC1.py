#!/usr/bin/env python3

import serial
import time
import json
from evdev import UInput, ecodes as e, AbsInfo

# ==============================
# CONFIGURACIÓN
# ==============================

SERIAL_PORT = "/dev/ttyUSB0"   # Cambiar si es necesario
BAUDRATE = 115200
INO_FILE = "ino.txt"

AXIS_MIN = -32768
AXIS_MAX = 32767

# ==============================
# CREAR JOYSTICK VIRTUAL
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
        e.ABS_X: abs_info,
        e.ABS_Y: abs_info,
        e.ABS_Z: abs_info,
        e.ABS_RX: abs_info,
        e.ABS_RY: abs_info,
        e.ABS_RZ: abs_info,
    },
    e.EV_KEY: [
        e.BTN_0, e.BTN_1, e.BTN_2, e.BTN_3,
        e.BTN_4, e.BTN_5, e.BTN_6, e.BTN_7,
        e.BTN_8, e.BTN_9, e.BTN_TRIGGER,
        e.BTN_THUMB
    ]
}

ui = UInput(capabilities, name="F16 HOTAS Virtual", bustype=e.BUS_USB)
print("✔ Joystick virtual creado")

# ==============================
# CONECTAR ARDUINO
# ==============================

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

print("✔ Conectado al Arduino")

# ==============================
# FUNCIONES
# ==============================

def map_axis(value):
    return int((value / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)

# ==============================
# LOOP PRINCIPAL
# ==============================

try:
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue

        parts = line.split(",")

        # Deben ser 18 valores
        if len(parts) != 18:
            continue

        try:
            values = list(map(int, parts))
        except ValueError:
            continue

        # ======================
        # Separar datos
        # ======================

        analog = values[0:6]
        digital = values[6:18]

        # ======================
        # GUARDAR EN ino.txt
        # ======================

        data = {
            "analog": {
                "A0": analog[0],
                "A1": analog[1],
                "A2": analog[2],
                "A3": analog[3],
                "A4": analog[4],
                "A5": analog[5]
            },
            "digital": {
                "D2": digital[0],
                "D3": digital[1],
                "D4": digital[2],
                "D5": digital[3],
                "D6": digital[4],
                "D7": digital[5],
                "D8": digital[6],
                "D9": digital[7],
                "D10": digital[8],
                "D11": digital[9],
                "D12": digital[10],
                "D13": digital[11]
            },
            "timestamp": time.time()
        }

        with open(INO_FILE, "w") as f:
            json.dump(data, f, indent=4)

        # ======================
        # ACTUALIZAR JOYSTICK
        # ======================

        # Ejes
        ui.write(e.EV_ABS, e.ABS_X,  map_axis(analog[0]))
        ui.write(e.EV_ABS, e.ABS_Y,  map_axis(analog[1]))
        ui.write(e.EV_ABS, e.ABS_Z,  map_axis(analog[2]))
        ui.write(e.EV_ABS, e.ABS_RX, map_axis(analog[3]))
        ui.write(e.EV_ABS, e.ABS_RY, map_axis(analog[4]))
        ui.write(e.EV_ABS, e.ABS_RZ, map_axis(analog[5]))

        # Botones
        button_codes = [
            e.BTN_0, e.BTN_1, e.BTN_2, e.BTN_3,
            e.BTN_4, e.BTN_5, e.BTN_6, e.BTN_7,
            e.BTN_8, e.BTN_9, e.BTN_TRIGGER,
            e.BTN_THUMB
        ]

        for i in range(12):
            ui.write(e.EV_KEY, button_codes[i], digital[i])

        ui.syn()

except KeyboardInterrupt:
    print("\nApagando sistema...")

finally:
    ui.close()
    ser.close()