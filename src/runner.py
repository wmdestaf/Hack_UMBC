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
    
    
def keydown0(e):
    global canv
    
    #print('down', e.keysym_num)
    k = e.keysym_num
    if k >= 65361 and k <= 65364: 
        keydowns[k-65361] = 1

def game_loop0():
    global canv, grid, keydowns
    
    dx, dy = 0, 0
    #calculate panning of the camera. This logic can be condensed easily.
    if keydowns[0] != keydowns[2]: #left right
        if keydowns[0]: #left
            dx -= 1
            dy += 1
        else: #right
            dx += 1
            dy -= 1
    if keydowns[1] != keydowns[3]: #up down
        if keydowns[1]: #up
            dx -= 1
            dy -= 1
        else: #down
            dx += 1
            dy += 1
            

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
    main.root.title("RPG")
    
    main.root.resizable(False,False)
    main.root.geometry(str(s_width) + 'x' + str(s_height))
    
    main.root.bind("<KeyPress>", keydown0)
    main.root.bind("<KeyRelease>", keyup0)
    
    canv = main.canv = tk.Canvas(main.root, bg='green', height=500, width=500)
    main.canv.pack()
    main.canv.update()
    
    menubar = Menu(main.root)
    menubar.add_command(label="Open", command=load_file,accelerator="Ctrl-O")
    main.root.bind_all("<Control-o>", lambda k: load_file())

    debugmenu = Menu(menubar, tearoff=0)
    #debugmenu.add_command(label="Cell Size", command=disp_cell_size_debug)
    menubar.add_cascade(label="Debug", menu=debugmenu)

    main.root.config(menu=menubar)
    
    mode = main.mode= "ISOMETRIC"
    new() #make fresh board
    keydowns = main.keydowns = [False for i in range(4)] #LEFT UP RIGHT DOWN

    game_loop0()
    root.mainloop() 