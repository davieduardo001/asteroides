import threading
import queue

# Threading setup for input
input_queue = queue.Queue()
shared_input_state = {
    'rotate_left': False,
    'rotate_right': False,
    'thrust_on': False,
    'shoot_request': False
}
input_lock = threading.Lock()
stop_input_thread_event = threading.Event()

# Input Processing Thread Function
def input_processing_thread_func():
    print("Input processing thread started.")
    while not stop_input_thread_event.is_set():
        try:
            command, key_state = input_queue.get(timeout=0.1) # Timeout to allow checking stop_event
            with input_lock:
                if command == 'rotate_left':
                    shared_input_state['rotate_left'] = key_state
                elif command == 'rotate_right':
                    shared_input_state['rotate_right'] = key_state
                elif command == 'thrust_on':
                    shared_input_state['thrust_on'] = key_state
                elif command == 'shoot_request': # This is an event, not a continuous state
                    if key_state: # True on KEYDOWN
                        shared_input_state['shoot_request'] = True 
                    # No 'else' needed as shoot_request is reset by Player.update()
            input_queue.task_done()
        except queue.Empty:
            continue # No input, loop back and check stop_event
        except Exception as e:
            print(f"Error in input thread: {e}") # Basic error handling
            break # Exit thread on unexpected error
    print("Input processing thread stopped.")
