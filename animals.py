#encoding: utf-8
from tkinter import *
import random
import math
import time
import copy

def draw():
    global canvas_id

    for f in grass:
        clr = f["clr"] if grass_fill else ""
        if grass_circle:
            canvas_id.append(canvas.create_oval(f["x"],f["y"],f["x"]+f["size"],f["y"]+f["size"],fill=clr,outline=f["clr"],width=2))
        if grass_rectangle:
            canvas_id.append(canvas.create_rectangle(f["x"],f["y"],f["x"]+f["size"],f["y"]+f["size"],fill=clr,outline=f["clr"],width=2))
    for c in creatures:
        speed = c["DNA"][0]
        attack = c["DNA"][1]
        efficiency = c["DNA"][2]
        size = c["DNA"][3]
        x,y = c["x"],c["y"]

        clr = "#" + hex((attack-96) * 4 - 1)[2:].zfill(2) + hex((efficiency-36) * 4 - 1)[2:].zfill(2) + hex(speed * 16 - 1)[2:].zfill(2) 
        fill_clr = clr if creature_fill else ""
        if creature_circle:
            canvas_id.append(canvas.create_oval(x,y,x+size,y+size,fill=fill_clr,outline=clr,width=2))
        if creature_rectangle:
            canvas_id.append(canvas.create_rectangle(x,y,x+size,y+size,fill=fill_clr,outline=clr,width=2))

        if draw_line:
            canvas_id.append(canvas.create_line(x+size/2,y+size/2,*calc_pos(x+size/2,y+size/2,c["degree"],c["DNA"][0]),fill="black",width=2))

        if draw_hp:
            color = "green"
            if c["HP"] <= size * 1: color = "red"
            elif c["HP"] >= size * 4: color = "blue"
            canvas_id.append(canvas.create_line(x+size/2,y,x+size/2,y-c["HP"],fill=color,width=5))
    
    grass_l.configure(text="植物:{0}".format(len(grass)))
    creature_l.configure(text="動物:{0}".format(len(creatures)))
    g = []
    s = []
    for c in creatures:
        g.append(c["generation"])
        s.append(species(c["DNA"]))
    max_g = max(g) if g else 0
    min_g = min(g) if g else 0
    ave_g = round(float(sum(g))/len(g),2) if g else 0
    mod_g = mode(g) if g else 0
    mod_s = mode([str(specie[0])+specie[1] for specie in s]) if s else "0A"

    max_generation_l.configure(text="最大世代:{0}".format(max_g))
    min_generation_l.configure(text="最小世代:{0}".format(min_g))
    ave_generation_l.configure(text="平均世代:{0}".format(ave_g))
    mode_generation_l.configure(text="最多世代:{0}".format(mod_g))
    count_species_l.configure(text="種数:{0}".format(len(set(s))))
    mode_species_l.configure(text="最多種:{0}".format(mod_s))

    tk.update()
    for i in canvas_id:
        canvas.delete(i)
    canvas_id = []

