import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
import os
import sys
import psutil  # Você pode precisar instalar: pip install psutil
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
    user,
    uptimes
)

# Variável global para controlar o processo
processo_little = None

# Criar janela principal
root = ttk.Window(themename="superhero")
root.title("Painel de Monitoramento")
root.geometry("600x545")
root.resizable(False, False)
root.overrideredirect(False)

# Criar os frames
top_frame = ttk.Frame(root,
                      bootstyle="dark",  width=600, height=45)
top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", )
top_frame.grid_propagate(False)

frame_1 = ttk.Frame(root, height=500, width=176, bootstyle="default")
frame_1.grid(row=1, column=0, rowspan=2, sticky="ns")
frame_1.grid_propagate(False)

frame_2 = ttk.Frame(root, height=450, width=450, bootstyle="default")
frame_2.grid(row=1, column=1, sticky="nsew")
frame_2.grid_propagate(False)

frame_3 = ttk.Frame(root, height=48, width=450, bootstyle="defaul")
frame_3.grid(row=2, column=1, sticky="nsew")
frame_3.grid_propagate(False)

# Criar labels
label_7 = ttk.Label(top_frame, text="Carregando...",
                    justify=CENTER, bootstyle="inverse-dark", wraplength=200, )
label_7.grid(row=0, column=0,  sticky="ew", pady=15, padx=10)
label_7.config(foreground="white")
label = ttk.Label(frame_1, text="Carregando...",
                  justify=CENTER, bootstyle="default", wraplength=155, anchor="center",)
label.grid(row=1, column=0,  padx=15, pady=10)
label.config(foreground="white")

label_2 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="default", wraplength=155)
label_2.grid(row=2, column=0,)
label_2.config(foreground="white")

label_3 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="default", wraplength=155)
label_3.grid(row=3, column=0,)
label_3.config(foreground="white")

label_4 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="default", wraplength=155)
label_4.grid(row=4, column=0,)
label_4.config(foreground="white")

label_5 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="default", wraplength=155)
label_5.grid(row=5, column=0,)
label_5.config(foreground="white")

label_6 = ttk.Label(frame_1, text="Carregando...",
                    justify=CENTER, bootstyle="default", wraplength=155)
label_6.grid(row=6, column=0,)
label_6.config(foreground="white")
label_8 = ttk.Label(top_frame, text="Carregando...",
                    justify=CENTER, bootstyle="inverse-dark", wraplength=280)
label_8.grid(row=0, column=1, padx=40)
label_8.config(foreground="white")

# Scrollbar Vertical
scrollbar = ttk.Scrollbar(frame_2, orient="vertical")

# Criar ListBox
listbox = ttk.Treeview(frame_2, columns=("Nome", "CPU", "Memoria"),
                       show="headings", height=27, yscrollcommand=scrollbar.set, bootstyle="success")
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
                   bootstyle="danger", command=terminate_process)
botao.grid(row=0, column=1, padx=290, pady=5)

# Variável para controlar o estado do checkbox
checkbox_var = ttk.BooleanVar()


def controlar_little_py():
    # Controla a execução do little.py baseado no estado do checkbox
    global processo_little

    try:
        if checkbox_var.get():  # Se checkbox está marcado
            # Verificar se o processo já não está rodando
            if processo_little is None or processo_little.poll() is not None:
                arquivo = r"C:\Users\minec\OneDrive\Área de Trabalho\Painel de monitoramento de Processos do Sistema\src\little_info.py"

                if os.path.exists(arquivo):
                    processo_little = subprocess.Popen(
                        [sys.executable, arquivo])

                else:
                    print(f"Arquivo não encontrado: {arquivo}")
                    # Desmarcar o checkbox se o arquivo não existir
                    checkbox_var.set(False)

        else:  # Se checkbox está desmarcado
            # Fechar o processo se estiver rodando
            if processo_little is not None and processo_little.poll() is None:
                try:
                    # Método 1: Terminar o processo diretamente
                    processo_little.terminate()

                    # Aguardar um pouco para o processo terminar
                    try:
                        processo_little.wait(timeout=3)

                    except subprocess.TimeoutExpired:
                        # Se não terminar em 3 segundos, forçar o encerramento
                        processo_little.kill()
                        print("Little.py encerrado forçadamente")

                    processo_little = None

                except Exception as e:
                    print(f"Erro ao terminar little.py: {e}")
                    # Método alternativo usando psutil (mais robusto)
                    try:
                        if processo_little.pid:
                            proc = psutil.Process(processo_little.pid)
                            proc.terminate()
                            proc.wait(timeout=3)
                            print("Little.py terminado usando psutil")
                            processo_little = None
                    except Exception as e2:
                        print(f"Erro com psutil também: {e2}")
            else:
                print("Little.py não estava rodando")

    except Exception as e:
        print(f"Erro geral no controle do little.py: {e}")
        # Em caso de erro, desmarcar o checkbox
        checkbox_var.set(False)


def fechar_aplicacao():
    # Função para fechar a aplicação e todos os processos filhos
    global processo_little

    # Fechar little.py se estiver rodando
    if processo_little is not None and processo_little.poll() is None:
        try:
            processo_little.terminate()
            processo_little.wait(timeout=2)
        except:
            try:
                processo_little.kill()
            except:
                pass

    root.destroy()


# Configurar o checkbox
checkbox = ttk.Checkbutton(top_frame,  variable=checkbox_var,
                           bootstyle="warning-round-toggle", command=controlar_little_py,)
checkbox.grid(row=0, column=2, )

# Configurar evento de fechamento da janela
root.protocol("WM_DELETE_WINDOW", fechar_aplicacao)


def update_system():
    # """Atualiza as informações do sistema na interface"""
    try:
        memory_info = get_memory_info()
        cpu_info = get_cpu_info()
        partition_info = get_partition_info()
        partition_used = get_partition_used()
        internet_info = get_internet_info()
        gpu_info = get_gpu_info()
        info_user = user()
        time_info = uptimes()

        process_list = process_info_with_pid()

        label.config(text=f" Memoria \n{memory_info}")
        label_2.config(text=cpu_info)
        label_3.config(text=partition_info)
        label_4.config(text=partition_used)
        label_5.config(text=f" Internet \n{internet_info}")
        label_6.config(text=f" CPU \n {gpu_info}")
        label_7.config(text=info_user)
        label_8.config(text=time_info)
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
