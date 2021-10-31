import main
from main import *
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from os.path import exists
import copy
import math

def keyup0(e):
    #print('up', e.keysym_num)
    k = e.keysym_num
    if k >= 65361 and k <= 65364: #pan
        keydowns[k-65361] = 0
    
def toggle_lock():
    global camera_lock, viewmenu
    
    if camera_lock == False:
        center_screen()
        camera_lock = True
    else:
        camera_lock = False
        
    #set label
    pre = "L" if not camera_lock else "Unl"
    viewmenu.entryconfigure(1, label = pre + "ock Camera")
    
def keydown0(e):
    global canv
    
    #print('down', e.keysym_num)
    k = e.keysym_num
    if k >= 65361 and k <= 65364: 
        keydowns[k-65361] = 1
    elif k == 121: #y
        toggle_lock()
        

def game_loop0():
    global canv, grid, keydowns
    
    dx, dy = 0, 0
    #calculate panning of the camera. This logic can be condensed easily.
    if camera_lock: #Move with player
        if keydowns[0] != keydowns[2]: #left right
            if keydowns[0]: #left
                dx -= 1
                dy += 1
            else: #right
                dx += 1
                dy -= 1
        elif keydowns[1] != keydowns[3]: #up down
            if keydowns[1]: #up
                dx -= 1
                dy -= 1
            else: #down
                dx += 1
                dy += 1

        #TODO: update player 'position' off dx, dy
        #...
    else: #move with arrowkeys
        dx = keydowns[2] - keydowns[0]
        dy = keydowns[3] - keydowns[1]
        

    #actually pan the camera
    if dx:
        canv.xview_scroll(dx, UNITS)
    if dy:
        canv.yview_scroll(dy, UNITS)
    canv.update()
    canv.after(25, game_loop0)

if __name__ == "__main__":
    s_width,s_height = 500,500
    root = main.root = tk.Tk()
    root.title("RPG")
    
    root.resizable(False,False)
    root.geometry(str(s_width) + 'x' + str(s_height))
    
    root.bind("<KeyPress>", keydown0)
    root.bind("<KeyRelease>", keyup0)
    
    canv = main.canv = tk.Canvas(root, bg='black', height=500, width=500)
    canv.pack()
    canv.update()
    
    
    menubar = Menu(root)
    menubar.add_command(label="Open", command=load_file,accelerator="Ctrl-O")
    root.bind_all("<Control-o>", lambda k: load_file())
    
    viewmenu = Menu(root, tearoff=0)
    lock_widget_id = viewmenu.add_command(label="Unlock Camera", command=toggle_lock, accelerator="Y")
    menubar.add_cascade(label="View", menu=viewmenu)

    debugmenu = Menu(menubar, tearoff=0)
    #debugmenu.add_command(label="Cell Size", command=disp_cell_size_debug)
    menubar.add_cascade(label="Debug", menu=debugmenu)

    root.config(menu=menubar)
    
    mode = main.mode= "ISOMETRIC"
    new() #make fresh board
    keydowns = main.keydowns = [False for i in range(4)] #LEFT UP RIGHT DOWN
    camera_lock = True

    game_loop0()
    root.mainloop() 