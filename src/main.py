import tkinter as tk
from tkinter import filedialog as fd
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from os.path import exists
import copy
import math
import collections
    
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
    
    def seralize(self):
        #This will become much more complicated.
        return str(self.color)
        
    def deserialize(self,x):
        #ditto
        self.color = int(x)
        
    
    def __repr__(self):
        return ",".join(map(str,self.__dict__.keys())) + "\n" + ",".join(map(str,self.__dict__.values()))
   
def on_cell_click(x,y,r_id,off):
    def internal(ignore):
        global grid, canv, root, saved
        obj = grid[x][y]
        obj.chg_gcol(off) #change the logical representation
        canv.itemconfig(r_id, fill = obj.get_gcol())      
        canv.update()
        saved = False
        root.title(root.title() + ("*" if root.title()[-1] != '*' else ''))
    return internal
   
def clean_grid():
    global grid, total_sz
    for x in range(total_sz[0]):
        for y in range(total_sz[1]):
            canv.delete(grid[x][y].gid)
   
def generate_grid(which_mode):
    global canv, grid, total_sz, onscreen, mode
    
    clean_grid() #Clear any bindings that previously existed
    
    
    cwidth = canv.winfo_width()
    cheight = canv.winfo_height()
    
    #Render the grid orthogonally
    
    dy = cheight/onscreen[1]
    
    if which_mode == "ORTHOGONAL":
        dx = cwidth/onscreen[0]
        for x in range(total_sz[0]):
            for y in range(total_sz[1]):
                r_id = canv.create_rectangle(dx*x,dy*y,dx*(x+1),dy*(y+1), fill = grid[x][y].get_gcol()) 
                canv.tag_bind(r_id, "<Button-1>", on_cell_click(x,y,r_id,1))
                canv.tag_bind(r_id, "<Button-3>", on_cell_click(x,y,r_id,-1))
                grid[x][y].gid = r_id
        mode = "ORTHOGONAL"
    else: #ISOMETRIC
        dx = cwidth/onscreen[0] * math.sqrt(2) #!
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
    global canv, grid, keydowns, imgs
    
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
    global grid, onscreen, base_onscreen, total_sz, base_scrollspeed, mode, curfile, root
    #Make logical board
    onscreen = [6,6]
    base_onscreen = onscreen
    total_sz = [10,10]
    grid = [[Cell((x+y)%2,canv,x,y) for x in range(total_sz[0])] for y in range(total_sz[1])]
    grid[4][4].color = 1
    grid[4][5].color = 3
    grid[5][5].color = 2
    
    generate_grid(mode) #Make graphical board

    canv["xscrollincrement"] = 2*onscreen[0]
    canv["yscrollincrement"] = 2*onscreen[1]
    #move the camera to the center of the canvas
    center_screen()
    canv.update()
    
    curfile = "*Untitled*"
    root.title("RPG: " + curfile)
    
def zoom(n):
    global canv, total_sz, onscreen, base_onscreen, mode
    if not n:
        onscreen = copy.deepcopy(base_onscreen)
    elif min(onscreen[0]+n,onscreen[1]+n) < 2 or max(onscreen[0]+n,onscreen[1]+n) > min(total_sz[0],total_sz[1]):
        return #Zoom too close, divide by zero. Zoom too far, centering becomes annoying to calculate for.
    onscreen[0] += n
    onscreen[1] += n
    generate_grid(mode) #Costly but necessary to rebind click->action areas within TK. 
    canv.update()
        
