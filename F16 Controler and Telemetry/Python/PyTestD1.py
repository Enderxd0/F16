#!/usr/bin/env python3

import serial
import time
import json
import subprocess
from evdev import UInput, ecodes as e, AbsInfo

# ==============================
# CONFIGURACIÓN
# ==============================

SERIAL_PORT = "/dev/ttyUSB0"
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

# Ahora solo 11 botones reales
button_codes = [
    e.BTN_0, e.BTN_1, e.BTN_2, e.BTN_3,
    e.BTN_4, e.BTN_5, e.BTN_6, e.BTN_7,
    e.BTN_8, e.BTN_9, e.BTN_TRIGGER
]

capabilities = {
    e.EV_ABS: {
        e.ABS_X: abs_info,
        e.ABS_Y: abs_info,
        e.ABS_Z: abs_info,
        e.ABS_RX: abs_info,
        e.ABS_RY: abs_info,
        e.ABS_RZ: abs_info,
    },
    e.EV_KEY: button_codes
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
# ABRIR TELNET A FLIGHTGEAR
# ==============================

proc = subprocess.Popen(
    ["telnet", "localhost", "5401"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

time.sleep(1)
print("✔ Conectado a FlightGear")

# ==============================
# FUNCIONES
# ==============================

def map_axis(value):
    return int((value / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)

def rpm_to_servo(n2_value):
    try:
        n2 = float(n2_value)
    except:
        return None

    if n2 < 0: n2 = 0
    if n2 > 100: n2 = 100

    return int((n2 / 100.0) * 180.0)

# ==============================
# LOOP PRINCIPAL
# ==============================

try:
    while True:

        # ===================================
        # 1️⃣ LEER RPM DEL SIM
        # ===================================

        proc.stdin.write("get /engines/engine[0]/n2\n")
        proc.stdin.flush()

        time.sleep(0.1)

        n2_value = None

        while True:
            line = proc.stdout.readline()
            if not line:
                break

            if "/engines/engine[0]/n2" in line:
                parts = line.split("'")
                if len(parts) >= 2:
                    n2_value = parts[1]
                break

        if n2_value:
            servo_angle = rpm_to_servo(n2_value)
            if servo_angle is not None:
                ser.write(f"{servo_angle}\n".encode())

        # ===================================
        # 2️⃣ LEER ARDUINO
        # ===================================

        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue

        parts = line.split(",")

        # Ahora deben ser 17 valores
        if len(parts) != 17:
            continue

        try:
            values = list(map(int, parts))
        except:
            continue

        analog = values[0:6]
        digital = values[6:17]  # 11 botones

        # Guardar en archivo
        data = {
            "analog": analog,
            "digital": digital,
            "rpm": n2_value,
            "timestamp": time.time()
        }

        with open(INO_FILE, "w") as f:
            json.dump(data, f, indent=4)

        # ======================
        # ACTUALIZAR JOYSTICK
        # ======================

        ui.write(e.EV_ABS, e.ABS_X,  map_axis(analog[0]))
        ui.write(e.EV_ABS, e.ABS_Y,  map_axis(analog[1]))
        ui.write(e.EV_ABS, e.ABS_Z,  map_axis(analog[2]))
        ui.write(e.EV_ABS, e.ABS_RX, map_axis(analog[3]))
        ui.write(e.EV_ABS, e.ABS_RY, map_axis(analog[4]))
        ui.write(e.EV_ABS, e.ABS_RZ, map_axis(analog[5]))

        for i in range(11):
            ui.write(e.EV_KEY, button_codes[i], digital[i])

        ui.syn()

        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nApagando sistema...")

finally:
    ui.close()
    ser.close()
    proc.terminate()