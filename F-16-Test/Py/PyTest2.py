#!/usr/bin/env python3
import serial
import time
from evdev import UInput, ecodes as e, AbsInfo

# ==============================
# CONFIGURACIÓN
# ==============================
SERIAL_PORT = "/dev/ttyUSB0"  # Ajustá según tu Arduino, puede ser /dev/ttyACM0 o similar se debe al puerto en el que reconozca el sistema operativo a tu Arduino, puedes verificarlo con `ls /dev/tty*` antes y después de conectar el Arduino para identificar el puerto correcto.
BAUDRATE = 115200 # Velocidad de comunicación con Arduino, preferiblemente 115200 para una comunicación rápida y estable.

AXIS_MIN = -32768
AXIS_MAX = 32767

# ==============================
# Crear joystick virtual
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
        e.ABS_X: abs_info,   # A0 Axis1
        e.ABS_Y: abs_info,   # A1 Axis2
        e.ABS_Z: abs_info,   # A2 (Throttle) Axis3
        e.ABS_RX: abs_info,  # A3 (Rudder)   Axis4
        e.ABS_RY: abs_info,  # A4 Axis5
        e.ABS_RZ: abs_info,  # A5 Axis6
    }
}

ui = UInput(capabilities, name="Arduino Virtual Joystick", bustype=e.BUS_USB)
print("Joystick virtual creado. Esperando datos de Arduino... Y Enviandolos al Joystick Virtual...")

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # Espera que Arduino se inicie

# ==============================
# LOOP PRINCIPAL
# ==============================
try:
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue

        parts = line.split(",")
        if len(parts) != 6:
            continue

        try:
            a0, a1, a2, a3, a4, a5 = map(int, parts)
        except ValueError:
            continue

        # Mapear valores 0-1023 al rango de ABS
        ax_x  = int((a0 / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)
        ax_y  = int((a1 / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)
        ax_z  = int((a2 / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)
        ax_rx = int((a3 / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)
        ax_ry = int((a4 / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)
        ax_rz = int((a5 / 1023) * (AXIS_MAX - AXIS_MIN) + AXIS_MIN)

        # Enviar valores al joystick virtual
        ui.write(e.EV_ABS, e.ABS_X, ax_x)
        ui.write(e.EV_ABS, e.ABS_Y, ax_y)
        ui.write(e.EV_ABS, e.ABS_Z, ax_z)
        ui.write(e.EV_ABS, e.ABS_RX, ax_rx)
        ui.write(e.EV_ABS, e.ABS_RY, ax_ry)
        ui.write(e.EV_ABS, e.ABS_RZ, ax_rz)
        ui.syn()

except KeyboardInterrupt:
    print("\nSaliendo...")
finally:
    ui.close()
    ser.close()