import tkinter as tk
from tkinter import filedialog as fd
#from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from os.path import exists
import json
import base64
import copy
import math
import collections
    
class Cell:
    def __init__(self,canv,x,y,color=0):
        self.canv = canv
        self.img_src_quality = None
        self.img = None
        self.img_id = -1
        self.img_selector_match_id = -1
        self.x=x #gridx, gridy
        self.y=y
        self.color = color
        self.possible_colors = ['white','red','pink','blue']
        self.gid = None
    
    def change_pretty(self):
        global canv
        self.color ^= 1
        canv.itemconfigure(self.gid, fill=self.get_gcol())
        canv.update()
    
    def fireImageChangeEvent(self, erase):
        global active_tile, canv
        
        if not active_tile and not erase:
            for i in range(1,5):
                canv.after(50 * i, lambda: self.change_pretty())
            return
        
        if erase: #deletion event
            canv.delete(self.img_id)
            self.img = None
            self.img_src_quality = None
            self.img_id = -1
            self.img_selector_match_id = -1
        else: #creation event
            if self.img: #remove any image which is already there
                canv.delete(self.img_id)
            self.img = active_tile[0]
            self.img_src_quality = active_tile[0]
            self.img_selector_match_id = active_tile[1]
            self.fireImageScaleEvent()
        canv.update()
            
    def fireImageScaleEvent(self):
        global mode, canv
        
        if not self.img:
            return
        
        canv.delete(self.img_id)
          
        dx, dy = disp_cell_size_debug(False)
        pil_img = ImageTk.getimage(self.img_src_quality)
        self.img = ImageTk.PhotoImage(pil_img.resize((int(dx),int(dy)), Image.ANTIALIAS))
        
        #TODO: DOES NOT ACCOUNT FOR IMAGES AT RESOLUTION x:y != 2:1
        onscreen_cell = canv.coords(self.gid)
        draw_x = onscreen_cell[2] #leftest point of the trapezoid
        draw_y = onscreen_cell[5] #highest point of the trapezoid
        
        self.img_id = canv.create_image(draw_x,draw_y,image=self.img)
        canv.itemconfig(self.img_id, state=tk.DISABLED) #ignore clicks on the *square* image, to pass through to the polygonal tile area
        
        #maintain isometric depth
        #find the nearest z-ordered item, and put us below it on the display list.
        for x in range(total_sz[0]):
            for y in range(total_sz[1]):
                if grid[x][y].img and (x > self.x or (x == self.x and y < self.y)):
                    canv.tag_lower(self.img_id, grid[x][y].img_id)
    
    def chg_gcol(self,off): #very legacy
        self.color += off
        self.color %= len(self.possible_colors)
    
    def get_gcol(self): #somewhat legacy
        return self.possible_colors[self.color]
    
    def seralize(self):
        return str(self.img_selector_match_id)
        
    def deserialize(self,x):
        self.img_selector_match_id = int(x)
        
    
    def __repr__(self):
        return ",".join(map(str,self.__dict__.keys())) + "\n" + ",".join(map(str,self.__dict__.values()))

def on_cell_click_factory(x,y,r_id,erase):
    def internal(ignore):
        global grid, canv, root, saved, active_tile
        obj = grid[x][y]

        #if active_tile or erase: #holy antipattern
        obj.fireImageChangeEvent(erase)
        
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
    
    #clean_grid() maybe not.
    cwidth = canv.winfo_width()
    cheight = canv.winfo_height()

    dy = cheight/onscreen[1]
    
    if which_mode == "ORTHOGONAL": #TODO: This doesn't come close to working anymore.
        dx = cwidth/onscreen[0]
        for x in range(total_sz[0]):
            for y in range(total_sz[1]):
                r_id = canv.create_rectangle(dx*x,dy*y,dx*(x+1),dy*(y+1), fill = grid[x][y].get_gcol()) 
                canv.tag_bind(r_id, "<Button-1>", on_cell_click_factory(x,y,r_id, False))
                canv.tag_bind(r_id, "<Button-3>", on_cell_click_factory(x,y,r_id, True))
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
                r_id = grid[x][y].gid
                if not r_id: #grid for the first time
                    r_id = canv.create_polygon([x1,y1,x2,y2,x3,y3,x4,y4], fill = grid[x][y].get_gcol(),outline='black') 
                    canv.tag_bind(r_id, "<Button-1>", on_cell_click_factory(x,y,r_id, False))
                    canv.tag_bind(r_id, "<Button-3>", on_cell_click_factory(x,y,r_id, True))
                    grid[x][y].gid = r_id
                else:
                    canv.coords(r_id,[x1,y1,x2,y2,x3,y3,x4,y4])
        mode = "ISOMETRIC"

        for x in range(total_sz[0]):
            for y in range(total_sz[1]):  
                grid[x][y].fireImageScaleEvent()
    
