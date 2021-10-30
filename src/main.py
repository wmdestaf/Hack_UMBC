import tkinter as tk
from tkinter import *
from tkinter import ttk
import copy
import math
    
class Cell:
    def __init__(self, color,canv,x,y):
        self.canv = canv
        self.color = color
        self.x=x
        self.y=y
        self.color = 0
        self.possible_colors = ['white','red','pink','blue']
        self.gid = None
    
    def chg_gcol(self,off):
        self.color += off
        self.color %= len(self.possible_colors)
    
    def get_gcol(self):
        return self.possible_colors[self.color]
    
    def __repr__(self):
        return ",".join(map(str,self.__dict__.keys())) + "\n" + ",".join(map(str,self.__dict__.values()))
   
def on_cell_click(x,y,r_id,off): #this is horrific garbage use of a 'factory' but I couldn't fit it in a lambda
    def internal(ignore):
        global grid, canv
        obj = grid[x][y]
        obj.chg_gcol(off) #change the logical representation
        canv.itemconfig(r_id, fill = obj.get_gcol())      
        canv.update()
    return internal
   
def generate_grid():
    global canv, grid, total_sz, onscreen, mode
    
    #Clear any bindings that previously existed
    for x in range(total_sz[0]):
        for y in range(total_sz[1]):
            canv.delete(grid[x][y].gid)
    
    cwidth = canv.winfo_width()
    cheight = canv.winfo_height()
    
    #Render the grid orthogonally
    dx = cwidth/onscreen[0]
    dy = cheight/onscreen[1]
    
    for x in range(total_sz[0]):
        for y in range(total_sz[1]):
            r_id = canv.create_rectangle(dx*x,dy*y,dx*(x+1),dy*(y+1), fill = grid[x][y].get_gcol()) 
            canv.tag_bind(r_id, "<Button-1>", on_cell_click(x,y,r_id,1))
            canv.tag_bind(r_id, "<Button-3>", on_cell_click(x,y,r_id,-1))
            grid[x][y].gid = r_id
            
    mode = "ORTHOGONAL"
    
def generate_grid_i():
    global canv, grid, total_sz, onscreen, mode
    
    #Clear any bindings that previously existed
    for x in range(total_sz[0]):
        for y in range(total_sz[1]):
            canv.delete(grid[x][y].gid)
    
    cwidth = canv.winfo_width()
    cheight = canv.winfo_height()
    
    dx = cwidth/onscreen[0] * math.sqrt(2) #!
    dy = cheight/onscreen[1]
    
    for x in range(total_sz[0]):
        for y in range(total_sz[1]):  
            x1 = (dx*x*0.5) + (0.0*dx) + (0.5*y*dx)
            y1 = (dy*0.5*y) + (0.5*dy) - (0.5*x*dy)
            x2 = x1 + 0.5*dx
            y2 = y1 - 0.5*dy
            x3 = x1 + 1.0*dx
            y3 = y1
            x4 = x2
            y4 = y1 + 0.5*dy
            r_id = canv.create_polygon([x1,y1,x2,y2,x3,y3,x4,y4], fill = grid[x][y].get_gcol(),outline='black') 
            canv.tag_bind(r_id, "<Button-1>", on_cell_click(x,y,r_id,1))
            canv.tag_bind(r_id, "<Button-3>", on_cell_click(x,y,r_id,-1))
            grid[x][y].gid = r_id
    
    mode = "ISOMETRIC"
    
def game_loop():
    global canv, grid, keydowns
    
    #calculate panning of the camera
    dx = keydowns[2] - keydowns[0]
    dy = keydowns[3] - keydowns[1]
    #actually pan the camera
    if dx:
        canv.xview_scroll(dx, UNITS)
    if dy:
        canv.yview_scroll(dy, UNITS)
    canv.update()
    canv.after(25, game_loop)
    
    
def keyup(e):
    #print('up', e.keysym_num)
    k = e.keysym_num
    if k >= 65361 and k <= 65364: #pan
        keydowns[k-65361] = 0
    
    
def keydown(e):
    global canv
    
    #print('down', e.keysym_num)
    k = e.keysym_num
    if k >= 65361 and k <= 65364: 
        keydowns[k-65361] = 1
    elif k == 99: #center
        center_screen()
        canv.update()
        

def donothing():
    pass
    
