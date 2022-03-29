# -*- coding: UTF-8 -*-
from tkinter.font import Font

from screeninfo import get_monitors
from tkinter import *
import pyglet
from PIL import Image, ImageTk


def rgb_to_hex(rgb: tuple):
    print('#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2]))

class Overlay:

    def __init__(self, magicka_enabled: bool, fatigue_enabled: bool):

        # Base screen dimensions for resize computation purposes
        base_width = 1920
        base_height = 1080

        # Get screen dimensions
        primary_monitor = [monitor for monitor in get_monitors() if monitor.is_primary][0]
        self._primary_width = primary_monitor.width
        self._primary_height = primary_monitor.height

        # Get screens ratio
        width_ratio = self._primary_width / base_width
        height_ratio = self._primary_height / base_height

        # Initate root window
        self.root = Tk()

        '''Set window parameters'''

        # Set window dimensions
        self.root.geometry(str(self._primary_width) + 'x' + str(self._primary_height))

        # Any purple color in the window becomes transparent
        # Window stays on top and the title bar is not visible
        self.root.overrideredirect(True)
        self.root.lift()
        self.root.wm_attributes('-topmost', True)
        self.root.wm_attributes('-transparent', 'purple')
        self.root.configure(background='purple')

        # Add custom font that Morrowind is using
        pyglet.font.add_file('MagicCardsNormal.ttf')

        # Calculate font size from height ratio
        base_font_size = 12
        self._font_size = int(base_font_size * height_ratio)

        # Define fonts
        # Font color from Morrowind.ini
        self._font_color = '#caa560'
        self._level_font = Font(family='Magic Cards', size=self._font_size, weight='bold')
        self._name_font = Font(family='Magic Cards', size=self._font_size)

        # Additional stats bar settings
        self._magicka_enabled = magicka_enabled
        self._fatigue_enabled = fatigue_enabled

        # How many characters of player name will get displayed on screen
        self._name_limit = 17

        # Limit amount of frames on display
        self._frames_limit = 8

        # Track how many frames there are
        self._frames_count = 0

        # Store created frames here
        self._frames = list()

        # Load up frame image and resize it according to the primary screen dimensions
        base_frame_image = (Image.open('openmw_frame.png'))
        base_frame_image_width = base_frame_image.size[0]
        base_frame_image_height = base_frame_image.size[1]

        resized_frame_image = base_frame_image.resize(
            (int(width_ratio * base_frame_image_width), int(height_ratio * base_frame_image_height)), Image.ANTIALIAS)
        self._frame_image = ImageTk.PhotoImage(resized_frame_image)

        # Define label properties
        self._label_height = int(self._font_size * 2)
        self._label_width = int(40 * width_ratio)

        # Offset between tops of two frames (bottom of frame 1's label and top of frame 2's label)
        # Defined as height of the whole frame + padding represented by double the font size
        self._frame_y_offset = self._label_height + self._frame_image.height() + 2 * self._font_size

        # Add height of magicka and fatigue bars if enabled
        if self._magicka_enabled:
            self._frame_y_offset += self._frame_image.height()
        if self._fatigue_enabled:
            self._frame_y_offset += self._frame_image.height()

        # Health bar gradient is achieved drawing single lines of different shades of red, similarly to magicka and fatigue
        self.health_bar_gradient = ['#d6a684', '#d9ad8f', '#debaa5', '#dbb39a', '#d69a7b', '#cb8265', '#c0694f',
                                    '#b55139',
                                    '#b54d39', '#a43f34', '#a43f34', '#9c3831', '#97352c']

        self.magicka_bar_gradient = ['#94aece', '#9cb3d3', '#adbede', '#a5b9d9', '#8ca6ce', '#769ac3', '#608eb8',
                                     '#4a82ad',
                                     '#4782a5', '#457d9c', '#427994', '#397584', '#3c7487']

        self.fatigue_bar_gradient = ['#9cd384', '#a4d78f', '#b5dfa5', '#addb9a', '#9ccf7b', '#8cc565', '#7bbc4f',
                                     '#6bb239',
                                     '#6baa39', '#6ba336', '#6b9d34', '#6b9631', '#638e31']

        # Create canvas and place it within the window
        self._canvas = Canvas(self.root, bg='purple', highlightthickness=0)
        self._canvas.pack(fill=BOTH, expand=True)

    # Create level and name label for frame
    def _create_label(self, start_y: int, player_name: str, level: int):
        label = LabelBar(self, start_y, player_name, level)
        return label

    # Create health bar within the frame
    def _create_health_bar(self, start_y: int, base_health: float, current_health: float):
        health_bar = Bar(self, start_y, base_health, current_health, self.health_bar_gradient)
        return health_bar

    # Create magicka bar within the frame
    def _create_magicka_bar(self, start_y: int, base_magicka: float, current_magicka: float):
        magicka_bar = Bar(self, start_y, base_magicka, current_magicka, self.magicka_bar_gradient)
        return magicka_bar

    # Create fatigue bar within the frame
    def _create_fatigue_bar(self, start_y, base_fatigue: float, current_fatigue: float):
        fatigue_bar = Bar(self, start_y, base_fatigue, current_fatigue, self.fatigue_bar_gradient)
        return fatigue_bar

    def _create_frame(self, player_name: str, level: int, base_health: float, current_health: float,
                      base_magicka: float, current_magicka: float, base_fatigue: float, current_fatigue: float):
        # Do not create further frames if the limit has been reached
        if self._frames_count >= self._frames_limit:
            return

        # Do not create frame for already existing name
        if self._get_index_frame_pair_by_player_name(player_name) is not None:
            print('Unable to create frame for ', player_name)
            return

        # Calculate position of the new frame
        start_y = self._frames_count * self._frame_y_offset

        '''Name correction'''
        # Replace space with unicode representation (regular spaces do not seem to work using Magic Cards font here)
        fixed_name = player_name.replace(' ', '\u2800')
        # Trim name to maximum allowed characters
        if len(fixed_name) > self._name_limit:
            fixed_name = fixed_name[:self._name_limit]

        # Level and name label
        label_bar = self._create_label(start_y, fixed_name, level)

        # Create stats bars
        health_bar = self._create_health_bar(start_y, base_health, current_health)
        magicka_bar = None
        fatigue_bar = None

        bars_count = 1
        # Create magicka bar if enabled
        if self._magicka_enabled:
            magicka_bar = self._create_magicka_bar(start_y + self._frame_image.height() - 1, base_magicka,
                                                   current_magicka)
            bars_count += 1

        # Create fatigue bar if enabled
        if self._fatigue_enabled:
            fatigue_bar = self._create_fatigue_bar(start_y + bars_count * (self._frame_image.height() - 1), base_fatigue,
                                                   current_fatigue)

        # Define frame data and append it to list
        frame_data = {'name': player_name, 'label': label_bar,
                      'bars': {'health': health_bar, 'magicka': magicka_bar, 'fatigue': fatigue_bar}}
        self._frames.append(frame_data)

        # Track how many frames are there in the screen
        self._frames_count += 1
        self._canvas.configure(scrollregion=self.canvas.bbox(ALL))

    def _update_frame(self, player_name: str, level: int, base_health: float, current_health: float,
                      base_magicka: float, current_magicka: float, base_fatigue: float, current_fatigue: float):
        frame = self._get_frame_by_name(player_name)

        # Exit if there is no frame for provided player name
        if frame is None:
            return

        old_level = frame['label'].level

        if level != old_level:
            frame['label'].update(level)

        old_base_health = frame['bars']['health'].base
        old_current_health = frame['bars']['health'].current

        if old_base_health != base_health or old_current_health != current_health:
            frame['bars']['health'].update(base_health, current_health)

        if self._magicka_enabled:
            old_base_magicka = frame['bars']['magicka'].base
            old_current_magicka = frame['bars']['magicka'].current

            if old_base_magicka != base_magicka or old_current_magicka != current_magicka:
                frame['bars']['magicka'].update(base_magicka, current_magicka)

        if self._fatigue_enabled:
            old_base_fatigue = frame['bars']['fatigue'].base
            old_current_fatigue = frame['bars']['fatigue'].current

            if old_base_fatigue != base_fatigue or old_current_fatigue != current_fatigue:
                frame['bars']['fatigue'].update(base_fatigue, current_fatigue)

    def update_frames(self, player_data: dict):
        if player_data is None:
            return

        # Add all names for removal
        player_names_to_remove = [frame['name'] for frame in self._frames]

        # Filter names for which bars should be created or updated
        # Remove names for which any of the create or update action has NOT been executed
        for name in player_data:
            name_data = player_data[name]

            level = name_data['level']
            base_health = name_data['baseHealth']
            current_health = name_data['currentHealth']
            base_magicka = name_data['baseMagicka']
            current_magicka = name_data['currentMagicka']
            base_fatigue = name_data['baseFatigue']
            current_fatigue = name_data['currentFatigue']

            # Frame for such name doesn't exist, create one
            if name not in player_names_to_remove:
                self._create_frame(name, level, base_health, current_health, base_magicka, current_magicka,
                                   base_fatigue, current_fatigue)
            # Frame exists execute an update
            else:
                self._update_frame(name, level, base_health, current_health, base_magicka, current_magicka,
                                   base_fatigue, current_fatigue)
                player_names_to_remove.remove(name)

        # Destroy health frames for remaining names in the list
        for name in player_names_to_remove:
            self._destroy_frame(name)

    # Store a point of mouse pressed on either level_frame, level_text, name_frame or name_text
    # prior to dragging, canvas elements (our frames) are dragged relative to this point
    def move_mark(self, event):
        self._canvas.scan_mark(event.x, event.y)

    # Drag frames within canvas to mouse location unless the scrollregion exceeds the canvas limits
    def move_canvas(self, event):
        print(event.x, event.y)

        self._canvas.scan_dragto(event.x, event.y, 1)

    # Only append frame if the player_name is unique throughout the list
    def _insert_frame(self, frame_data):
        index_frame_pair = self._get_index_frame_pair_by_player_name(frame_data['name'])

        if index_frame_pair is None:
            self._frames.append(frame_data)
            return True

        return False

    # If existent, return index (of frame) and frame as a tuple
    # If nonexistent, return None
    def _get_index_frame_pair_by_player_name(self, player_name: str):
        try:
            index_frame_pair = \
                [(i, self._frames[i]) for i in range(len(self._frames)) if self._frames[i]['name'] == player_name][0]
            return index_frame_pair
        except IndexError:
            return None

    # Get only frame from name
    def _get_frame_by_name(self, player_name: str):
        index_frame_pair = self._get_index_frame_pair_by_player_name(player_name)

        if index_frame_pair is None:
            return None

        return index_frame_pair[1]

    # When a frame is removed any frames below that frame shall be moved upwards by distance between
    # the removed frame and next frame in the sequence
    def _move_frame_on_removal(self, frame, dy):
        label_bar = frame['label']
        label_bar.move(dy)

        for bar_key in frame['bars']:
            stats_bar = frame['bars'][bar_key]
            stats_bar.move(dy)

    # Destroy visual representation of the frame and eventually remove the frame from the list
    # Also update the position of the frames below the one being removed
    def _destroy_frame(self, player_name):
        index_frame_pair = self._get_index_frame_pair_by_player_name(player_name)

        # Check if frame for such player name has been found
        if index_frame_pair is not None:
            frame = index_frame_pair[1]
            label_bar = frame['label']
            label_bar_coords = label_bar.get_coords()

            # Destroy visual representation of frame's components
            label_bar.destroy()

            for bar_key in frame['bars']:
                stats_bar = frame['bars'][bar_key]
                stats_bar.destroy()

            # Update height of frames lower in canvas

            # Distance by which will all remaining frame components shall be moved
            dy = None
            for i in range(index_frame_pair[0] + 1, len(self._frames)):
                update_frame = self._frames[i]
                # Obtain height by which will all remaining frame components shall be moved
                # as a distance between frame to be removed and the next frame below
                if dy is None:
                    update_label_bar_coords = update_frame['label'].get_coords()
                    dy = label_bar_coords[1] - update_label_bar_coords[1]

                # Update below frame's position
                self._move_frame_on_removal(update_frame, dy)

            # Remove frame from list, update total frames count and frames' region within canvas
            self._frames.remove(frame)
            self._frames_count -= 1
            self._canvas.configure(scrollregion=self.canvas.bbox(ALL))

    @property
    def canvas(self):
        return self._canvas

    @property
    def frame_image(self):
        return self._frame_image

    @property
    def frame_y_offset(self):
        return self._frame_y_offset

    @frame_y_offset.setter
    def frame_y_offset(self, value: int):
        self._frame_y_offset = value

    @property
    def label_height(self):
        return self._label_height

    @property
    def label_width(self):
        return self._label_width

    @property
    def font_size(self):
        return self._font_size

    @property
    def font_color(self):
        return self._font_color

    @property
    def level_font(self):
        return self._level_font

    @property
    def name_font(self):
        return self._name_font


class LabelBar:
    def __init__(self, overlay: Overlay, start_y: int, player_name: str, level: int):
        self._overlay = overlay

        self._level = level

        self._level_frame = overlay.canvas.create_rectangle(0, start_y, overlay.label_width,
                                                            start_y + overlay.label_height, outline=overlay.font_color,
                                                            fill='black')
        overlay.canvas.tag_bind(self._level_frame, '<ButtonPress-1>', overlay.move_mark)
        overlay.canvas.tag_bind(self._level_frame, '<B1-Motion>', overlay.move_canvas)

        level_frame_coords = overlay.canvas.coords(self._level_frame)
        level_frame_center = ((level_frame_coords[2] - level_frame_coords[0]) / 2,
                              level_frame_coords[3] - (level_frame_coords[3] - level_frame_coords[1]) / 2 + 2)

        self._level_text = overlay.canvas.create_text(level_frame_center[0], level_frame_center[1],
                                                      fill=overlay.font_color, text=level, font=overlay.level_font)
        overlay.canvas.tag_bind(self._level_text, '<ButtonPress-1>', overlay.move_mark)
        overlay.canvas.tag_bind(self._level_text, '<B1-Motion>', overlay.move_canvas)

        self._name_frame = overlay.canvas.create_rectangle(overlay.label_width, start_y,
                                                           overlay.label_width + overlay.frame_image.width() - 1,
                                                           start_y + overlay.label_height, outline=overlay.font_color,
                                                           fill='black')
        overlay.canvas.tag_bind(self._name_frame, '<ButtonPress-1>', overlay.move_mark)
        overlay.canvas.tag_bind(self._name_frame, '<B1-Motion>', overlay.move_canvas)

        name_frame_coords = overlay.canvas.coords(self._name_frame)
        name_frame_center = (overlay.label_width +
                             (name_frame_coords[2] - name_frame_coords[0]) / 2,
                             name_frame_coords[3] - (name_frame_coords[3] - name_frame_coords[1]) / 2 + 2)

        self._name_text = overlay.canvas.create_text(name_frame_center[0], name_frame_center[1],
                                                     fill=overlay.font_color, text=player_name, font=overlay.name_font)
        overlay.canvas.tag_bind(self._name_text, '<ButtonPress-1>', overlay.move_mark)
        overlay.canvas.tag_bind(self._name_text, '<B1-Motion>', overlay.move_canvas)

    # Update level value
    def update(self, level: int):
        self._level = level
        self._overlay.canvas.itemconfig(self._level_text, text=str(level))

    def get_coords(self):
        return self._overlay.canvas.coords(self._level_frame)

    def move(self, dy):
        self._overlay.canvas.move(self._level_frame, 0, dy)
        self._overlay.canvas.move(self._level_text, 0, dy)
        self._overlay.canvas.move(self._name_frame, 0, dy)
        self._overlay.canvas.move(self._name_text, 0, dy)

    # Destroy visual representation
    def destroy(self):
        self._overlay.canvas.delete(self._level_frame)
        self._overlay.canvas.delete(self._level_text)
        self._overlay.canvas.delete(self._name_frame)
        self._overlay.canvas.delete(self._name_text)

    @property
    def level_frame(self):
        return self._level_frame

    @property
    def name_frame(self):
        return self._name_frame

    @property
    def level(self):
        return self._level


class Bar:

    def __init__(self, overlay: Overlay, start_y: int, base: float, current: float, color_gradient: list):
        self._overlay = overlay

        self._base = base
        self._current = current

        self._frame = overlay.canvas.create_image(40, overlay.label_height + start_y,
                                                  image=overlay.frame_image, anchor=NW)

        self._lines = []

        # Coordinates of bar frame in canvas
        self._frame_x0 = overlay.canvas.coords(self._frame)[0]
        self._frame_x1 = self._frame_x0 + overlay.frame_image.width()

        # Keep small space between lines and bar frame edges
        self._lines_x0 = self._frame_x0 + 2
        self._lines_x1 = self._frame_x1 - 2

        # Adjust lines to be drawn inside inner part of bar frame
        # Offset from top bar frame border
        self._lines_frame_offset_y = 2

        # Get max lines width
        self._lines_max_width = self._lines_x1 - self._lines_x0

        '''Draw the lines finally'''
        # Despite HP not being neccessarily full, draw lines for full hp and update it later
        for i in range(len(color_gradient)):
            color = color_gradient[i]
            line = overlay.canvas.create_line(self._lines_x0,
                                              start_y + self._lines_frame_offset_y + overlay.label_height + i,
                                              self._lines_x1,
                                              start_y + self._lines_frame_offset_y + overlay.label_height + i,
                                              fill=color, width=1)
            self._lines.append(line)

        self.update(base, current)

    # Get ratio from base and current values
    def _calculate_ratio(self, base: float, current: float):
        return current / base

    def get_coords(self):
        return self._overlay.canvas.coords(self._frame)

    def move(self, dy):
        self._overlay.canvas.move(self._frame, 0, dy)

        for line in self._lines:
            self._overlay.canvas.move(line, 0, dy)

    # Update lines width
    def update(self, base: float, current: float):
        self._base = base
        self._current = current

        # Calculate ratio
        ratio = self._calculate_ratio(base, current)

        # Adjust lines' width
        for line in self._lines:
            line_x0 = self._overlay.canvas.coords(line)[0]
            line_y0 = self._overlay.canvas.coords(line)[1]
            self._overlay.canvas.coords(line, line_x0, line_y0,
                                        int(self._lines_max_width * ratio + self._lines_x0), line_y0)

    # Destroy visual representation of the object
    def destroy(self):
        for line in self._lines:
            self._overlay.canvas.delete(line)
        self._overlay.canvas.delete(self._frame)

    @property
    def base(self):
        return self._base

    @property
    def current(self):
        return self._current