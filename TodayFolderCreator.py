# -*- coding: utf-8 -*-
import sys
import os
import ctypes
from ctypes import wintypes
import json
import shutil
import datetime
import zipfile
import subprocess
import tkinter as tk
from tkinter import ttk

SETTINGS_FILE = 'settings.json'

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_settings_path():
    return os.path.join(get_base_dir(), SETTINGS_FILE)

def load_settings():
    default_settings = {
        'open_after_drop': False,
        'move_across_drives': False,
        'under_todayfolders': False,
        'compress_past': False,
        'compress_days': 3,
        'delete_past': False,
        'delete_days': 7
    }
    s_path = get_settings_path()
    if os.path.exists(s_path):
        try:
            with open(s_path, 'r', encoding='utf-8') as f:
                default_settings.update(json.load(f))
        except:
            pass
    return default_settings

def save_settings(settings):
    try:
        with open(get_settings_path(), 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except:
        pass

def is_shift_pressed():
    # VK_SHIFT is 0x10
    return (ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000) != 0



class SettingsApp:
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        root.title("DayBox (設定)")
        
        window_width = 460
        window_height = 280
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        root.resizable(False, False)
        
        style = ttk.Style()
        style.configure('.', font=('Meiryo UI', 9))

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.var_open = tk.BooleanVar(value=settings.get('open_after_drop', False))
        self.var_move = tk.BooleanVar(value=settings.get('move_across_drives', False))
        self.var_under = tk.BooleanVar(value=settings.get('under_todayfolders', False))
        self.var_compress = tk.BooleanVar(value=settings.get('compress_past', False))
        self.var_days = tk.IntVar(value=settings.get('compress_days', 3))
        self.var_delete = tk.BooleanVar(value=settings.get('delete_past', False))
        self.var_del_days = tk.IntVar(value=settings.get('delete_days', 7))

        ttk.Checkbutton(frame, text="ドロップ後にフォルダを開く", variable=self.var_open).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(frame, text="ドライブが違う場合でも、コピーせず移動", variable=self.var_move).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(frame, text="作成先を「DayBox」親フォルダ内にまとめる", variable=self.var_under).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        comp_frame = ttk.Frame(frame)
        comp_frame.grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(comp_frame, text="過去のDayBoxを圧縮する", variable=self.var_compress).pack(side=tk.LEFT)
        self.spin_days = ttk.Spinbox(comp_frame, from_=0, to=365, textvariable=self.var_days, width=5)
        self.spin_days.pack(side=tk.LEFT, padx=5)
        ttk.Label(comp_frame, text="日後 (""0""で直ちに実行)").pack(side=tk.LEFT)

        del_frame = ttk.Frame(frame)
        del_frame.grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(del_frame, text="過去のDayBoxを削除する", variable=self.var_delete).pack(side=tk.LEFT)
        self.spin_del_days = ttk.Spinbox(del_frame, from_=0, to=365, textvariable=self.var_del_days, width=5)
        self.spin_del_days.pack(side=tk.LEFT, padx=5)
        ttk.Label(del_frame, text="日後 (""0""で直ちに実行)").pack(side=tk.LEFT)

        btn_save = ttk.Button(frame, text="Save", command=self.save_and_close)
        btn_save.place(relx=1.0, rely=0.0, anchor=tk.NE)

        ttk.Separator(root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0,0))
        
        info_text = (
            "○操作\n"
            "   [ダブルクリック] 今日のDayBoxを作成・表示\n"
            "   [ドラッグ＆ドロップ] DayBoxを作成・アイテムを整理\n"
            "   [本体をShift + ダブルクリック] 設定画面を表示\n"
            "   ※ ショートカットに「--nosettings」を付けると、Shiftを押していても設定画面を開きません。"
        )
        lbl_info = tk.Label(root, justify=tk.LEFT, text=info_text, anchor='nw', bg='#f0f0f0', font=('Meiryo UI', 9))
        lbl_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def save_and_close(self):
        self.settings['open_after_drop'] = self.var_open.get()
        self.settings['move_across_drives'] = self.var_move.get()
        self.settings['under_todayfolders'] = self.var_under.get()
        self.settings['compress_past'] = self.var_compress.get()
        try:
            val = int(self.spin_days.get())
            if val < 0: val = 0
            self.settings['compress_days'] = val
        except:
            pass
        self.settings['delete_past'] = self.var_delete.get()
        try:
            val = int(self.spin_del_days.get())
            if val < 0: val = 0
            self.settings['delete_days'] = val
        except:
            pass
        save_settings(self.settings)
        self.root.destroy()

