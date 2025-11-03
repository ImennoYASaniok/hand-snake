import pygame
from collections import deque

class Game:
    def __init__(self):
        # ------ Надписи и данные о игре, находящиеся сверху слева
        self.labels = {}
        self.init_labels()
        # ------ Кнопки на экране
        self.buttons = []
        self.init_button_menu()

    def init_labels(self):
        self.labels = {}

        label_fps = {
            "coords": (5, 0),
            "text": f"fps: {self.parent.clock.get_fps():2.0f} / {self.parent.FPS}",
            "font": pygame.font.Font(self.base_style["font_path"], 30)
        }
        label_fps["label"] = self.parent.label_text(coords=label_fps["coords"],
                                                    text=label_fps["text"],
                                                    font=label_fps["font"],
                                                    color=self.base_style["colors"]["light"])
        self.labels["fps"] = label_fps


    def set_label(self, key, text):
        self.labels[key]["text"] = text
        self.labels[key]["label"] = self.parent.label_text(coords=self.labels[key]["coords"],
                                                    text=self.labels[key]["text"],
                                                    font=self.labels[key]["font"],
                                                    color=self.base_style["colors"]["light"])

    def init_button_menu(self):
        w, h = 80, 50
        button_ToMenu = {
            "font": pygame.font.Font(self.base_style["font_path"], 30),
            "coords": (self.parent.display_w-w, 0, w, h),
            "text": "...",
            "color": {
                "inactive": self.base_style["colors"]["base2"],
                "hover": self.base_style["colors"]["base1"],
                "pressed": self.base_style["colors"]["light"],
                "text": self.base_style["colors"]["light"]
            },
            "func": lambda: self.parent.display_change('menu')
        }
        button_ToMenu["button"] = self.parent.button(coords=button_ToMenu["coords"],
                                                              text=button_ToMenu["text"],
                                                              color=button_ToMenu["color"],
                                                              font=button_ToMenu["font"],
                                                              func=button_ToMenu["func"])
        self.buttons.append(button_ToMenu)

    def set_sound(self, sound):
        if self.curr_sound != sound:
            if sound is None:
                pygame.mixer.music.pause()
                # self.flag_sound = 1
            else: # elif self.flag_sound:
                pygame.mixer.music.load(self.sounds[sound])
                pygame.mixer.music.play(-1)
                pygame.mixer.music.unpause()
                # self.flag_sound = 0
        self.curr_sound = sound

    def set_sound_player(self, type_player):
        if type_player == "pause": pygame.mixer.music.pause()
        elif type_player == "play": pygame.mixer.music.unpause()

    def room_change(self, type_room):
        self.type_room = type_room
        self.flag_change_room = 1

    def change_game(self, name_game):
        delta_energy = 3
        if not self.flag_mini_games:
            if self.character.character["energy"][0] - delta_energy < 0:
                self.set_message(f"Не хватает энергии чтобы поиграть в игры, нужно ещё {delta_energy + 1} ")
            else:
                self.flag_mini_games = True
                pygame.mixer.music.pause()
                out_many = self.mini_games[self.type_room][name_game]()
                pygame.mixer.music.unpause()
                self.character.character["money"][0] += out_many
                self.set_label("money", f"монеты: {self.character.character['money'][0]}")
                self.character.character["energy"][0] -= delta_energy
                for obj in self.room_now.objects.values():
                    obj.data["func"] = 0
                self.flag_mini_games = False

    def draw(self):
        # ------ Иницилизация карты, пола
        self.parent.display.fill(self.base_style["colors"]["black"])
        self.parent.display.blit(self.game_layer, (self.coords_game_layer[0], self.coords_game_layer[1]))
        self.game_layer.fill((0, 0, 0))
        self.game_layer.blit(self.room_now.floor, (0, 0))

        # ------ Перемещение карты (динамическая камеры)
        # self.set_dinamic_zone(type_output=1)
        if self.type_dinamic == 0:
            if self.character.character["coords_display"][1] < self.coords_dinamic_zone[1]:
                self.flags_dinamic["up"] = 1
                self.flags_dinamic["down"] = 0
                self.flags_dinamic["left"] = 0
                self.flags_dinamic["right"] = 0
            else: self.flags_dinamic["up"] = 0
            if self.character.character["coords_display"][1] > self.coords_dinamic_zone[3]:
                self.flags_dinamic["up"] = 0
                self.flags_dinamic["down"] = 1
                self.flags_dinamic["left"] = 0
                self.flags_dinamic["right"] = 0
            else: self.flags_dinamic["down"] = 0
            if self.character.character["coords_display"][0] < self.coords_dinamic_zone[0]:
                self.flags_dinamic["up"] = 0
                self.flags_dinamic["down"] = 0
                self.flags_dinamic["left"] = 1
                self.flags_dinamic["right"] = 0
            else: self.flags_dinamic["left"] = 0
            if self.character.character["coords_display"][0] > self.coords_dinamic_zone[2]:
                self.flags_dinamic["up"] = 0
                self.flags_dinamic["down"] = 0
                self.flags_dinamic["left"] = 0
                self.flags_dinamic["right"] = 1
            else: self.flags_dinamic["right"] = 0
        elif self.type_dinamic == 1:
            self.flags_dinamic["up"] = 1
            self.flags_dinamic["down"] = 1
            self.flags_dinamic["left"] = 1
            self.flags_dinamic["right"] = 1

        # ------ Отрисовка всех объектов
        if self.flag_change_room:
            self.flag_change_room = 0
            for name, obj in self.room_now.objects.items():
                if name in self.delete_enemys:
                    if "enemy" in name and self.delete_enemys[name] == False:
                        self.coords_enemy[name] = [obj.data["coords"][0], obj.data["coords"][1]]
                        self.hp_enemys[name] = obj.data["hp"]
                # if "enemy" in name and name not in self.coords_enemy.keys():
                #     self.coords_enemy[name] = [obj.data["coords"][0], obj.data["coords"][1]]
            self.room_now.delete_all()
            self.room_now = self.list_rooms[self.type_room](self.parent, self, self.base_style)
            self.room_now.enter_rooms()
            self.init_map()
            # print()
            # print("enemys", list(filter(lambda x: "enemy" in x, self.room_now.objects.keys())))
            # print("coords_enemys", list(self.coords_enemy.keys()))
            # print("delete_enemys", list(self.delete_enemys.keys()))
        # print(self.coords_game_layer[0] - self.coords_game_layer_old[0], self.coords_game_layer[1] - self.coords_game_layer_old[1])
        self.room_now.draw()

        # ------ Пули
        delete_bullet = []
        for name, bullet in dict(list(filter(lambda x: "bullet" in x[0], self.room_now.objects.items()))).items():
            bullet.update()
            if bullet.bullet_data["delete"] == 1: delete_bullet.append(bullet.bullet_data["name"])
        # print(list(dict(list(filter(lambda x: "bullet" in x[0], self.room_now.objects.items()))).keys()))
        for _ in range(len(delete_bullet)):
            if delete_bullet[0] in self.room_now.objects.keys():
                del self.room_now.objects[delete_bullet[0]]

        # ------ Вывод значений и данных о игре
        # if self.flag_message_energy == 1: self.set_message()
        for i in self.labels.values():
            if "label" in i.keys():
                self.parent.display.blit(i["label"], i["coords"])
        self.set_label("fps", f"fps: {self.parent.clock.get_fps():2.0f} / {self.parent.FPS}")
        self.set_label("hp", f"hp: {self.character.character['hp'][0]} / {self.character.character['hp'][2]}")
        if self.parent.settings_var["character_energy"] == 1:
            self.set_label("energy", f"энергия: {self.character.character['energy'][0]} / {self.character.character['energy'][2]}")

        # ------ Карта
        if self.parent.settings_var["draw_map"] == 1: self.map.draw()

        # ------ Условия выхода
        if self.character.character["hp"][0] <= 0:
            self.parent.display_change("final", dop_type="fail")

        # ------ Вывод данных в консоль
        # print("MOUSE", pygame.mouse.get_pos())
        # print(pygame.mouse._get_cursor()) # pygame.mouse.get_pos()

        # self.coords_game_layer_old = self.coords_game_layer.copy()

    def set_rect(self, layer, coords, color_base, thickness_border=None, color_border=None):
        if thickness_border == None: thickness_border = 5
        if len(coords) < 4: raise IndexError("Мало параметров coords, как минимум 4 (x, y, w, h)")
        if len(color_base) < 3: raise IndexError("Мало параметров RGB цвета color, как минимум 3")
        rect_layer = pygame.Surface((coords[2], coords[3]))
        if color_border != None:
            pygame.draw.lines(self.game_layer, color_border, True, [[coords[0], coords[1]],
                                                               [coords[0]+coords[2], coords[1]],
                                                               [coords[0]+coords[2], coords[1]+coords[3]],
                                                               [coords[0], coords[1]+coords[3]]], thickness_border)
        if len(color_base) >= 4: rect_layer.set_alpha(color_base[3])
        rect_layer.fill(color_base[:3])
        layer.blit(rect_layer, (coords[0], coords[1]))

    def set_dinamic_zone(self, type_output=0):
        if type_output == 1:
            output_flags = list(self.flags_dinamic.values())
        elif type_output == 2:
            if list(self.flags_dinamic.values())[0] == 0: # up
                pass
        self.set_rect(layer=self.parent.display,
                      coords=(self.start_coords_dinamic_zone[0],
                              self.start_coords_dinamic_zone[1],
                              self.start_coords_dinamic_zone[2] - self.start_coords_dinamic_zone[0],
                              self.start_coords_dinamic_zone[3] - self.start_coords_dinamic_zone[1]),
                      color_base=(50, 50, 50, 100))

    def set_message(self, text, delay=2500):
        label = {
            "coords": (100, 100),
            "text": text,
            "font": pygame.font.Font(self.base_style["font_path"], 40)  # self.base_style["dop_font"]
        }
        label["label"] = self.parent.label_text(coords=label["coords"],
                                                text=label["text"],
                                                font=label["font"],
                                                color=self.base_style["colors"]["light"], type_blit=False)
        label["label"], label["coords"] = self.parent.align(label["label"], label["coords"],
                                            inacurr=-20, type_blit=False, type_align="center")
        bortic = 20
        coords_rect = (label["coords"][0]-bortic,
                       label["coords"][1]-bortic,
                       label["label"].get_width()+bortic,
                       label["label"].get_height()+bortic)
        pygame.draw.rect(self.parent.display, self.base_style["colors"]["base2"], coords_rect) # self.game_layer
        self.parent.display.blit(label["label"], label["coords"]) # self.game_layer
        pygame.display.flip()
        pygame.time.wait(delay)

    def hp_character_up(self, price, val, type_val):
        if self.character.character["money"][0] - price < 0:
            self.set_message(f"Не хватает денег, для {val} {type_val} нужно {price} монет ")
        elif self.character.character[type_val][0] + val > self.character.character[type_val][2]:
            self.set_message(f"Всё {type_val} восстановлено (макс. {self.character.character[type_val][2]} {type_val}) ")
        else:
            self.character.character["money"][0] -= price
            self.character.character[type_val][0] += val
            self.set_label("money", f"монеты: {self.character.character['money'][0]}")

    def render_objects(self, draw_rects=False): # dop_buttons=None,
        objects = self.room_now.objects #list(self.room_now.objects.values())
        dop_objects_down = list(self.room_now.dop_objects_down.values())
        dop_objects_up = list(self.room_now.dop_objects_up.values())

        delete_obj = []
        for name, obj in objects.items():
            if name == "DINAMIC_door_1":
                if False not in self.delete_enemys.values() or self.delete_enemys == {}:
                    delete_obj.append(name)
        for _ in range(len(delete_obj)):
            del self.room_now.objects[delete_obj[0]]

        # Распределение по слоям
        for obj in objects.values():
            if self.character.character["rect"].centery > obj.data["rect"].centery:
                obj.data["type_render"] = 1
            else:
                obj.data["type_render"] = 2

        # Отрисовка
        if dop_objects_up is not None:
            for obj in dop_objects_up: # sorted(dop_objects_up, key=lambda obj: (obj.data["rect"].y, obj.data["rect"].h)):
                obj.draw()
        for name, obj in sorted(list(filter(lambda name_obj: name_obj[1].data["type_render"] == 1, objects.items())), key=lambda name_obj: name_obj[1].data["rect"].y + name_obj[1].data["rect"].h):
            obj.draw()
        self.character.update(draw_rects)
        for name, obj in sorted(list(filter(lambda name_obj: name_obj[1].data["type_render"] == 2, objects.items())), key=lambda name_obj: name_obj[1].data["rect"].y + name_obj[1].data["rect"].h):
            obj.draw()
        if dop_objects_down is not None:
            for obj in dop_objects_down: # sorted(dop_objects_down, key=lambda obj: (obj.data["rect"].y, obj.data["rect"].h)):
                obj.draw()
        if draw_rects:
            for obj in objects:
                pygame.draw.rect(self.game_layer, (255, 255, 255), obj.data["rect"])

    def collide(self, base_object, objects, draw_rects, type_collide="rect", type_return="dirs"):
        if type(objects) == dict:
            names_objects = list(objects.keys())
            objects = list(objects.values())
        dir_collides = []
        if type_return == "objcts": collide_objcts = {}

        if type_collide == "rect":
            base_rect = base_object["rect"]
        elif type_collide == "sprite":
            base_rect = base_object["sprite"].get_rect()
            base_rect.x = base_object["coords"][0]
            base_rect.y = base_object["coords"][1]
        else:
            base_rect = base_object["rect"]
        if draw_rects: pygame.draw.rect(self.game_layer, (255, 0, 0), base_rect)

        i = 0
        for obj in objects:
            try:
                if type_collide == "sprite":
                    if "sprite" in obj.data:
                        obj_rect = obj.data["sprite"].get_rect()
                        obj_rect.x = obj.data["coords"][0]
                        obj_rect.y = obj.data["coords"][1]

                    else:
                        obj_rect = obj.data["rect"]
                else:
                    obj_rect = obj.data["rect"]
            except AttributeError:
                if type_collide == "sprite":
                    obj_rect = obj.character["sprite"].get_rect()
                else:
                    obj_rect = obj.character["rect"]

            if base_rect.colliderect(obj_rect):
                collision_area = base_rect.clip(obj_rect)
                if type_return == "objcts": collide_objcts[names_objects[i]] = obj
                if collision_area.width > collision_area.height:
                    if base_rect.centery < obj_rect.centery:
                        dir_collides.append("down")
                    else:
                        dir_collides.append("up")
                else:
                    if base_rect.centerx < obj_rect.centerx:
                        dir_collides.append("right")
                    else:
                        dir_collides.append("left")
            i += 1

        if dir_collides == []: dir_collides = [None]
        dir_collides = list(set(dir_collides))
        if type_return == "dirs":
            return dir_collides
        elif type_return == "objcts":
            return collide_objcts

    def animate_sprite(self, for_data, reverse=False):
        for_data[0] += for_data[1]
        # print(for_data[2])
        if for_data[0] > for_data[2] or for_data[0] < 0:
            if reverse:
                for_data[1] = -for_data[1]
                for_data[0] += for_data[1]
            else:
                for_data[0] = 0
        return for_data

    # ==== BFS
    def bfs(self, start, goal, graph):
        queue = deque([start])
        visited = {start: None} # {}
        # for start in starts:
        #     visited[start] = None
        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break
            next_nodes = graph[cur_node]
            for next_node in next_nodes:
                if next_node not in visited:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return queue, visited
    # ========

    def mouse_state(self, state):
        self.val_mouse_state = state

    def check_event(self, event):
        for commands in self.list_comands:
            if event.type in commands.keys():
                if type(commands[event.type]) == dict:
                    if event.key in commands[event.type].keys():
                        commands[event.type][event.key]()
                else:
                    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                        commands[event.type](event.type)
                    else:
                        commands[event.type]()

    def delete_all(self):
        # print("GAME ", *list(map(lambda x: x["text"] if "text" in x.keys() else x["texts"], self.buttons)), sep=" ")
        for j in range(len(self.buttons)): del self.buttons[0]
        # self.parent.type_music = 1
        self.parent.set_music()