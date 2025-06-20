
import ttkbootstrap as ttk
from ctypes import windll
from sistem_utils.system_utils import (

    get_cpu_info,
    get_memory_info,
    get_internet_info,
    little_gpu_info

)


def hide_from_taskbar(window):
    hwnd = windll.user32.GetParent(window.winfo_id())

    ex_style = windll.user32.GetWindowLongW(hwnd, -20)
    ex_style = ex_style | 0x00000080

    windll.user32.SetWindowLongW(hwnd, -20, ex_style)
    windll.user32.ShowWindow(hwnd, 5)


root = ttk.Window(themename="superhero")
root.title("Painel de Monitoramento")
root.geometry("750x20+665+0")
root.resizable(False, False)
root.overrideredirect(True)
root.after(0, lambda: hide_from_taskbar(root))

root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 700
window_height = 20

x_position = screen_width - window_width - 10
y_position = 10

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Configurações de transparência e "sempre por cima"
root.attributes('-alpha', 0.8)
root.attributes('-topmost', True)
# style


# Frames

frame_1 = ttk.Frame(height=20, width=700, bootstyle="dark")
frame_1.grid(row=0, column=0)
frame_1.grid_propagate(False)


# Label

label_1 = ttk.Label(frame_1, text="CPU", bootstyle="inverse-dark")
label_1.grid(row=0, column=0,)
label_2 = ttk.Label(frame_1, text="Memoria", bootstyle="inverse-dark")
label_2.grid(row=0, column=1,)
label_3 = ttk.Label(frame_1, text="Rede", bootstyle="inverse-dark")
label_3.grid(row=0, column=2,)
label_4 = ttk.Label(frame_1, text="GPU",
                    bootstyle="inverse-dark", wraplength=270)
label_4.grid(row=0, column=3, )


def little_update():

    cpu = get_cpu_info()
    memory = get_memory_info()
    rede = get_internet_info()
    gpu = little_gpu_info()

    label_1.config(text=f" CPU {cpu}")
    label_2.config(text=f" RAM {memory}")
    label_3.config(text=rede)
    label_4.config(text=gpu)

    root.after(1000, little_update)


little_update()

root.mainloop()
