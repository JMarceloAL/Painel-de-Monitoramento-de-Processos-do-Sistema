from psutil import virtual_memory, cpu_percent, cpu_freq, disk_usage, disk_partitions, net_io_counters
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


# Criar janela principal
root = ttk.Window(themename="vapor")
root.title("Painel de Monitoramento")
root.geometry("600x500")
root.resizable(False, False)
root.overrideredirect(False)


# Criar o frame
frame_1 = ttk.Frame(root, height=400, width=140, bootstyle="info")
frame_1.pack(expand=False)
frame_1.grid(row=0, column=0, )
frame_1.grid_propagate(False)
frame_2 = ttk.Frame(root, height=400, width=500, bootstyle="Primary")

frame_2.grid(row=0, column=1, columnspan=2)
frame_3 = ttk.Frame(root, height=100, width=600, bootstyle="Success")

frame_3.grid(row=1, column=0, columnspan=2)


# Criar label
label = ttk.Label(frame_1, text="ola mundo",
                  justify=CENTER, bootstyle="inverse-info")
label.grid(row=0, column=0,  pady=10)
label_2 = ttk.Label(frame_1, text="ola mundo",
                    justify=CENTER, bootstyle="inverse-info")

label_2.grid(row=1, column=0, )
label_3 = ttk.Label(frame_1, text="ola mundo",
                    justify=CENTER, bootstyle="inverse-info")

label_3.grid(row=2, column=0, )
label_4 = ttk.Label(frame_1, text="ola mundo",
                    justify=CENTER, bootstyle="inverse-info")

label_4.grid(row=3, column=0, )
label_5 = ttk.Label(frame_1, text="ola mundo",
                    justify=CENTER, bootstyle="inverse-info")

label_5.grid(row=4, column=0, )


def get_network_speed(value):

    bytes_sent = value.bytes_sent
    bytes_recv = value.bytes_recv

    return f"S: {bytes_sent / 1024 / 1024:.1f}KB R:{bytes_recv / 1024 / 1024:.1f}KB"


def bytes_to_gigas(value):
    return f'{value / 1024 / 1024 / 1024:.1f} GB'


def showdisk(value):
    discos = []
    for partitio in value:
        convert = partitio.device
        discos.append(convert)
        string = ''.join(map(str, discos))
    return string


def get_disk_used_space(value):
    partitions = disk_partitions()
    result = []

    for partition in partitions:
        try:
            usage = value(partition.mountpoint)
            used_gb = usage.used / (1024**3)
            total_gb = usage.total / (1024**3)
            percent = usage.percent
            result.append(
                f"{partition.device}: {total_gb:.1f}GB  {used_gb:.1f}GB\n {percent}% \n")
        except:
            result.append(f"{partition.device}: 0GB")

    return " ".join(result)


def Update_Sistem():

    # Memória
    memoria = virtual_memory()
    Memory_info = f" Memoria \n {(bytes_to_gigas(memoria.used))} / {(bytes_to_gigas(memoria.total))} / {memoria.percent}% "

    # CPU
    cpu_use = cpu_percent(interval=0.1)
    cpu_frq = cpu_freq()
    CPU_info = f"CPU \n {cpu_use} % / {cpu_frq.current}Ghz"
    # Partição

    diskpartitions = disk_partitions()
    Partition_Info = f" Discos \n {showdisk(diskpartitions)} "
    disks_used = disk_usage
    Partition_used = f" {get_disk_used_space(disks_used)}"
    # Memória

    # Internet

    Internet = net_io_counters()
    Internet_info = f"Internet \n {get_network_speed(Internet)}"

    label.config(text=Memory_info)
    label_2.config(text=CPU_info)
    label_3.config(text=Partition_Info)
    label_4.config(text=Partition_used)
    label_5.config(text=Internet_info)

    root.after(1000, Update_Sistem)


Update_Sistem()
root.mainloop()