def load_file():
    global root, saved, onscreen, base_onscreen, total_sz, grid, canv
    #Construct the logical grid
    filename = fd.askopenfilename(filetypes=[("HackUMBC RPG Engine File",".rpg")])
    if not filename:
        #messagebox.showinfo('Error', 'Please provide an appropriate file.')
        return
    try:
        f = open(filename,"r")
    except:
        messagebox.showinfo('Error', 'Could not open ' + filename)
        return
    
    try:
        with f:
            _total_sz = list(map(int,f.readline().strip().split(",")))
            _onscreen = list(map(int,f.readline().strip().split(",")))
            _grid     = [[Cell(0,canv,x,y) for x in range(_total_sz[0])] for y in range(_total_sz[1])]
            for y in range(_total_sz[1]): #used up all my brainpower and forgot how to do this as a list comp
                line_serial = f.readline().strip().split(",")
                for x, elem in enumerate(line_serial):
                    _grid[x][y].deserialize(elem)
    except Exception:
        messagebox.showinfo('Error', 'The file is unsupported or corrupt.')
        return
        
    clean_grid()
        
    total_sz = _total_sz
    onscreen = _onscreen
    base_onscreen = copy.deepcopy(onscreen)
    grid = _grid #SLOW
        
    saved = True
    curfile = filename
    root.title("RPG: " + curfile)
    
    generate_grid(mode)
    center_screen()
    canv.update()
    
def save_file():
    global root, curfile, saved
    
    if curfile == "*Untitled*":    
       return save_f_as()
    if not attempt_write(curfile):
        messagebox.showinfo('Error', 'Could not write to ' + curfile)
        return
        
    root.title("RPG: " + curfile) #important, removes asterisk
    saved = True
    
    
def save_f_as():
    global root, curfile, total_sz, onscreen
    filename = fd.asksaveasfilename(initialfile="Untitled.rpg",defaultextension=".rpg",filetypes=[("HackUMBC RPG Engine File",".rpg")])
    if not filename:
        messagebox.showinfo('Error', 'Please enter an appropriate name.')
        return
    if not attempt_write(filename):
        messagebox.showinfo('Error', 'Could not write to ' + filename)
        return
        
    saved = True
    curfile = filename
    root.title("RPG: " + curfile)
        
def attempt_write(filename):
    try:
        with open(filename,"w") as f:
            f.write(",".join(map(str,total_sz)) + "\n")
            f.write(",".join(map(str,onscreen)) + "\n")
            for x in range(total_sz[0]):
                for y in range(total_sz[1]):    
                    f.write(grid[x][y].seralize() + ("," if y != total_sz[1] - 1 else "\n"))
    except EnvironmentError:
        return False
    return True
    
def disp_cell_size_debug():
    cwidth = canv.winfo_width()
    cheight = canv.winfo_height()
    dx = (cwidth/onscreen[0] * math.sqrt(2)) if mode == "ISOMETRIC" else (cwidth/onscreen[0]) 
    dy = cheight/onscreen[1]
    messagebox.showinfo('Info', str(round(dx,5)) + "," + str(round(dy,5)))
    
def import_assets():
    global selector, imgs

    filenames = fd.askopenfilenames(filetypes=[("PNG",".png")])
    errs = []
    raw_imgs = []
    for filename in filenames:
        try:
            raw_imgs.append(tk.PhotoImage(file=filename))
        except: #TODO: except WHAT?
            errs.append(filename)
            
    if errs: #at least one image failed
        errstr = "\n".join(["Could not open file: " + f for f in errs])
        messagebox.showinfo('Error', errstr)
        
    off = len(imgs)
    #insert valid images and bind selectors:
    for i, img in enumerate(raw_imgs, start=off):
        x = ((i % 3) * 66.66) + 32 + 10 
        y = (int(i / 3) * (32+10)) + 16 + 6
        
        r_id = selector.create_image(x,y,image=img)
        selector.tag_bind(r_id, "<Button-1>", lambda k: donothing)
        selector.tag_bind(r_id, "<Button-3>", lambda k: donothing)
        selector.tag_bind(r_id, "<Shift-Button-3>", destroy_img_factory(r_id))
        imgs[r_id] = img #store
    selector.update()
        
def destroy_img_factory(tk_id): 
    def destr_img(ignore): #this is actually necessary because python's GC is overzealous
        global selector,imgs
        imgs.pop(tk_id)
        selector.unbind_all(tk_id)
        selector.delete(tk_id)
        
        #At this point, the images may be unordered in the grid. Move them back into place.
        for i, r_id in enumerate(imgs):
            x = ((i % 3) * 66.66) + 32 + 10 
            y = (int(i / 3) * (32+10)) + 16 + 6
            selector.coords(r_id, x, y)
        selector.update()
    return destr_img
    