def game_loop():
    global canv, grid, keydowns, imgs, active_tile
    
    #calculate panning of the camera
    dx = keydowns[2] - keydowns[0]
    dy = keydowns[3] - keydowns[1]
    #actually pan the camera
    if dx:
        canv.xview_scroll(dx, tk.UNITS)
    if dy:
        canv.yview_scroll(dy, tk.UNITS)

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
        canv.xview_scroll(1, tk.UNITS)
        canv.yview_scroll(1, tk.UNITS)
    else: #utter ridiculousness
        dx = cwidth/onscreen[0] * math.sqrt(2) #!
        canv["yscrollincrement"] = (cheight / 2) - (dy/2)
        canv.yview_scroll(-1, tk.UNITS)
        canv["xscrollincrement"] = 0.5 * (total_sz[0] - (onscreen[0]/math.sqrt(2))) * dx
        canv.xview_scroll(1, tk.UNITS)
        
    
    canv["xscrollincrement"] = oldxs
    canv["yscrollincrement"] = oldys
    canv.update()
    
def new():
    global grid, onscreen, base_onscreen, total_sz, base_scrollspeed, mode, curfile, root
    #Make logical board
    onscreen = [6,6]
    base_onscreen = onscreen
    total_sz = [10,10]
    
    if grid:
        clean_grid() #might be bad
    grid = [[Cell(canv,x,y,color=(x+y)%2) for x in range(total_sz[0])] for y in range(total_sz[1])]
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
    generate_grid(mode)
    canv.update()
        
