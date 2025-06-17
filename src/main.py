import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sistem_utils.system_utils import (
    get_memory_info,
    get_cpu_info,
    get_partition_info,
    get_partition_used,
    get_internet_info,
    get_gpu_info,
    process_info_with_pid,
    colum_cpu,
    colum_memory, on_item_select,
    terminate_process,
)


# Criar janela principal
root = ttk.Window(themename="superhero")
root.title("Painel de Monitoramento")
root.geometry("600x500")
root.resizable(False, False)
root.overrideredirect(False)

# Criar os frames
frame_1 = ttk.Frame(root, height=453, width=176, bootstyle="dark")
frame_1.grid(row=0, column=0,)
frame_1.grid_propagate(False)

frame_2 = ttk.Frame(root, height=453, width=450, bootstyle="success")
frame_2.grid(row=0, column=1, columnspan=2)
frame_2.grid_propagate(False)

frame_3 = ttk.Frame(root, height=50, width=600, bootstyle="dark")
frame_3.grid(row=1, column=0, columnspan=2)
frame_3.grid_propagate(False)

# Criar labels
label = ttk.Label(frame_1, text="Carregando...",
                  justify=CENTER, bootstyle="inverse-dark", wraplength=155, anchor="center",)
label.grid(row=0, column=0,  pady=5, padx=15)
label.config(foreground="white")

label_2 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="inverse-dark", wraplength=155)
label_2.grid(row=1, column=0,  pady=5,)
label_2.config(foreground="white")

label_3 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="inverse-dark", wraplength=155)
label_3.grid(row=2, column=0,  pady=5, )
label_3.config(foreground="white")

label_4 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="inverse-dark", wraplength=155)
label_4.grid(row=3, column=0,  pady=5, )
label_4.config(foreground="white")

label_5 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="inverse-dark", wraplength=155)
label_5.grid(row=4, column=0,  pady=5, )
label_5.config(foreground="white")

label_6 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="inverse-dark", wraplength=155)
label_6.grid(row=5, column=0,  pady=5, )
label_6.config(foreground="white")

# Scrollbar Vertical
scrollbar = ttk.Scrollbar(frame_2, orient="vertical")

# Criar ListBox
listbox = ttk.Treeview(frame_2, columns=("Nome", "CPU", "Memoria"),
                       show="headings", height=30, yscrollcommand=scrollbar.set, bootstyle="dark")
scrollbar.config(command=listbox.yview)

listbox.grid(row=0, column=1, )
scrollbar.grid(row=0, column=2,  sticky="ns",)

# Define os Titulos das Colunas
listbox.heading("Nome", text="Nome", )
listbox.heading("CPU", text="CPU")
listbox.heading("Memoria", text="Memoria")

# Define a Largura (ajustei para incluir coluna PID)
listbox.column("Nome", width=136,)
listbox.column("CPU", width=136, anchor="center")
listbox.column("Memoria", width=136, anchor="center")

# Bind do evento de seleção (modificado para passar o listbox como parâmetro)
listbox.bind('<<TreeviewSelect>>',
             lambda event: on_item_select(event, listbox))

# botão (modificado para chamar a função terminate_process)
botao = ttk.Button(frame_3, text="Finalizar Processo",
                   bootstyle="light", command=terminate_process)
botao.grid(row=0, column=1, padx=470, pady=10)


def update_system():
    #"""Atualiza as informações do sistema na interface"""
    try:
        memory_info = get_memory_info()
        cpu_info = get_cpu_info()
        partition_info = get_partition_info()
        partition_used = get_partition_used()
        internet_info = get_internet_info()
        gpu_info = get_gpu_info()

        # Usar a função modificada que inclui PID
        process_list = process_info_with_pid()

        label.config(text=memory_info)
        label_2.config(text=cpu_info)
        label_3.config(text=partition_info)
        label_4.config(text=partition_used)
        label_5.config(text=internet_info)
        label_6.config(text=gpu_info)

        listbox.heading("CPU", text=F" CPU {colum_cpu()}")
        listbox.heading("Memoria", text=f'Memoria {colum_memory()}')

        for row in listbox.get_children():
            listbox.delete(row)

        for proc in process_list:
            listbox.insert("", "end", values=(
                proc['nome'], proc['cpu'], proc['memoria'], proc['pid']))

    except Exception as e:
        print(f"Erro ao atualizar sistema: {e}")

    root.after(1000, update_system)


update_system()
root.mainloop()
