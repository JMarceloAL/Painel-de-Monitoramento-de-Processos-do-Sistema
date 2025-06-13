from psutil import virtual_memory, cpu_percent, cpu_freq , disk_usage, disk_partitions
import tkinter as tk

def bytes_to_gigas(value):
    return f'{value / 1024 / 1024 / 1024:.1f} GB'


def showdpartition (value):
    for partitio in value:
     convert = partitio.device
     return convert


def update_system_info():
    # Memória
    memoria = virtual_memory()
    
    # CPU
    cpu_use = cpu_percent(interval=0.1)
    cpu_frq = cpu_freq()
    #Partição
    disk = disk_usage('/')
    diskpartitions = disk_partitions()
    
    
    texto = f"""MEMÓRIA:
Total: {bytes_to_gigas(memoria.total)}
Usada: {bytes_to_gigas(memoria.used)}
Livre: {bytes_to_gigas(memoria.available)}
Uso: {memoria.percent:.1f}%

CPU:
Uso Geral: {cpu_use:.1f}%
Frequência: {cpu_frq.current:.2f} MHz

ARMAZENAMENTO
Partição : {showdpartition(diskpartitions)}
Total : {bytes_to_gigas(disk.total)}
Uso: {disk.percent} %
Livre : {bytes_to_gigas(disk.free)}


"""
                                                                                                                                                                                     
    label1.config(text=texto)

    root.after(1000, update_system_info)

# Criar janela principal
root = tk.Tk()
root.title("Painel de Monitoramento")
root.geometry("500x400")

label1 = tk.Label(root, text="Carregando...", font=("Courier", 12), justify="left")
label1.pack(pady=20)

update_system_info()

root.mainloop()