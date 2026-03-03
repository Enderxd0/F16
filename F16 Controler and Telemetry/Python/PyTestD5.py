#!/usr/bin/env python3

import serial
import time
import subprocess
from evdev import UInput, ecodes as e, AbsInfo

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

AXIS_MIN = -32768
AXIS_MAX = 32767

# ==============================
# JOYSTICK
# ==============================

abs_info = AbsInfo(
    value=0,
    min=AXIS_MIN,
    max=AXIS_MAX,
    fuzz=0,
    flat=0,
    resolution=0
)

button_codes = [
    e.BTN_0, e.BTN_1, e.BTN_2, e.BTN_3,
    e.BTN_4, e.BTN_6, e.BTN_7,
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
print("✔ Joystick creado")

# ==============================
# ARDUINO
# ==============================

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.01)
time.sleep(2)
print("✔ Arduino conectado")

# FORZAR SERVO A 0°
ser.write(b"0\n")
time.sleep(1)

# ==============================
# TEST DE SERVO 10 VECES
# ==============================

print("🔧 Test servo 0 ↔ 180")

for i in range(10):
    ser.write(b"0\n")
    time.sleep(0.5)
    ser.write(b"180\n")
    time.sleep(0.5)

ser.write(b"0\n")
time.sleep(1)

print("✔ Test terminado\n")

# ==============================
# TELNET FlightGear
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
print("✔ FlightGear conectado")

last_rpm_time = 0
rpm_interval = 0.2
n2_value = 0

# ==============================
# FUNCIONES
# ==============================

def map_axis(value):
    return int((value / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)

def rpm_to_servo(n2):

    # Limites duros
    if n2 <= 60:
        return 180

    if n2 >= 100:
        return 0

    # Escalar 60-100 → 180-0
    scaled = (n2 - 60) / 40.0   # ahora rango 0-1
    angle = 180 - (scaled * 180.0)

    return int(angle)

# ==============================
# LOOP PRINCIPAL
# ==============================

try:
    while True:

        now = time.time()

        # ======================
        # LEER RPM
        # ======================
        if now - last_rpm_time > rpm_interval:

            proc.stdin.write("get /engines/engine[0]/n2\n")
            proc.stdin.flush()

            time.sleep(0.05)

            while True:
                line = proc.stdout.readline()
                if not line:
                    break

                if "/engines/engine[0]/n2" in line:
                    parts = line.split("'")
                    if len(parts) >= 2:
                        try:
                            n2_value = float(parts[1])
                        except:
                            pass
                    break

            angle = rpm_to_servo(n2_value)

            ser.write(f"{angle}\n".encode())

            last_rpm_time = now

        # ======================
        # LEER ARDUINO (JOYSTICK)
        # ======================

        line = ser.readline().decode(errors="ignore").strip()

        if line:
            parts = line.split(",")

            if len(parts) == 17:
                try:
                    values = list(map(int, parts))
                except:
                    continue

                analog = values[0:6]
                digital = values[6:17]

                ui.write(e.EV_ABS, e.ABS_X,  map_axis(analog[0]))
                ui.write(e.EV_ABS, e.ABS_Y,  map_axis(analog[1]))
                ui.write(e.EV_ABS, e.ABS_Z,  map_axis(analog[2]))
                ui.write(e.EV_ABS, e.ABS_RX, map_axis(analog[3]))
                ui.write(e.EV_ABS, e.ABS_RY, map_axis(analog[4]))
                ui.write(e.EV_ABS, e.ABS_RZ, map_axis(analog[5]))

                for i in range(min(len(button_codes), len(digital))):
                    ui.write(e.EV_KEY, button_codes[i], digital[i])

                ui.syn()

        time.sleep(0.005)

except KeyboardInterrupt:
    print("\nApagando...")

finally:
    ui.close()
    ser.close()
    proc.terminate()