#include <Keyboard.h>
#include <Mouse.h>

void setup() {
  Serial1.begin(115200);
  Keyboard.begin();
  Mouse.begin();
}

void loop() {
  if (Serial1.available() >= 3) {
    char type = Serial1.read();
    
    // RESET BEFEHL
    if (type == 'R') {
      Serial1.read(); 
      Serial1.read();
      Keyboard.releaseAll();
      Mouse.release(MOUSE_LEFT);
      Mouse.release(MOUSE_RIGHT);
      Mouse.release(MOUSE_MIDDLE);
    }
    // TASTATUR
    else if (type == 'K') {
      byte key = Serial1.read();
      byte state = Serial1.read(); // 1 = Press, 0 = Release
      
      uint8_t targetKey = key;

      // Modifier-Zuordnungen
      if (key == 0x11) targetKey = KEY_LEFT_CTRL;
      else if (key == 0x12) targetKey = KEY_LEFT_ALT;
      else if (key == 0x10) targetKey = KEY_LEFT_SHIFT;
      else if (key == 0x5B) targetKey = KEY_LEFT_GUI;
      else if (key == 0x0D) targetKey = KEY_RETURN;
      else if (key == 0x08) targetKey = KEY_BACKSPACE;
      else if (key == 0x09) targetKey = KEY_TAB;
      else if (key == 0x1B) targetKey = KEY_ESC;
      else if (key == 0x25) targetKey = KEY_LEFT_ARROW;
      else if (key == 0x26) targetKey = KEY_UP_ARROW;
      else if (key == 0x27) targetKey = KEY_RIGHT_ARROW;
      else if (key == 0x28) targetKey = KEY_DOWN_ARROW;

      if (state == 1) {
        Keyboard.press(targetKey);
      } else {
        Keyboard.release(targetKey);
      }
    } 
    // MAUSBEWEGUNG
    else if (type == 'M') {
      int8_t dx = (int8_t)Serial1.read();
      int8_t dy = (int8_t)Serial1.read();
      Mouse.move(dx, dy);
    }
    // MAUSKLICKS
    else if (type == 'C') {
      byte button = Serial1.read();
      byte state = Serial1.read();
      
      char b = MOUSE_LEFT;
      if (button == 2) b = MOUSE_RIGHT;
      if (button == 3) b = MOUSE_MIDDLE;

      if (state == 1) Mouse.press(b);
      else Mouse.release(b);
    }
  }
}