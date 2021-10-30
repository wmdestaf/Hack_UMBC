import tkinter as tk
from tkinter import *
from tkinter import ttk
    
class Cell:
    def __init__(self, color,canv,x,y):
        self.canv = canv
        self.color = color
        self.x=x
        self.y=y
        self.color = 0
        self.possible_colors = ['white','red','green','blue']
    
    def chg_gcol(self,off):
        self.color += off
        self.color %= len(self.possible_colors)
    
    def get_gcol(self):
        return self.possible_colors[self.color]
    
    def __repr__(self):
        return ",".join(map(str,self.__dict__.keys())) + "\n" + ",".join(map(str,self.__dict__.values()))
   
def on_cell_click(x,y,r_id,off):
    def internal(ignore):
        global grid, canv
        obj = grid[x][y]
        obj.chg_gcol(off) #change the logical representation
        canv.itemconfig(r_id, fill = obj.get_gcol())      
        canv.update()
    return internal
   
def generate_grid():
    global canv, grid, total_sz, onscreen
    
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
    #print('down', e.keysym_num)
    k = e.keysym_num
    if k >= 65361 and k <= 65364: 
        keydowns[k-65361] = 1
    elif k == 99: #center
        center_screen()

def donothing():
    pass
    
def center_screen():
    global canv, grid, onscreen, total_sz
    
    cwidth = canv.winfo_width()
    cheight = canv.winfo_height()
    
    #Move to the top-left pf the grid
    canv.xview_moveto(0.5) 
    canv.yview_moveto(0.5)
    #Move to the center of the grid
    oldxs = canv["xscrollincrement"]
    oldys = canv["yscrollincrement"]
    
    canv["xscrollincrement"] = 0.5 * (total_sz[0] - onscreen[0]) * (cwidth  / onscreen[0])
    canv["yscrollincrement"] = 0.5 * (total_sz[1] - onscreen[1]) * (cheight / onscreen[1])
    canv.xview_scroll(1, UNITS)
    canv.yview_scroll(1, UNITS)
    
    canv["xscrollincrement"] = oldxs
    canv["yscrollincrement"] = oldys
    
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
    
    #SCROLL SPEED
    canv["xscrollincrement"] = 10
    canv["yscrollincrement"] = 10

    
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=donothing)
    filemenu.add_command(label="Open", command=donothing)
    filemenu.add_command(label="Save", command=donothing)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    viewmenu = Menu(menubar, tearoff=0)
    viewmenu.add_command(label="Center", command=center_screen, accelerator="(C)")
    root.bind_all("<C>", center_screen)
    menubar.add_cascade(label="View", menu=viewmenu)

    root.config(menu=menubar)
    
    
    
    onscreen = [6,6]
    total_sz = [10,10]
    grid = [[Cell((x+y)%2,canv,x,y) for x in range(total_sz[0])] for y in range(total_sz[1])]
    grid[4][4].color = 1
    grid[5][5].color = 2
    
    #move the camera to the center of the canvas
    center_screen()
    
    generate_grid()
    keydowns = [False for i in range(4)] #LEFT UP RIGHT DOWN
    
    
    game_loop()
    root.mainloop()