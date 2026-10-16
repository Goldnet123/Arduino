import serial
import time
import ctypes
from pynput import keyboard, mouse

COM_PORT = 'COM9'  # <-- Deinen COM-Port eintragen
BAUD_RATE = 115200

user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)
CENTER_X = screen_w // 2
CENTER_Y = screen_h // 2

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"[+] Erfolgreich verbunden mit {COM_PORT}")
except Exception as e:
    print(f"[-] Fehler: {e}")
    exit()

is_active = False

def send_reset():
    try:
        ser.write(bytes([ord('R'), 0, 0]))
    except Exception:
        pass

def toggle_active(key):
    global is_active
    if key == keyboard.Key.home:
        is_active = not is_active
        send_reset()
        
        if is_active:
            user32.SetCursorPos(CENTER_X, CENTER_Y)
            print("\n[Modus] >>> AKTIV <<<")
        else:
            print("\n[Modus] --- INAKTIV ---")
        update_listeners()

def get_key_code(key):
    # 1. Modifiers & Spezielle Tasten
    if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        return 0x11
    elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
        return 0x12
    elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
        return 0x10
    elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
        return 0x5B
    elif key == keyboard.Key.enter:
        return 0x0D
    elif key == keyboard.Key.backspace:
        return 0x08
    elif key == keyboard.Key.tab:
        return 0x09
    elif key == keyboard.Key.esc:
        return 0x1B
    elif key == keyboard.Key.space:
        return ord(' ')
    elif key == keyboard.Key.left:
        return 0x25
    elif key == keyboard.Key.up:
        return 0x26
    elif key == keyboard.Key.right:
        return 0x27
    elif key == keyboard.Key.down:
        return 0x28

    # 2. Virtual Keys für A-Z (VK 65 bis 90)
    # VK_T ist 84 -> Wandelt es GARANTIERT in 't' (ASCII 116) um!
    vk = getattr(key, 'vk', None)
    if vk is not None and 65 <= vk <= 90:
        return ord(chr(vk).lower())

    # 3. Restliche Zeichen abfangen (Zahlen, Satzzeichen)
    if hasattr(key, 'char') and key.char is not None:
        val = ord(key.char)
        # Wenn pynput wegen Ctrl/Alt ein Steuerzeichen (<32) schickt, ignorieren!
        if val >= 32:
            return ord(key.char.lower())

    return None

def on_press(key):
    if key == keyboard.Key.home:
        toggle_active(key)
        return
    
    if is_active:
        k = get_key_code(key)
        if k is not None:
            try:
                ser.write(bytes([ord('K'), k & 0xFF, 1]))
            except Exception:
                pass

def on_release(key):
    if key == keyboard.Key.home:
        return
        
    if is_active:
        k = get_key_code(key)
        if k is not None:
            try:
                ser.write(bytes([ord('K'), k & 0xFF, 0]))
            except Exception:
                pass

def on_move(x, y):
    if not is_active:
        return

    dx = x - CENTER_X
    dy = y - CENTER_Y

    if dx != 0 or dy != 0:
        clamped_dx = max(-127, min(127, int(dx)))
        clamped_dy = max(-127, min(127, int(dy)))

        try:
            ser.write(bytes([ord('M'), clamped_dx & 0xFF, clamped_dy & 0xFF]))
        except Exception:
            pass

        user32.SetCursorPos(CENTER_X, CENTER_Y)

def on_click(x, y, button, pressed):
    if not is_active:
        return
    btn_code = 1 if button == mouse.Button.left else (2 if button == mouse.Button.right else 3)
    state = 1 if pressed else 0
    try:
        ser.write(bytes([ord('C'), btn_code, state]))
    except Exception:
        pass

kb_listener = None
m_listener = None

def update_listeners():
    global kb_listener, m_listener
    if kb_listener is not None:
        kb_listener.stop()
    if m_listener is not None:
        m_listener.stop()

    kb_listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=is_active)
    m_listener = mouse.Listener(on_move=on_move, on_click=on_click, suppress=is_active)
    
    kb_listener.start()
    m_listener.start()

send_reset()
update_listeners()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    send_reset()
    print("\nBeendet.")