if __name__ == "__main__":
    s_width,s_height = 700,500
    root = tk.Tk()
    ttk.Style(root).theme_use('alt')
    
    root.title("RPG")
    root.resizable(False,False)
    root.geometry(str(s_width) + 'x' + str(s_height))
    
    root.bind("<KeyPress>", keydown)
    root.bind("<KeyRelease>", keyup)
    
    #main canvas
    canv = tk.Canvas(root, bg='green', height=500, width=500)
    canv.grid(row=0,column=2)
    canv.update()
    
    #scrollbar for tiles
    selector_bar = ttk.Scrollbar(root, orient=VERTICAL)
    selector_bar.grid(row=0,column=0,sticky=(N,S))
    
    #tile 'selector'
    selector = tk.Canvas(root, bg='white',yscrollcommand=selector_bar.set, height=500, width=200, borderwidth=5, relief='sunken')
    selector.pack_propagate(0)
    selector.grid(row=0,column=1)
    
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=new, accelerator="Ctrl-N")
    root.bind_all("<Control-n>", lambda k: new()) #needed, as otherwise tries to pass new a param if just given raw FP
    filemenu.add_command(label="Open", command=load_file,accelerator="Ctrl-O")
    root.bind_all("<Control-o>", lambda k: load_file())
    filemenu.add_command(label="Save", command=save_file,accelerator="Ctrl-S")
    root.bind_all("<Control-s>", lambda k: save_file())
    filemenu.add_command(label="Save As...", command=save_f_as,accelerator="Ctrl-Alt-S")
    root.bind_all("<Control-Alt-s>", lambda k: save_f_as())
    filemenu.add_separator()
    filemenu.add_command(label="Import", command=import_assets, accelerator="Ctrl-I")
    root.bind_all("<Control-i>", lambda k: import_assets())
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    viewmenu = Menu(menubar, tearoff=0)
    viewmenu.add_command(label="Center",     command=center_screen,    accelerator="C"   )
    viewmenu.add_command(label="Zoom In",    command=lambda: zoom(-1), accelerator="Ctrl +")
    root.bind_all("<Control-plus>",  lambda k: zoom(-1))
    root.bind_all("<Control-equal>", lambda k: zoom(-1)) #!!!
    viewmenu.add_command(label="Zoom Out",   command=lambda: zoom(1),  accelerator="Ctrl -")
    root.bind_all("<Control-minus>", lambda k: zoom(1))
    viewmenu.add_command(label="Reset Zoom", command=lambda: zoom(0),  accelerator="Ctrl+0")
    root.bind_all("<Control-0>",     lambda k: zoom(0))
    viewmenu.add_separator()
    viewmenu.add_command(label="Orthogonal", command=lambda: generate_grid("ORTHOGONAL"), accelerator="Ctrl+Shift+O")
    root.bind_all("<Control-Shift-O>", lambda k: generate_grid("ORTHOGONAL"))
    viewmenu.add_command(label="Isometric",  command=lambda: generate_grid("ISOMETRIC"), accelerator="Ctrl+Shift+I")
    root.bind_all("<Control-Shift-I>", lambda k: generate_grid("ISOMETRIC"))
    menubar.add_cascade(label="View", menu=viewmenu)
    
    debugmenu = Menu(menubar, tearoff=0)
    debugmenu.add_command(label="Cell Size", command=disp_cell_size_debug)
    menubar.add_cascade(label="Debug", menu=debugmenu)

    root.config(menu=menubar)
    
    mode="ORTHOGONAL"
    new() #make fresh board
    keydowns = [False for i in range(4)] #LEFT UP RIGHT DOWN
    
    saved = False #IO
    imgs = collections.OrderedDict()
    
    game_loop()
    root.mainloop()