def center_screen():
    global canv, grid, onscreen, total_sz, mode
    
    cwidth = canv.winfo_width()
    cheight = canv.winfo_height()
    
    #Move to the top-left pf the grid
    canv.xview_moveto(0.5) 
    canv.yview_moveto(0.5)
    #Move to the center of the grid
    oldxs = canv["xscrollincrement"]
    oldys = canv["yscrollincrement"]
    
    dy = cheight/onscreen[1]
    
    if mode == "ORTHOGONAL":
        dx = cwidth/onscreen[0]
        canv["xscrollincrement"] = 0.5 * (total_sz[0] - onscreen[0]) * dx
        canv["yscrollincrement"] = 0.5 * (total_sz[1] - onscreen[1]) * dy
        canv.xview_scroll(1, UNITS)
        canv.yview_scroll(1, UNITS)
    else: #utter ridiculousness
        dx = cwidth/onscreen[0] * math.sqrt(2) #!
        canv["yscrollincrement"] = (cheight / 2) - (dy/2)
        canv.yview_scroll(-1, UNITS)
        canv["xscrollincrement"] = 0.5 * (total_sz[0] - (onscreen[0]/math.sqrt(2))) * dx
        canv.xview_scroll(1, UNITS)
        
    
    canv["xscrollincrement"] = oldxs
    canv["yscrollincrement"] = oldys
    canv.update()
    
def new():
    global grid, onscreen, base_onscreen, total_sz, base_scrollspeed
    #Make logical board
    onscreen = [6,6]
    base_onscreen = onscreen
    total_sz = [10,10]
    grid = [[Cell((x+y)%2,canv,x,y) for x in range(total_sz[0])] for y in range(total_sz[1])]
    grid[4][4].color = 1
    grid[4][5].color = 3
    grid[5][5].color = 2
    generate_grid() #Make graphical board

    canv["xscrollincrement"] = 2*onscreen[0]
    canv["yscrollincrement"] = 2*onscreen[1]
    #move the camera to the center of the canvas
    center_screen()
    canv.update()
    
def zoom(n):
    global canv, total_sz, onscreen, base_onscreen, mode
    if not n:
        onscreen = copy.deepcopy(base_onscreen)
    elif min(onscreen[0]+n,onscreen[1]+n) < 2 or max(onscreen[0]+n,onscreen[1]+n) > min(total_sz[0],total_sz[1]):
        return #Zoom too close, divide by zero. Zoom too far, centering becomes annoying to calculate for.
    onscreen[0] += n
    onscreen[1] += n
    generate_grid() if mode == "ORTHOGONAL" else generate_grid_i()  #Costly but necessary to rebind click->action areas within TK. 
    canv.update()
        
    
if __name__ == "__main__":
    s_width,s_height = 500,500
    root = tk.Tk()
    root.title("RPG")
    root.resizable(False,False)
    root.geometry(str(s_width) + 'x' + str(s_height))
    
    root.bind("<KeyPress>", keydown)
    root.bind("<KeyRelease>", keyup)
    
    canv = tk.Canvas(root, bg='green', height=500, width=500)
    canv.pack()
    canv.update()
    
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=new, accelerator="Ctrl-N")
    root.bind_all("<Control-n>", lambda k: new()) #needed, as otherwise tries to pass new a param if just given raw FP
    filemenu.add_command(label="Open", command=donothing,accelerator="Ctrl-O")
    filemenu.add_command(label="Save", command=donothing,accelerator="Ctrl-S")
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    viewmenu = Menu(menubar, tearoff=0)
    viewmenu.add_command(label="Center",     command=center_screen,    accelerator="(C)"   )
    viewmenu.add_command(label="Zoom In",    command=lambda: zoom(-1), accelerator="Ctrl +")
    root.bind_all("<Control-plus>",  lambda k: zoom(-1))
    root.bind_all("<Control-equal>", lambda k: zoom(-1)) #!!!
    viewmenu.add_command(label="Zoom Out",   command=lambda: zoom(1),  accelerator="Ctrl -")
    root.bind_all("<Control-minus>", lambda k: zoom(1))
    viewmenu.add_command(label="Reset Zoom", command=lambda: zoom(0),  accelerator="Ctrl+0")
    root.bind_all("<Control-0>",     lambda k: zoom(0))
    viewmenu.add_separator()
    viewmenu.add_command(label="Orthogonal", command=generate_grid,   accelerator="Ctrl+Alt+Shift+O")
    root.bind_all("<Control-Alt-Shift-O>", lambda k: generate_grid())
    viewmenu.add_command(label="Isometric",  command=generate_grid_i, accelerator="Ctrl+Alt+Shift+I")
    root.bind_all("<Control-Alt-Shift-I>", lambda k: generate_grid_i())
    menubar.add_cascade(label="View", menu=viewmenu)

    root.config(menu=menubar)
    
    new() #make fresh board
    keydowns = [False for i in range(4)] #LEFT UP RIGHT DOWN
    
    game_loop()
    root.mainloop()