def load_file():
    global root, saved, onscreen, base_onscreen, total_sz, grid, canv, imgs, selector, active_tile
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
            _grid     = [[Cell(canv,x,y,color=(x+y)%2) for x in range(_total_sz[0])] for y in range(_total_sz[1])]
            for y in range(_total_sz[1]): #used up all my brainpower and forgot how to do this as a list comp
                line_serial = f.readline().strip().split(",")
                for x, elem in enumerate(line_serial):
                    _grid[x][y].deserialize(elem)
            if f.readline().strip() != "?????":
                raise Exception
            _imgs = collections.OrderedDict()
            line = f.readline()
            while line:
                iid, width, height, img_base64 = line.split(" ")
                iid, width, height = map(int,(iid,width,height))
                
                img = Image.frombytes('RGBA', (width,height), base64.b64decode(img_base64))
                img_64_32 = ImageTk.PhotoImage(img.resize((64,32), Image.ANTIALIAS))
                img = ImageTk.PhotoImage(img)
                _imgs[iid] = (img, img_64_32)
                line = f.readline()
    except Exception as e:
        print(e)
        messagebox.showinfo('Error', 'The file is unsupported or corrupt.')
        return
        
    clean_grid() #VERY IMPORTANT
        
    total_sz = _total_sz
    onscreen = _onscreen
    base_onscreen = copy.deepcopy(onscreen)
    grid = _grid
    
    generate_grid(mode)
    
    #delete and move any existing tiles in selector
    b_imgs = []
    for key in imgs:
        selector.delete(key)
        b_imgs.append(imgs[key])
        del imgs[key]
    
    file_to_tkmap = collections.OrderedDict()
    for i, logical_id in enumerate(_imgs):
        x = ((i % 3) * 66.66) + 32 + 10     #TODO: Modular scaling
        y = (int(i / 3) * (32+10)) + 16 + 6
        
        r_id = selector.create_image(x,y,image=_imgs[logical_id][1])
        selector.tag_bind(r_id, "<Button-1>", set_active_tile_factory(r_id))
        selector.tag_bind(r_id, "<Button-3>", lambda k: unset_active_tile())
        selector.tag_bind(r_id, "<Shift-Button-3>", destroy_img_factory(r_id))
        file_to_tkmap[logical_id] = r_id 
        file_to_tkmap.move_to_end(logical_id,True)
    selector.update()

    #Rebind each cell to the appropriate id
    for x in range(total_sz[0]):
        for y in range(total_sz[1]):
            grimd = grid[x][y].img_selector_match_id #uhhhhhhhhhhhhhhhhhhhhhhhhhhh
            if grimd != -1:
                old = grimd
                grimd = file_to_tkmap[grimd]
                grid[x][y].img_selector_match_id = grimd
                fullsize = _imgs[old][0]
                active_tile = [fullsize,grimd] #[imgs[sel_id][0],sel_id]
                grid[x][y].fireImageChangeEvent(False)
                
    unset_active_tile()
    
    #Rebind the global mapping (which has logical ids as keys) to now have tk ids as keys. Because start at 0, potential for overlap,
    #so just make a list (2N space) and swap pointers.
    __imgs = collections.OrderedDict()
    for logical_id in file_to_tkmap:
        __imgs[file_to_tkmap[logical_id]] = _imgs[logical_id]
    _imgs = __imgs
    
    #merge back anything that was in selector before load
    for i, reserved_imgs in enumerate(b_imgs, start=len(_imgs)):
        x = ((i % 3) * 66.66) + 32 + 10     #TODO: Modular scaling
        y = (int(i / 3) * (32+10)) + 16 + 6 
        real_id = selector.create_image(x,y,image=reserved_imgs[1])
        selector.tag_bind(real_id, "<Button-1>", set_active_tile_factory(real_id))
        selector.tag_bind(real_id, "<Button-3>", lambda k: unset_active_tile())
        selector.tag_bind(real_id, "<Shift-Button-3>", destroy_img_factory(real_id))
        _imgs[real_id] = reserved_imgs
    
    imgs = _imgs #pointer swap back, and done!
    
    saved = True
    curfile = filename
    root.title("RPG: " + curfile)
    
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
            f.write("?????\n") #sep for img manifest
            #this will make resync a pain but easiest way for now.
            for iid in imgs:
                im = ImageTk.getimage(imgs[iid][0])
                f.write(str(iid) + " " + str(im.width) + " " + str(im.height) + " ")
                raw = "".join(base64.encodebytes(im.tobytes()).decode('utf-8').split("\n"))
                f.write(raw)
                f.write("\n")
                    
    except EnvironmentError:
        return False
    return True
    
def disp_cell_size_debug(pop):
    cwidth = canv.winfo_width()
    cheight = canv.winfo_height()
    dx = ((cwidth/onscreen[0]) * math.sqrt(2)) if mode == "ISOMETRIC" else (cwidth/onscreen[0])
    dy = cheight/onscreen[1]
    if pop:
        messagebox.showinfo('Info', str(round(dx,5)) + "," + str(round(dy,5)))
    return (dx,dy)
    
def import_assets():
    global selector, imgs

    filenames = fd.askopenfilenames(filetypes=[("PNG",".png")])
    errs = []
    raw_imgs = []
    for filename in filenames:
        try:
            pil_img = Image.open(filename)
            #save source quality: 0 = source, 1 = 64x32
            raw_imgs.append( (ImageTk.PhotoImage(pil_img), ImageTk.PhotoImage(pil_img.resize((64,32), Image.ANTIALIAS))) )
        except Exception as e: #TODO: except WHAT?
            print(e)
            errs.append(filename)
            
    if errs: #at least one image failed
        errstr = "\n".join(["Could not open file: " + f for f in errs])
        messagebox.showinfo('Error', errstr)
        
    off = len(imgs)
    #insert valid images and bind selectors:
    for i, img in enumerate(raw_imgs, start=off):
        x = ((i % 3) * 66.66) + 32 + 10     #TODO: Modular scaling
        y = (int(i / 3) * (32+10)) + 16 + 6
        
        r_id = selector.create_image(x,y,image=img[1])
        selector.tag_bind(r_id, "<Button-1>", set_active_tile_factory(r_id))
        selector.tag_bind(r_id, "<Button-3>", lambda k: unset_active_tile())
        selector.tag_bind(r_id, "<Shift-Button-3>", destroy_img_factory(r_id))
        imgs[r_id] = img #store tuple
        imgs.move_to_end(r_id,True)
    selector.update()
        