def get_today_folder_path(settings):
    base = get_base_dir()
    if settings.get('under_todayfolders', False):
        base = os.path.join(base, 'DayBox')
        os.makedirs(base, exist_ok=True)
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    folder_path = os.path.join(base, today_str)
    return folder_path

def create_and_open_today_folder(settings):
    path = get_today_folder_path(settings)
    os.makedirs(path, exist_ok=True)
    subprocess.Popen(f'explorer "{path}"')

def get_drive(path):
    return os.path.splitdrive(os.path.abspath(path))[0].upper()

def do_compression(settings):
    if not settings.get('compress_past', False):
        return
    days = settings.get('compress_days', 3)
    base = get_base_dir()
    if settings.get('under_todayfolders', False):
        base = os.path.join(base, 'DayBox')
    
    if not os.path.exists(base):
        return

    cutoff = datetime.date.today() - datetime.timedelta(days=days)
    
    for item in os.listdir(base):
        item_path = os.path.join(base, item)
        if os.path.isdir(item_path):
            try:
                d = None
                if len(item) == 10 and item.replace('-', '').isdigit():
                    d = datetime.datetime.strptime(item, '%Y-%m-%d').date()
                elif len(item) == 8 and item.isdigit():
                    d = datetime.datetime.strptime(item, '%Y%m%d').date()
                    
                if d is not None and d <= cutoff:
                    zip_path = os.path.join(base, item + '.zip')
                    if not os.path.exists(zip_path):
                        shutil.make_archive(item_path, 'zip', base, item)
                        shutil.rmtree(item_path)
            except Exception:
                pass

def rename_if_exists(dst):
    if not os.path.exists(dst):
        return dst
    base_target = dst
    name, ext = os.path.splitext(base_target)
    counter = 1
    while os.path.exists(dst):
        dst = f"{name}_{counter}{ext}"
        counter += 1
    return dst

def process_dropped_files(files, settings):
    target_dir = get_today_folder_path(settings)
    os.makedirs(target_dir, exist_ok=True)
    target_drive = get_drive(target_dir)

    for src in files:
        if not os.path.exists(src):
            continue
            
        src_drive = get_drive(src)
        basename = os.path.basename(src)
        dst = os.path.join(target_dir, basename)
        dst = rename_if_exists(dst)

        move_across = settings.get('move_across_drives', False)

        try:
            if src_drive != target_drive and not move_across:
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            else:
                shutil.move(src, dst)
        except Exception:
            pass

    if settings.get('open_after_drop', False):
        subprocess.Popen(f'explorer "{target_dir}"')

def do_deletion(settings):
    if not settings.get('delete_past', False):
        return
    days = settings.get('delete_days', 7)
    base = get_base_dir()
    if settings.get('under_todayfolders', False):
        base = os.path.join(base, 'DayBox')
    
    if not os.path.exists(base):
        return

    cutoff = datetime.date.today() - datetime.timedelta(days=days)
    
    for item in os.listdir(base):
        item_path = os.path.join(base, item)
        
        name_to_check = item
        if item.endswith('.zip'):
            name_to_check = item[:-4]
            
        d = None
        if len(name_to_check) == 10 and name_to_check.replace('-', '').isdigit():
            try:
                d = datetime.datetime.strptime(name_to_check, '%Y-%m-%d').date()
            except ValueError:
                pass
        elif len(name_to_check) == 8 and name_to_check.isdigit():
            try:
                d = datetime.datetime.strptime(name_to_check, '%Y%m%d').date()
            except ValueError:
                pass
                
        if d is not None and d <= cutoff:
            try:
                if os.path.isdir(item_path):
                    def remove_readonly(func, path, excinfo):
                        os.chmod(path, 0o777)
                        func(path)
                    shutil.rmtree(item_path, onerror=remove_readonly)
                else:
                    os.remove(item_path)
            except Exception:
                pass

def main():
    settings = load_settings()
    do_compression(settings)
    do_deletion(settings)

    args = sys.argv[1:]
    
    # User can place "--nosettings" in the shortcut arguments to explicitly 
    # disable the settings screen from opening even if shift is pressed.
    force_no_settings = False
    if '--nosettings' in args:
        force_no_settings = True
        args = [a for a in args if a != '--nosettings']

    # When double-clicking without drag and drop, len(args) == 0.
    # When drag-and-drop, len(args) > 0.
    if len(args) == 0 and is_shift_pressed() and not force_no_settings:
        root = tk.Tk()
        app = SettingsApp(root, settings)
        root.mainloop()
    elif len(args) == 0:
        create_and_open_today_folder(settings)
    else:
        process_dropped_files(args, settings)

if __name__ == '__main__':
    main()
