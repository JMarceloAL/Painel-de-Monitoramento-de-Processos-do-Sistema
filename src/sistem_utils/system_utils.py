import psutil
from psutil import virtual_memory, cpu_percent, cpu_freq, disk_usage, disk_partitions, net_io_counters, process_iter
import pynvml
import subprocess
import platform
import GPUtil
import tkinter.messagebox as messagebox


# Variável global para armazenar informações da GPU
gpu_info_cache = None


def get_gpu_info():

    # Obtém informações da GPU (NVIDIA, AMD ou Intel) e retorna formatado para exibição

    global gpu_info_cache

    # Cache das informações básicas da GPU (modelo, fabricante)
    if gpu_info_cache is None:
        gpu_info_cache = detect_gpu_basic_info()

    # Obter informações dinâmicas (temperatura, utilização, etc.)
    dynamic_info = get_gpu_dynamic_info(gpu_info_cache['fabricante'])

    # Combinar informações básicas com dinâmicas
    gpu_info_cache.update(dynamic_info)

    return format_gpu_info(gpu_info_cache)


def detect_gpu_basic_info():
    """Detecta informações básicas da GPU (modelo e fabricante)"""
    info = {
        'fabricante': 'Desconhecido',
        'modelo': 'Não detectado',
        'memoria_total': 'N/A'
    }

    try:
        sistema = platform.system()

        if sistema == "Windows":
            info = detect_gpu_windows()
        elif sistema == "Linux":
            info = detect_gpu_linux()
        elif sistema == "Darwin":  # macOS
            info = detect_gpu_macos()

    except Exception as e:
        print(f"Erro ao detectar GPU: {e}")

    return info


def detect_gpu_windows():
    """Detecta GPU no Windows usando wmic"""
    info = {'fabricante': 'Desconhecido',
            'modelo': 'Não detectado', 'memoria_total': 'N/A'}

    try:
        cmd = 'wmic path win32_VideoController get Name,AdapterRAM /format:csv'
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 3:
                        adapter_ram = parts[1].strip()
                        name = parts[2].strip()

                        if name and name != 'Name' and name:
                            info['modelo'] = name[:30] + \
                                "..." if len(name) > 30 else name

                            # Determinar fabricante
                            name_lower = name.lower()
                            if any(x in name_lower for x in ['nvidia', 'geforce', 'quadro', 'rtx', 'gtx']):
                                info['fabricante'] = 'NVIDIA'
                            elif any(x in name_lower for x in ['amd', 'radeon', 'rx']):
                                info['fabricante'] = 'AMD'
                            elif 'intel' in name_lower:
                                info['fabricante'] = 'Intel'

                            # Memória
                            if adapter_ram and adapter_ram.isdigit():
                                memoria_gb = int(adapter_ram) / (1024**3)
                                info['memoria_total'] = f"{memoria_gb:.1f}GB"

                            break
    except Exception as e:
        print(f"Erro Windows GPU: {e}")

    return info


