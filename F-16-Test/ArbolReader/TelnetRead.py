import telnetlib3 as telnetlib

HOST = "127.0.0.1"
PORT = 5501  # el telnet de FlightGear

tn = telnetlib.Telnet(HOST, PORT)

def read_until_prompt():
    return tn.read_until(b"/>").decode("utf-8")

def list_dir(path):
    tn.write(f"ls {path}\n".encode("utf-8"))
    output = read_until_prompt()
    lines = output.splitlines()
    children = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith(">"):
            children.append(line)
    return children

def get_value(path):
    tn.write(f"get {path}\n".encode("utf-8"))
    output = read_until_prompt()
    return output.strip()

def walk(path, file):
    children = list_dir(path)
    for child in children:
        full_path = f"{path}/{child}"
        try:
            value = get_value(full_path)
            file.write(f"{full_path} = {value}\n")
        except:
            # si da error, asumimos que es un directorio y recorremos
            walk(full_path, file)

with open("fg_tree.txt", "w") as f:
    walk("f16", f)