def set_active_tile_factory(sel_id):
    def set_active_tile(ignore):
        global active_tile, imgs
        active_tile = [imgs[sel_id][0],sel_id]
    return set_active_tile
    
        
def unset_active_tile():
    global active_tile
    active_tile = None
        
def destroy_img_factory(tk_id): 
    def destr_img(ignore): #this is actually necessary because python's GC is overzealous
        global selector, imgs, grid
        imgs.pop(tk_id)
        selector.unbind_all(tk_id)
        selector.delete(tk_id)
        
        #At this point, the images may be unordered in the grid. Move them back into place.
        for i, r_id in enumerate(imgs):
            x = ((i % 3) * 66.66) + 32 + 10 
            y = (int(i / 3) * (32+10)) + 16 + 6
            selector.coords(r_id, x, y)
        unset_active_tile()
        
        for x in range(total_sz[0]):
            for y in range(total_sz[1]):
                if grid[x][y].img_selector_match_id == tk_id: #delete any references still in the grid
                    grid[x][y].fireImageChangeEvent(True)
                
        selector.update()
    return destr_img
    
def show_help():
    string = "..."
    messagebox.showinfo("Info",string)
    
if __name__ == "__main__":
    s_width,s_height = 750,525
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
    selector_bar = ttk.Scrollbar(root, orient=tk.VERTICAL)
    selector_bar.grid(row=0,column=0,sticky=(tk.N,tk.S))
    
    #tile 'selector'
    selector = tk.Canvas(root,yscrollcommand=selector_bar.set, height=500, width=200, borderwidth=5, relief='sunken')
    selector.pack_propagate(0)
    selector.grid(row=0,column=1)
    
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
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

    viewmenu = tk.Menu(menubar, tearoff=0)
    viewmenu.add_command(label="Center",     command=center_screen,    accelerator="C"   )
    viewmenu.add_command(label="Zoom In",    command=lambda: zoom(-1), accelerator="Ctrl +")
    root.bind_all("<Control-plus>",  lambda k: zoom(-1))
    root.bind_all("<Control-equal>", lambda k: zoom(-1)) #!!!
    viewmenu.add_command(label="Zoom Out",   command=lambda: zoom(1),  accelerator="Ctrl -")
    root.bind_all("<Control-minus>", lambda k: zoom(1))
    viewmenu.add_command(label="Reset Zoom", command=lambda: zoom(0),  accelerator="Ctrl+0")
    root.bind_all("<Control-0>",     lambda k: zoom(0))
    #viewmenu.add_separator()
    #swapping requires messing with UI for tiles, not going to bother with for this
    #viewmenu.add_command(label="Orthogonal", command=lambda: generate_grid("ORTHOGONAL"), accelerator="Ctrl+Shift+O")
    #root.bind_all("<Control-Shift-O>", lambda k: generate_grid("ORTHOGONAL"))
    #viewmenu.add_command(label="Isometric",  command=lambda: generate_grid("ISOMETRIC"), accelerator="Ctrl+Shift+I")
    #root.bind_all("<Control-Shift-I>", lambda k: generate_grid("ISOMETRIC"))
    menubar.add_cascade(label="View", menu=viewmenu)
    
    debugmenu = tk.Menu(menubar, tearoff=0)
    debugmenu.add_command(label="Cell Size", command=lambda: disp_cell_size_debug(True))
    menubar.add_cascade(label="Debug", menu=debugmenu)

    menubar.add_command(label="Help...", command=show_help)

    root.config(menu=menubar)
    
    root.bind_all("<Escape>", lambda k: unset_active_tile())
    
    mode="ISOMETRIC"
    grid = None
    new() #make fresh board
    keydowns = [False for i in range(4)] #LEFT UP RIGHT DOWN
    
    saved = False #IO
    imgs = collections.OrderedDict()
    active_tile = None
    
    #root.bind("<Motion>", active_tile_micro_on_cursor)
    
    game_loop()
    root.mainloop()