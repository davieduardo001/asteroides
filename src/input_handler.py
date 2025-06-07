import threading
import queue

# Configuração de threading para entrada
input_queue = queue.Queue()
shared_input_state = {
    'rotate_left': False,
    'rotate_right': False,
    'thrust_on': False,
    'shoot_request': False
}
input_lock = threading.Lock()
stop_input_thread_event = threading.Event()

# Função da thread de processamento de entrada
def input_processing_thread_func():
    print("Thread de processamento de entrada iniciada.")
    while not stop_input_thread_event.is_set():
        try:
            command, key_state = input_queue.get(timeout=0.1) # Timeout para permitir a verificação de stop_event
            with input_lock:
                if command == 'rotate_left':
                    shared_input_state['rotate_left'] = key_state
                elif command == 'rotate_right':
                    shared_input_state['rotate_right'] = key_state
                elif command == 'thrust_on':
                    shared_input_state['thrust_on'] = key_state
                elif command == 'shoot_request': # Este é um evento, não um estado contínuo
                    if key_state: # True em KEYDOWN
                        shared_input_state['shoot_request'] = True 
                    # Não é necessário 'else', pois shoot_request é resetado por Player.update()
            input_queue.task_done()
        except queue.Empty:
            continue # Sem entrada, volta ao loop e verifica stop_event
        except Exception as e:
            print(f"Erro na thread de entrada: {e}") # Tratamento básico de erro
            break # Sai da thread em erro inesperado
    print("Thread de processamento de entrada parada.")
