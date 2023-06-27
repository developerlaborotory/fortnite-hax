import pymem
import pymem.process
import keyboard
import time
import cv2
import numpy as np
import threading
import tkinter as tk
 
class FortniteCheat:
    aimbot_enabled = False
    esp_enabled = False
    spinbot_enabled = False
    smoothing_factor = 0
 
    def __init__(self):
        while True:
            try:
                self.pm = pymem.Pymem("FortniteClient-Win64-Shipping.exe")
                self.module_base = pymem.process.module_from_name(self.pm.process_handle, "FortniteClient-Win64-Shipping.exe").lpBaseOfDll
                self.local_player = self.module_base + 0x3C6C3B0
                self.entity_list = self.module_base + 0x4CDDA98
                break
            except:
                time.sleep(1)
 
    def aimbot(self):
        while self.aimbot_enabled:
            player_position = self.pm.read_float(self.local_player + 0x70)
            entity_count = self.pm.read_int(self.module_base + 0x4D3B22C)
 
            for i in range(entity_count):
                entity = self.pm.read_int(self.entity_list + i * 0x8)
 
                if entity:
                    entity_position = self.pm.read_float(entity + 0x70)
 
                    if entity_position:
                        dx = player_position - entity_position
 
                        if dx > 0:
                            self.pm.write_float(entity + 0x70, entity_position - 0.1)
                        elif dx < 0:
                            self.pm.write_float(entity + 0x70, entity_position + 0.1)
 
                        if self.spinbot_enabled:
                            self.pm.write_float(self.local_player + 0x7C, dx / (self.smoothing_factor + 1))
 
            time.sleep(0.001)
 
    def esp(self):
        while self.esp_enabled:
            player_position = self.pm.read_float(self.local_player + 0x70)
            entity_count = self.pm.read_int(self.module_base + 0x4D3B22C)
 
            # Create empty image
            image = np.zeros((1080, 1920, 3), dtype=np.uint8)
 
            for i in range(entity_count):
                entity = self.pm.read_int(self.entity_list + i * 0x8)
 
                if entity:
                    entity_position = self.pm.read_float(entity + 0x70)
 
                    if entity_position:
                        entity_distance = int(np.sqrt((player_position - entity_position) ** 2))
 
                        if entity_distance < 300:
                            entity_screen_position = self.world_to_screen(entity_position)
                            cv2.circle(image, entity_screen_position, 5, (0, 255, 0), -1)
 
            cv2.imshow('ESP', image)
            cv2.waitKey(1)
 
    def world_to_screen(self, position):
        view_matrix = self.pm.read_bytes(self.module_base + 0x501AE60, 64)
        view_matrix = np.frombuffer(view_matrix, dtype=np.float32).reshape((4, 4))
 
        w = view_matrix[3][0] * position.x + view_matrix[3][1] * position.y + view_matrix[3][2] * position.z + view_matrix[3][3]
 
        if w < 0.1:
            return (0, 0)
 
        x = view_matrix[0][0] * position.x + view_matrix[0][1] * position.y + view_matrix[0][2] * position.z + view_matrix[0][3]
        y = view_matrix[1][0] * position.x + view_matrix[1][1] * position.y + view_matrix[1][2] * position.z + view_matrix[1][3]
 
        return (int(1920 / 2 * (1 + x / w)), int(1080 / 2 * (1 - y / w)))
 
    def start(self):
        aimbot_thread = threading.Thread(target=self.aimbot)
        esp_thread = threading.Thread(target=self.esp)
 
        aimbot_thread.start()
        esp_thread.start()
 
        root = tk.Tk()
        root.geometry('150x150')
 
        aimbot_button = tk.Button(root, text='Aimbot', command=self.toggle_aimbot)
        aimbot_button.pack()
 
        esp_button = tk.Button(root, text='ESP', command=self.toggle_esp)
        esp_button.pack()
 
        spinbot_button = tk.Button(root, text='Spinbot', command=self.toggle_spinbot)
        spinbot_button.pack()
 
        smoothing_label = tk.Label(root, text='Smoothing Factor:')
        smoothing_label.pack()
 
        smoothing_scale = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, command=self.set_smoothing_factor)
        smoothing_scale.pack()
 
        root.mainloop()
 
    def toggle_aimbot(self):
        self.aimbot_enabled = not self.aimbot_enabled
 
    def toggle_esp(self):
        self.esp_enabled = not self.esp_enabled
 
    def toggle_spinbot(self):
        self.spinbot_enabled = not self.spinbot_enabled
 
    def set_smoothing_factor(self, value):
        self.smoothing_factor = int(value)
 
if __name__ == '__main__':
    cheat = FortniteCheat()
    cheat.start()