def detect_gpu_linux():
    """Detecta GPU no Linux usando lspci"""
    info = {'fabricante': 'Desconhecido',
            'modelo': 'Não detectado', 'memoria_total': 'N/A'}

    try:
        result = subprocess.run(
            ['lspci', '-nn'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if any(x in line for x in ['VGA compatible controller', '3D controller']):
                    gpu_name = line.split(
                        ': ', 1)[-1] if ': ' in line else line
                    info['modelo'] = gpu_name[:30] + \
                        "..." if len(gpu_name) > 30 else gpu_name

                    # Determinar fabricante
                    line_lower = line.lower()
                    if any(x in line_lower for x in ['nvidia', 'geforce']):
                        info['fabricante'] = 'NVIDIA'
                    elif any(x in line_lower for x in ['amd', 'radeon']):
                        info['fabricante'] = 'AMD'
                    elif 'intel' in line_lower:
                        info['fabricante'] = 'Intel'
                    break
    except Exception as e:
        print(f"Erro Linux GPU: {e}")

    return info


def detect_gpu_macos():
    """Detecta GPU no macOS usando system_profiler"""
    info = {'fabricante': 'Desconhecido',
            'modelo': 'Não detectado', 'memoria_total': 'N/A'}

    try:
        result = subprocess.run(['system_profiler', 'SPDisplaysDataType'],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line and not line.startswith(' '):
                    gpu_name = line.split(':')[0]
                    info['modelo'] = gpu_name[:30] + \
                        "..." if len(gpu_name) > 30 else gpu_name

                    # Determinar fabricante
                    gpu_lower = gpu_name.lower()
                    if any(x in gpu_lower for x in ['nvidia', 'geforce']):
                        info['fabricante'] = 'NVIDIA'
                    elif any(x in gpu_lower for x in ['amd', 'radeon']):
                        info['fabricante'] = 'AMD'
                    elif 'intel' in gpu_lower:
                        info['fabricante'] = 'Intel'
                    elif any(x in gpu_lower for x in ['apple', 'm1', 'm2', 'm3']):
                        info['fabricante'] = 'Apple'
                    break
    except Exception as e:
        print(f"Erro macOS GPU: {e}")

    return info


def get_gpu_dynamic_info(fabricante):
    """Obtém informações dinâmicas da GPU baseado no fabricante"""
    dynamic_info = {
        'temperatura': 'N/A',
        'utilizacao': 'N/A',
        'memoria_usada': 'N/A',
        'fan_speed': 'N/A'
    }

    try:
        if fabricante == 'NVIDIA':
            dynamic_info = get_nvidia_info()
        elif fabricante == 'AMD':
            dynamic_info = get_amd_info()
        elif fabricante == 'Intel':
            dynamic_info = get_intel_info()
    except Exception as e:
        print(f"Erro ao obter info dinâmica: {e}")

    return dynamic_info


def get_nvidia_info():
    """Obtém informações dinâmicas da GPU NVIDIA"""
    info = {'temperatura': 'N/A', 'utilizacao': 'N/A',
            'memoria_usada': 'N/A', 'fan_speed': 'N/A'}

    try:
        # Tentar usar pynvml primeiro
        try:
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)

            # Temperatura
            temp = pynvml.nvmlDeviceGetTemperature(
                handle, pynvml.NVML_TEMPERATURE_GPU)
            info['temperatura'] = f"{temp}°C"

            # Utilização
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            info['utilizacao'] = f"{util.gpu}%"

            # Memória
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            mem_used_gb = mem_info.used / (1024**3)
            info['memoria_usada'] = f"{mem_used_gb:.1f}GB"

            pynvml.nvmlShutdown()

        except:
            # Fallback para nvidia-smi
            result = subprocess.run([
                'nvidia-smi',
                '--query-gpu=temperature.gpu,utilization.gpu,memory.used',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                temp, util, mem = result.stdout.strip().split(', ')
                info['temperatura'] = f"{temp}°C"
                info['utilizacao'] = f"{util}%"
                info['memoria_usada'] = f"{int(mem)/1024:.1f}GB"

    except Exception as e:
        print(f"Erro NVIDIA: {e}")

    return info


def get_amd_info():
    """Obtém informações dinâmicas da GPU AMD"""
    info = {'temperatura': 'N/A', 'utilizacao': 'N/A',
            'memoria_usada': 'N/A', 'fan_speed': 'N/A'}

    try:
        # Tentar usar GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            info['temperatura'] = f"{gpu.temperature}°C" if gpu.temperature else 'N/A'
            info['utilizacao'] = f"{gpu.load*100:.0f}%" if gpu.load else 'N/A'
            info['memoria_usada'] = f"{gpu.memoryUsed/1024:.1f}GB" if gpu.memoryUsed else 'N/A'
    except:
        # AMD específico no Linux
        try:
            if platform.system() == "Linux":
                # Tentar ler sensores do sistema
                result = subprocess.run(
                    ['sensors'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'amdgpu' in line.lower() and '°C' in line:
                            temp = line.split('°C')[0].split()[-1]
                            if temp.replace('.', '').isdigit():
                                info['temperatura'] = f"{temp}°C"
                            break
        except Exception as e:
            print(f"Erro AMD: {e}")

    return info


def get_intel_info():
    """Obtém informações dinâmicas da GPU Intel"""
    info = {'temperatura': 'N/A', 'utilizacao': 'N/A',
            'memoria_usada': 'N/A', 'fan_speed': 'N/A'}

    try:
        # Intel geralmente compartilha memória com o sistema
        # Informações limitadas disponíveis
        if platform.system() == "Linux":
            result = subprocess.run(
                ['sensors'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if any(x in line.lower() for x in ['coretemp', 'intel']) and '°C' in line:
                        temp = line.split('°C')[0].split()[-1]
                        if temp.replace('.', '').isdigit():
                            info['temperatura'] = f"{temp}°C"
                        break
    except Exception as e:
        print(f"Erro Intel: {e}")

    return info


def format_gpu_info(gpu_info):
    """Formata as informações da GPU para exibição"""
    fabricante = gpu_info.get('fabricante', 'Desconhecido')
    modelo = gpu_info.get('modelo', 'Não detectado')
    temp = gpu_info.get('temperatura', 'N/A')
    util = gpu_info.get('utilizacao', 'N/A')
    mem_used = gpu_info.get('memoria_usada', 'N/A')
    mem_total = gpu_info.get('memoria_total', 'N/A')

    # Criar texto formatado baseado no fabricante
    if fabricante == 'NVIDIA':
        return f" GPU NVIDIA\n{modelo}\n {temp}\n {util}\n {mem_used}/{mem_total}"
    elif fabricante == 'AMD':
        return f" GPU AMD\n{modelo}\n {temp}\n {util}\n {mem_used}"
    elif fabricante == 'Intel':
        return f" GPU Intel\n{modelo}\n {temp}\n Integrada"
    elif fabricante == 'Apple':
        return f" GPU Apple\n{modelo}\n {temp}\n Unificada"
    else:
        return f" GPU\n{modelo}\n {temp}\n⚡ {util}"


def get_network_speed(value):
    # Obtém velocidade da rede em KB
    bytes_sent = value.bytes_sent
    bytes_recv = value.bytes_recv
    return f"S: {bytes_sent / 1024 / 1024:.1f}KB R:{bytes_recv / 1024 / 1024:.1f}KB"


def bytes_to_gigas(value):
    """Converte bytes para GB"""
    return f'{value / 1024 / 1024 / 1024:.1f} GB'


def showdisk(value):
    # Mostra os discos disponíveis
    discos = []
    for partitio in value:
        convert = partitio.device
        discos.append(convert)
        string = ''.join(map(str, discos))
    return string


def get_disk_used_space(value):
    # Obtém espaço usado nos discos
    partitions = disk_partitions()
    result = []

    for partition in partitions:
        try:
            usage = value(partition.mountpoint)
            used_gb = usage.used / (1024**3)
            total_gb = usage.total / (1024**3)
            percent = usage.percent
            result.append(
                f"\n   {partition.device}: {total_gb:.1f}GB / {used_gb:.1f}GB\n   {percent}% \n")
        except:
            result.append(f"{partition.device}: 0GB")

    return " ".join(result)


def get_memory_info():
    # Obtém informações de memória
    memoria = virtual_memory()
    return f" Memoria \n {(bytes_to_gigas(memoria.used))} / {(bytes_to_gigas(memoria.total))} / {memoria.percent}% "


def get_cpu_info():
    # Obtém informações da CPU
    cpu_use = cpu_percent(interval=0.1)
    cpu_frq = cpu_freq()
    return f" CPU \n{cpu_use} % / {cpu_frq.current}Ghz"


def get_partition_info():
    # Obtém informações das partições"""
    diskpartitions = disk_partitions()
    return f" Discos \n   {showdisk(diskpartitions)} "


def get_partition_used():
    # Obtém espaço usado nas partições
    disks_used = disk_usage
    return f"    {get_disk_used_space(disks_used)}"


def get_internet_info():
    # Obtém informações da internet
    Internet = net_io_counters()
    return f"  Internet \n   {get_network_speed(Internet)}"


def process_info_with_pid():
    # Versão modificada da process_info que inclui o PID
    processos = []
    blacklist = {
        'System Idle Process', 'System', 'Registry', 'smss.exe', 'csrss.exe',
        'wininit.exe', 'services.exe', 'lsass.exe', 'svchost.exe',
        'fontdrvhost.exe', 'dwm.exe'
    }

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            nome = proc.info['name']
            pid = proc.info['pid']

            if not nome or nome in blacklist or pid <= 4:
                continue

            cpu = proc.cpu_percent(interval=None)
            memoria = proc.memory_percent()

            processos.append({
                'nome': nome,
                'cpu': f"{cpu:.2f}%",
                'memoria': f"{memoria:.2f}%",
                'pid': pid
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return processos


def colum_cpu():
    # Obtém informações da CPU
    cpu_use = cpu_percent(interval=0.1)

    return f"{cpu_use} %"


def colum_memory():
    # Obtém informações de memória
    memoria = virtual_memory()
    return f"{memoria.percent} %"


selected_process = None


def on_item_select(event, listbox):
    # Função chamada quando um item é selecionado na listbox
    global selected_process
    selection = listbox.selection()
    if selection:
        item = listbox.item(selection[0])
        values = item['values']
        if values:
            selected_process = {
                'nome': values[0],
                'cpu': values[1],
                'memoria': values[2],
                'pid': values[3]
            }


def terminate_process():
    # Função para finalizar o processo selecionado
    global selected_process

    if not selected_process:
        messagebox.showwarning("Aviso", "Nenhum processo selecionado!")
        return

    try:
        pid = int(selected_process['pid'])
        process_name = selected_process['nome']

        # Confirmar antes de finalizar
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Deseja realmente finalizar o processo?\n\n"
            f"Nome: {process_name}\n"
            f"PID: {pid}"
        )

        if resposta:
            # Tentar finalizar o processo
            process = psutil.Process(pid)
            process.terminate()

            # Aguardar um pouco para o processo terminar graciosamente
            try:
                process.wait(timeout=3)
                messagebox.showinfo(
                    "Sucesso", f"Processo '{process_name}' finalizado com sucesso!")
            except psutil.TimeoutExpired:
                # Se não terminou graciosamente, forçar encerramento
                process.kill()
                messagebox.showinfo(
                    "Sucesso", f"Processo '{process_name}' foi forçado a encerrar!")

            # Limpar seleção
            selected_process = None

    except psutil.NoSuchProcess:
        messagebox.showerror("Erro", "O processo não existe mais!")
        selected_process = None
    except psutil.AccessDenied:
        messagebox.showerror(
            "Erro", "Acesso negado! Execute como administrador para finalizar este processo.")
    except ValueError:
        messagebox.showerror("Erro", "PID inválido!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao finalizar processo: {str(e)}")