def update():
    global grass,creatures
    grass_new = []
    for n in range(len(grass)):
        f = grass[n]
        if random.randint(1,35) == 1 and len(grass) < 800:
            grass_new.append(make_grass(
                f["x"]+random.randint(10,30)*random.choice([-1,1]),
                f["y"]+random.randint(10,30)*random.choice([-1,1]),
                limit(f["size"]+random.randint(-5,5),20,40),
                int(f["clr"][3:5],16)
                ))
        f["size"] *= 1.05
        f["size"] = limit(f["size"],0,40)
        if random.randint(1,100)!=1 or True:
            grass_new.append(f)
    grass = copy.deepcopy(grass_new)
            
    creatures_new = []
    for m in range(len(creatures)):
        c = creatures[m]
        x,y = c["x"],c["y"]
        size = c["DNA"][3]
        attack = c["DNA"][1]
        efficiency = c["DNA"][2]

        for n in range(len(grass)):
            f = grass[n]
            f_x,f_y = f["x"],f["y"]
            f_s = f["size"]
            if touch(x,y,size,f_x,f_y,f_s):
                if grass[n]["size"] > attack*0.1:
                    grass[n]["size"] -= attack*0.1
                    creatures[m]["HP"] += int(attack*0.1 * efficiency/100)
                else:
                    creatures[m]["HP"] += int(f_s * efficiency/100)
                    del grass[n]
                break
        else:
            degree = c["degree"]
            speed = c["DNA"][0]

            c["x"],c["y"] = calc_pos(x,y,degree,speed*1)
            c["degree"] +=  random.randint(-30,30)
            if c["degree"] > 360:
                c["degree"] = c["degree"] % 360
            elif c["degree"] < 0:
                c["degree"] = -c["degree"]

            if c["x"] + c["DNA"][3] > field or c["x"] < 0:
                c["degree"] = 180 - c["degree"]
            if c["y"] + c["DNA"][3] > field or c["y"] < 0:
                c["degree"] = 360 - c["degree"]

        cost = c["DNA"][0] * 0.01 + c["DNA"][1] * 0.01 + c["DNA"][2] * 0.0 + c["DNA"][3] * 0.1
        #cost *= 0.2
        cost *= 0.1
        c["HP"] -= cost
        if c["HP"] >= c["DNA"][3] * 5:
            c["HP"] = c["HP"] // 2.5
            creatures_new.append(copy_creature(c["x"],c["y"],c["HP"]//2,c["generation"],c["DNA"]))
        if c["HP"] > 0:
            creatures_new.append(c)
        else:
            grass.append(make_grass(c["x"],c["y"],5))

    creatures = copy.deepcopy(creatures_new)



def touch(x1,y1,s1,x2,y2,s2):
    if x1 + s1 >= x2 and x1 + s1 <= x2 + s2 and check_y(y1,s1,y2,s2):
        return True
    elif x1 >= x2 and x1 <= x2 + s2 and check_y(y1,s1,y2,s2):
        return True

    return False

def check_y(y1,s1,y2,s2):
    if y1 + s1 >= y2 and y1 + s1 <= y2 + s2:
        return True
    elif y1 >= y2 and y1 <= y2 + s2:
        return True
    return False

def calc_pos(x,y,degree,distance):
    radian = degree * math.pi / 180
    y2 = math.sin(radian) * distance + y
    x2 = math.cos(radian) * distance + x
    return x2,y2

def make_creature():
    speed = random.randint(1,16)
    attack = random.randint(100,160)
    efficiency = random.randint(64,100)
    size = random.randint(1,32)

    x,y = random.randint(0,field),random.randint(0,field)
    degree = random.randint(0,360)

    return {"x":x,"y":y,"degree":degree,"HP":size*10,"generation":1,"DNA":(speed,attack,efficiency,size)}

def limit(v,l,h):
    if v < l:
        return l
    elif v > h:
        return h
    return v

def copy_creature(x,y,hp,generation,DNA):
    dna = ( limit(DNA[0]+random.randint(-1,1),1,16),\
            limit(DNA[1]+random.randint(-3,3),100,160),\
            limit(DNA[2]+random.randint(-3,3),64,100),\
            limit(DNA[3]+random.randint(-2,2),1,32))
    return {"x":x,"y":y,"degree":random.randint(-180,180),"HP":hp,"generation":generation+1,"DNA":dna}

def make_grass(x=None,y=None,size=None,clr=None):
    if size is None:
        size = random.randint(20,40)
    if x is None:
        x,y = random.randint(0,field),random.randint(0,field)
    if clr is None:
        clr = hex(random.randint(0,255))
    else:
        clr = hex(limit(clr+random.randint(-5,5),0,255))
    clr = clr[2:].zfill(2)

    if x < 0: x=0
    if y < 0: y=0
    if x > field: x=field
    if y > field: y=field

    return {"x":x,"y":y,"size":size,"clr":"#00{0}00".format(clr)}

def clicked(x,y):
    global stop_update

    if click_mode == RESEARCH:
        research(x,y)
    elif click_mode == KILL:
        kill_creature(x,y)
    elif click_mode == STOP:
        stop_update = not stop_update
    elif click_mode == ADD:
        add_creature(x,y)

def add_creature(x,y):
    size = made_DNA[3]
    creature = {"x":x-size//2,"y":y-size//2,"generation":1,"degree":random.randint(-180,180),"HP":size*10,"DNA":made_DNA}
    creatures.append(creature)

def kill_creature(x,y):
    global creatures,grass
    new_creatures = []
    new_grass = []
    for c in creatures:
        if (c["x"] - x) ** 2 + (c["y"] - y) ** 2 > c["DNA"][3] ** 2:
            new_creatures.append(c)
    for g in grass:
        if (g["x"] - x) ** 2 + (g["y"] - y) ** 2 > g["size"] ** 2:
            new_grass.append(g)

    creatures = copy.deepcopy(new_creatures)
    grass = copy.deepcopy(new_grass)

def research(x,y):
    for c in creatures:
        if (c["x"] - x) ** 2 + (c["y"] - y) ** 2 < c["DNA"][3] ** 2:
            data_tk = Tk()
            data_tk.title("個体情報")
            data_tk.geometry("120x250")
            data_canvas = Canvas(data_tk,width=50,height=50)
            data_canvas.pack(anchor=N)
            clr = "#" + hex((c["DNA"][1]-96) * 4 - 1)[2:].zfill(2) + hex((c["DNA"][2]-36) * 4 - 1)[2:].zfill(2) + hex(c["DNA"][0] * 16 - 1)[2:].zfill(2) 
            size = c["DNA"][3]
            s = species(c["DNA"])
            data_canvas.create_oval((50-size)//2,(50-size)//2,50-(50-size)//2,50-(50-size)//2,outline=clr,width=2)
            Label(data_tk,text="　世代:{}".format(c["generation"]),font=("",20)).pack(anchor=W)
            Label(data_tk,text="　　種:{}".format(str(s[0])+s[1]),font=("",20)).pack(anchor=W)
            Label(data_tk,text="大きさ:{}".format(c["DNA"][3]),font=("",20)).pack(anchor=W)
            Label(data_tk,text="　速度:{}".format(c["DNA"][0]),font=("",20)).pack(anchor=W)
            Label(data_tk,text="　効率:{}".format(c["DNA"][2]),font=("",20)).pack(anchor=W)
            Label(data_tk,text="攻撃力:{}".format(c["DNA"][1]),font=("",20)).pack(anchor=W)
            break
def make():
    make_tk = Tk()
    make_tk.title("設計")
    make_canvas = Canvas(make_tk,width=50,height=50)
    make_canvas.pack(anchor=N)

    size = IntVar(master=make_tk)
    speed = IntVar(master=make_tk)
    attack = IntVar(master=make_tk)
    efficiency = IntVar(master=make_tk)
    size.set(made_DNA[3])
    speed.set(made_DNA[0])
    attack.set(made_DNA[1])
    efficiency.set(made_DNA[2])

    size_scale = Scale(make_tk,orient=HORIZONTAL,from_=1,to=32,bg="gray",variable=size)
    speed_scale = Scale(make_tk,orient=HORIZONTAL,from_=1,to=16,bg="blue",variable=speed)
    attack_scale = Scale(make_tk,orient=HORIZONTAL,from_=100,to=160,bg="red",variable=attack)
    efficiency_scale = Scale(make_tk,orient=HORIZONTAL,from_=64,to=100,bg="green",variable=efficiency)
    species_label = Label(make_tk,text="0A",font=("",20))
    scl = [size_scale,speed_scale,attack_scale,efficiency_scale]
    for s in scl:
        s.configure(command=lambda e:draw_creature_img(make_canvas,species_label,size.get(),speed.get(),attack.get(),efficiency.get()))
    
    species_label.pack()
    Label(make_tk,text="大きさ",font=("",15)).pack()
    size_scale.pack()
    Label(make_tk,text="速度",font=("",15)).pack()
    speed_scale.pack()
    Label(make_tk,text="攻撃力",font=("",15)).pack()
    attack_scale.pack()
    Label(make_tk,text="効率",font=("",15)).pack()
    efficiency_scale.pack()

def draw_creature_img(make_canvas,species_label,size,speed,attack,efficiency):
    global made_DNA,click_mode
    make_canvas.delete("all")

    x,y = (50-size)//2,(50-size)//2
    clr = "#" + hex((attack-96) * 4 - 1)[2:].zfill(2) + hex((efficiency-36) * 4 - 1)[2:].zfill(2) + hex(speed * 16 - 1)[2:].zfill(2) 
    fill_clr = clr if creature_fill else ""
    if creature_circle:
        make_canvas.create_oval(x,y,x+size,y+size,fill=fill_clr,outline=clr,width=2)
    if creature_rectangle:
        make_canvas.create_rectangle(x,y,x+size,y+size,fill=fill_clr,outline=clr,width=2)
    made_DNA = (speed,attack,efficiency,size)
    click_mode = ADD
    species_label.configure(text="".join(map(str,species(made_DNA))))

def species(DNA):
        #14B ~ 77L
        speed = DNA[0]
        attack = DNA[1]
        efficiency = DNA[2]
        size = DNA[3]

        speacie = int(round(speed * 16 - 1 + (attack - 96) * 4 - 1 + (efficiency - 36) * 4 - 1,-1)) // 10

        #1~5 6~11 12~22 23~32
        size_genre = "L"
        if size <= 5: size_genre="B"
        elif size <= 11: size_genre="S"
        elif size <= 22: size_genre="M"

        return (speacie,size_genre)

def mode(l):
    d = {k:0 for k in set(l)}

    for i in l:
        d[i] += 1

    d_reversed = {d[k]:k for k in d}
    return d_reversed[max(d_reversed)]

def setting():
    setting_tk = Tk()
    setting_tk.title("設定")

    var = [draw_line,draw_hp,grass_circle,grass_rectangle,grass_fill,creature_circle,creature_rectangle,creature_fill]
    txt = ["速度線の描画","体力の描画","植物を円で描画","植物を矩形で描画","植物を塗り潰し","動物を円で描画","動物を矩形で描画","動物を塗り潰し"]
    btn = []

    btn.append(Button(setting_tk,text=txt[0],highlightbackground="blue" if var[0] else "white",command=lambda: change_setting(0,btn)))
    btn.append(Button(setting_tk,text=txt[1],highlightbackground="blue" if var[1] else "white",command=lambda: change_setting(1,btn)))
    btn.append(Button(setting_tk,text=txt[2],highlightbackground="blue" if var[2] else "white",command=lambda: change_setting(2,btn)))
    btn.append(Button(setting_tk,text=txt[3],highlightbackground="blue" if var[3] else "white",command=lambda: change_setting(3,btn)))
    btn.append(Button(setting_tk,text=txt[4],highlightbackground="blue" if var[4] else "white",command=lambda: change_setting(4,btn)))
    btn.append(Button(setting_tk,text=txt[5],highlightbackground="blue" if var[5] else "white",command=lambda: change_setting(5,btn)))
    btn.append(Button(setting_tk,text=txt[6],highlightbackground="blue" if var[6] else "white",command=lambda: change_setting(6,btn)))
    btn.append(Button(setting_tk,text=txt[7],highlightbackground="blue" if var[7] else "white",command=lambda: change_setting(7,btn)))

    for b in btn:
        b.configure(width=12)
        b.pack()


def change_setting(n,btn):
    global draw_line,draw_hp,grass_circle,grass_rectangle,grass_fill,creature_circle,creature_rectangle,creature_fill
    var = [draw_line,draw_hp,grass_circle,grass_rectangle,grass_fill,creature_circle,creature_rectangle,creature_fill]
    var[n] = not var[n]
    btn[n].configure(highlightbackground="blue" if var[n] else "white")
    draw_line,draw_hp,grass_circle,grass_rectangle,grass_fill,creature_circle,creature_rectangle,creature_fill = var

def change_mode(v):
    global click_mode
    click_mode = v

def end():
    global close

    close = True


if __name__ == "__main__":

    tk = Tk()
    field = 800
    stop_update = True
    close = False

    made_DNA = (1,100,64,1)

    STOP = "START/STOP"
    RESEARCH = "RESEARCH"
    ADD = "ADD"
    KILL = "KILL"
    click_mode = STOP
    click_mode_list = [STOP,RESEARCH,KILL,ADD]

    draw_line = False
    draw_hp = False
    grass_circle = True
    grass_rectangle = False
    grass_fill = False
    creature_circle = True
    creature_rectangle = False
    creature_fill = True

    tk.geometry("{0}x{1}".format(field+200,field))
    tk.title("animals")

    canvas = Canvas(tk,width=field,height=field,bg="#bc763c")
    canvas.pack(anchor=W)

    canvas.bind("<ButtonPress>",lambda e:clicked(e.x,e.y))

    FPS_l = Label(tk,text="FPS:0",font=("",20))
    grass_l = Label(tk,text="植物:0",font=("",20))
    creature_l = Label(tk,text="動物:0",font=("",20))
    max_generation_l = Label(tk,text="最大世代:1",font=("",20))
    min_generation_l = Label(tk,text="最小世代:1",font=("",20))
    ave_generation_l = Label(tk,text="平均世代:1",font=("",20))
    mode_generation_l = Label(tk,text="最多世代:1",font=("",20))
    count_species_l = Label(tk,text="種数:0",font=("",20))
    mode_species_l = Label(tk,text="最多種:0",font=("",20))
    setting_btn = Button(tk,text="設定",font=("",30),highlightbackground="blue",bg="blue",command=setting)
    make_btn = Button(tk,text="設計",font=("",30),highlightbackground="green",bg="green",command=make)

    mode_var = StringVar(master=tk)
    mode_var.set(click_mode)
    cng_mode = OptionMenu(tk,mode_var,*click_mode_list,command=lambda e:change_mode(mode_var.get()))

    end_btn = Button(tk,text="終了",font=("",30),highlightbackground="red",bg="red",command=end)
    labels = [FPS_l,grass_l,creature_l,max_generation_l,min_generation_l,ave_generation_l,mode_generation_l,count_species_l,mode_species_l,setting_btn,make_btn,cng_mode,end_btn]

    for i in range(len(labels)):
        labels[i].place(x=field+50,y=30*i)

    canvas_id = []
    creatures = []
    grass = []

    creatures = [make_creature() for i in range(100)]
    creatures = [{"HP":500,"generation":1,"DNA":(16,160,100,1),"x":200,"y":200,"degree":0}]
    creatures = [{"HP":500,"generation":1,"DNA":(16,160,100,32),"x":200,"y":200,"degree":0}]
    creatures = [{"HP":500,"generation":1,"DNA":(1,160,64,32),"x":200,"y":200,"degree":0}]
    grass = [make_grass() for i in range(200)]

    wait = 1 / 20
    while True:
        t = time.time()
        draw()
        if close:
            break
        if not stop_update:
            update()
        else:
            pass
        now = time.time()
        if (now-t) < wait:
            time.sleep(wait-(now-t))
        FPS_l.configure(text="FPS:{0}".format(round(1/(now-t),2)))

