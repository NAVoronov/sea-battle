from tkinter import *
import random
import time
from ship import *
from var import *
from tkinter import messagebox

pic = {0: ".\\pic\\human.png", 1: ".\\pic\\comp.png"}

Player1 = 1
Player2 = 2
GameStopped = 0

but_txt = {Player1 : "Stop the Game", Player2 : "Stop the Game", GameStopped : "Start the Game"}

# ---------------------класс игрового поля-----------------------------


class BattleField:

    # ---------------------------------
    def setBoats(self):

        if not( GameStatus == GameStopped):
            return 0
        
        battleCells = []
        
        for sh in self.ships:

            decks = 1  # есть ли вокруг корабли ?
            while decks:
                a, b, sh.orient = random.randint(1, self.x), random.randint(1, self.y), random.randint(0, 1)

                if battleCells.count(chr(b + 64) + str(a)):  # попали в уже корабль
                    continue

                j, bound = a, self.x  # горизонтальная постановка
                if sh.orient:  # вертикальная постановка
                    j, bound = b, self.y

                if j + sh.decks > bound+1:
                    continue  # вылезем за поле

                k = ""
                for i in range(j - 1, j + sh.decks + 1):
                    if sh.orient:  # вертикальная постановка
                        k = chr(i + 64)
                        decks = battleCells.count(k + str(a-1)) + battleCells.count(k + str(a)) + battleCells.count(k + str(a+1))
                    else:  # горизонтальная постановка
                        k = str(i)
                        decks = battleCells.count(chr(b+63) + k) + battleCells.count(chr(b+64) + k) + battleCells.count(chr(b+65) + k)

                    if decks:
                        break

            sh.cells.clear()
            sh.wounds.clear()
            j = b if sh.orient else a
            for i in range(j, j + sh.decks):
                       # вертикальная постановка              # горизонтальная постановка
                cell = chr(i + 64) + str(a) if sh.orient else chr(b + 64) + str(i)

                battleCells.append(cell)
                sh.cells.append(cell)

        self.decksQ = len(battleCells)
        self.hitCells.clear()
        return 1
    # ---------------------------------

    def __init__(self, pl, kol_x, kol_y, place, can):
        self.plType = pl  # 0-человек, 1-комп
        self.x = kol_x  # кол-во клеток Х
        self.y = kol_y  # кол-вол клеток У
        self.pl = place  # левое поле или правое
        self.canv = can  # канва для отрисовки поля
        self.size = 0  # размер клетки

        self.decksQ = 0 # кол-во палуб в поле
        self.moves = 0
        self.hitCells = []

        self.canv.bind("<Button-1>", self.B1Click)
        self.canv.bind("<Button-3>", self.B3Click)
        self.canv.bind("<B1-Motion>", self.onMove)
        self.canv.bind("<ButtonRelease-1>", self.B1Release)
        self.canv.bind("<ButtonRelease-3>", self.B1Release)
        self.canv.bind("<KeyPress>", self.onKeyPress)

        self.canv.bind("<FocusIn>", self.f_in)
        self.canv.bind("<FocusOut>", self.f_out)

        #      активный кораблик в момент перетаскивания по полю
        self.activeShip = {"ship" : None, "restrict" : True, "actCell" : "", "lastPl" : []}

        #      корабли создаём - кол-во палуб, ориентация и канва (чьорт её побьери)
        self.ships = (Ship(4, random.randint(0, 1), can),
                      Ship(3, random.randint(0, 1), can), Ship(3, random.randint(0, 1), can),
                      Ship(2, random.randint(0, 1), can), Ship(2, random.randint(0, 1), can), Ship(2, random.randint(0, 1), can),
                      Ship(1, 0, can), Ship(1, 0, can), Ship(1, 0, can), Ship(1, 0, can)
                      )

        #      изображение игрока на кнопочке
        self.im = PhotoImage(file=pic[self.plType])
        self.canv.create_image(2, 2, image=self.im, anchor="nw", tags="pic")

        self.setBoats()  # поставили кораблики

    # ---------------рисовалка игрового поля---------------------------------------------------------------
    def draw(self):
        self.canv.delete("field")  # стираем все старые клетки, корабли пр. требуху

        for i in range(1, self.x + 1):  # перебираем вертикали
            for j in range(1, self.y + 1):  # и горизонтали
                self.canv.create_rectangle(i * self.size, j * self.size, (i + 1) * self.size, (j + 1) * self.size,
                                           tags=["field", chr(j + 64) + str(i)], fill=col[0])

        for i in range(self.x + 2):  # рисуем цифиры
            if i in range(1, self.x + 1):
                self.canv.create_text(i * self.size + self.size / 2, self.size / 2, text=str(i), tags=["field", "digit"])

        for i in range(self.y + 2):  # и букавы
            if i in range(1, self.y + 1):
                self.canv.create_text(self.size / 2, i * self.size + self.size / 2, text=chr(i + 64), tags=["field", "alfa"])

        for cell in self.hitCells:  # и если в игре, то места, куда попали крестиком метим
            self.draw_cross( int(cell[1:]), ord(cell[:1])-64 )

        for sh in self.ships:  # перебрали и нарисовали корабли
            sh.draw(sh.visible)

    # ---------------конец рисовалки игрового поля---------------------------------------------------------------

    def f_in(self, e):
        self.canv.config(bg = col[1])

    def f_out(self, e):
        self.canv.config(bg = col[0])        
    
    # ---------------------------------
    def B1Release(self, e):
        if GameStatus == GameStopped:

            if self.activeShip["ship"] is None or not self.activeShip["ship"].visible:
                return

            #  попытка поставить корабль в запретное место - он вернётся туда, где взят был
            if self.activeShip["restrict"]:
                self.activeShip["ship"].cells = self.activeShip["lastPl"].copy()
                self.activeShip["ship"].draw(True)

    # ---------------------------------
    def onMove(self, e):
        if not( GameStatus == GameStopped):
            return -1

        if self.activeShip["ship"] is None or not self.activeShip["ship"].visible:
            return 1

        badColor = False
        
        it = self.canv.find_overlapping(e.x, e.y, e.x, e.y)  # смотрим все объекты под мышой
        for i in it:  # и перебираем их
            tags = self.canv.gettags(i)
            if "field" in tags and tags[1] not in ["alfa", "digit", self.activeShip["actCell"] ]:

                sh, b, a = self.activeShip["ship"], ord(tags[1][:1]), int(tags[1][1:])

                j, bound = a, self.x  # горизонтальная постановка
                if sh.orient:  # вертикальная постановка
                    j, bound = b-64, self.y

                if j + sh.decks > bound+1:  # вылезем за поле
                    return 2

                bC = []
                for k in self.ships:  # узнаем все клетки, где есть корабли
                    if k.item != sh.item:  # кроме текущего, ибо его таскаем
                        for q in k.cells:
                            bC.append(q)

                decks, k, badColor = 0, "", False

                # посмотрим - есть ли вокруг корабли ?
                for i in range(j - 1, j + sh.decks + 1):
                    if sh.orient:  # вертикальная постановка
                        k = chr(i+64)
                        decks = bC.count(k + str(a - 1)) + bC.count(k + str(a)) + bC.count(k + str(a + 1))
                    else:  # горизонтальная постановка
                        k = str(i)
                        decks = bC.count(chr(b - 1) + k) + bC.count(chr(b) + k) + bC.count(chr(b + 1) + k)

                    if decks:
                        badColor = True
                        break

                sh.cells.clear()                
                for i in  range(j, j + sh.decks):
                    if sh.orient:  # вертикальная постановка
                        sh.cells.append( chr(i+64) + str(a) )
                    else:  # горизонтальная постановка
                        sh.cells.append( chr(b) + str(i) )
                    
                sh.draw(badColor+1) #  так уж повелось у меня - 0,1,2 = blue,green,red

                self.activeShip["restrict"] = badColor
                self.activeShip["actCell"] = tags[1]

        return badColor-1 # при запрете установки вернёт 0

    # --------------- ПКМ - меняем ориентацию корабля ------------------
    def B3Click(self, e):
        if GameStatus == GameStopped:

            self.B1Click(e)  # оно даст нам активный корабль

            if self.activeShip["ship"] is None or len(self.activeShip["lastPl"]) == 1:
                return

            sh, b, a = self.activeShip["ship"], ord(self.activeShip["actCell"][:1]), int(self.activeShip["actCell"][1:])

            sh.orient = int( not sh.orient )
            
            j, bound = a, self.x  # горизонтальная постановка
            if sh.orient:  # вертикальная постановка
                j, bound = b-64, self.y

            step = 1
            if j + sh.decks > bound+1:  # если вылезем за поле (вправо или вниз), то ставить надо влево или вверх
                step = -1
                if sh.orient:  # вертикальная постановка
                    e.y -= (sh.decks-1)*self.size
                else:
                    e.x -= (sh.decks-1)*self.size

            sh.cells.clear()
            for i in range(j, j + sh.decks*step, step):
                if sh.orient:  # вертикальная постановка
                    sh.cells.append( chr(i+64) + str(a) )
                else:  # горизонтальная постановка
                    sh.cells.append( chr(b) + str(i) )

            self.activeShip["actCell"] = ""  # иначе onMove не нарисует ничего
            if not self.onMove(e):
                sh.orient = int( not sh.orient )

    # --------------------------------------------------------------------------
    def draw_cross(self, a, b, col="black"):
        self.canv.create_line(a * self.size+5, b * self.size+5, (a+1) * self.size-5, (b+1) * self.size-5, tags="field", width=5, fill = col )
        self.canv.create_line((a+1) * self.size-5, b * self.size+5, a * self.size+5, (b+1) * self.size-5, tags="field", width=5, fill = col )        

    # ---------------------------------
    def B1Click(self, e):
        global GameStatus

        if GameStatus == GameStopped: # это если не играем ещё
            self.canv.focus_set()
            it = self.canv.find_overlapping(e.x, e.y, e.x, e.y)
            self.activeShip = {"ship" : None, "restrict" : True, "actCell": "", "lastPl" : []}
            
            for i in it:
                tags = self.canv.gettags(i)

                if 'field' in tags:
                    self.activeShip["actCell"] = tags[1]

                if 'boat' in tags:  # если этот объект - лодка, то
                    for sh in self.ships:  # надо найти его среди лодок !
                        if sh.item == i:
                            self.activeShip["ship"] = sh                        
                            self.activeShip["lastPl"] = sh.cells.copy()

                if "pic" in tags:  # это картинка с менюшкой
                    popup = Menu(self.canv, tearoff=0)
                    if self.plType == 1:  # был комп - меняем на человека
                        lab = "Сменить на человека"
                    else:
                        lab = "Сменить на комп"

                    popup.add_command(label=lab, command=self.chType)
                    popup.add_command(label="Расставить корабли (F5)", command=self.setAndShowBoats)
                    popup.add_command(label="Спрятать/показать корабли (F6)", command=self.shipShowHide)
                    popup.add_separator()
                    popup.add_command(label="Alt+F4 - выход", command=window.destroy)
                    popup.post(e.x_root, e.y_root)

        else: # а это клик в игре
            if GameStatus != self.pl: # тычок в поле соперника
                if self.click(e.x, e.y) == 2:
                    GameStatus = GameStopped
                    messagebox.showinfo( "Игра окончена", "Выиграл {}".format(self.pl) )
        
    # --------------------------------------------------------------------------

    def click(self, x, y):
        global GameStatus
        
        it = self.canv.find_overlapping(x, y, x, y)
        boatHit, cell = False, ''

        for i in it:
            tags = self.canv.gettags(i)

            if 'field' in tags:
                if tags[1] in self.hitCells:
                    return -1

                cell, b, a = tags[1], ord(tags[1][:1])-64, int(tags[1][1:])

            if 'boat' in tags:  # если этот объект - лодка, то
                for sh in self.ships:  # надо найти его среди лодок !
                    if sh.item == i:
                        boatHit = True
                        sh.wounds.append( cell )
                        self.hitCells.append( cell )
                        self.moves +=1
                        self.decksQ -= 1
                        self.canv.create_rectangle(a * self.size, b * self.size, (a + 1) * self.size, (b + 1) * self.size,
                                                                                             tags=["field", cell], fill=col[2] )

                        if len(sh.wounds) == len(sh.cells): # убил...
                            for c in sh.cells:
                                b, a = ord(c[:1])-64, int(c[1:])
                                for i in range(b-1, b+2):
                                    for j in range(a-1, a+2):
                                        k = chr(i + 64) + str(j)
                                        if (k not in sh.cells) and (k not in self.hitCells) and (i in range(1,self.y+1)) and (j in range(1,self.x+1)):
                                            self.draw_cross(j, i)
                                            self.hitCells.append( k )

                        if not self.decksQ: # конец игре
                            return 2                        

                        return 1 # ранил
                    
        if not boatHit and len(cell): # мимо
            self.moves +=1
            self.hitCells.append( cell )
            self.draw_cross(a, b)

            if GameStatus == Player2:   # переход хода 
                GameStatus = Player1
            else:
                GameStatus = Player2
                
            self.canv.focus_set()
            return 0

    # --------------------------------------------------------------------------
        
    def getShot(self):

        w = a = b = 0
        
        # попробовать найти раненого и добить его
        for sh in self.ships:
            if len(sh.wounds) and len(sh.wounds) != len(sh.cells): # нашли раненного
                orient = False
                for k in sh.wounds:
                    b, a = ord(k[:1])-64, int(k[1:])

                    if not orient: # струляем только горизонталь
                        # пульнём влево                    
                        if (a-1) in range(1, self.x+1) and (chr(b+64)+str(a-1)) not in self.hitCells:
                            a -= 1
                            break
                        # пульнём вправо    
                        elif (a+1) in range(1, self.x+1) and (chr(b+64)+str(a+1)) not in self.hitCells:
                            a += 1
                            break
                        # влево-вправо не струляется
                        if (chr(b+64)+str(a-1)) not in sh.wounds and (chr(b+64)+str(a+1)) not in sh.wounds:
                            orient = not orient
                        
                    if orient:  # а тут только вертикаль
                        # пульнём вверх
                        if (b-1) in range(1, self.y+1) and (chr(b+63)+str(a)) not in self.hitCells:
                            b -= 1
                            break
                        # пульнём вниз
                        elif (b+1) in range(1, self.y+1) and (chr(b+65)+str(a)) not in self.hitCells:
                            b += 1                        
                            break
                        # вверх-вниз не стреляется
                        if (chr(b+63)+str(a)) not in sh.wounds and (chr(b+65)+str(a)) not in sh.wounds:
                            orient = not orient

                w=1
                break

        # не получилось с раненым - бьём наугад, закрыв глаза...
        while not w:
            a, b = random.randint(1, self.x), random.randint(1, self.y)
            if (chr(b + 64) + str(a)) not in self.hitCells:
                break

        return self.click(a*self.size+1, b*self.size+1)

    # ------смена типа игрока с ПК на чела и наоборот---------------------------
    def chType(self):
        if GameStatus == GameStopped:
            self.plType = int(not self.plType)
            self.im = PhotoImage(file=pic[self.plType])
            self.canv.itemconfig("pic", image=self.im)

    # ---------------------------------
    def onKeyPress(self, e):
        global GameStatus

        if e.keysym == "F5":
            self.setAndShowBoats()

        if e.keysym == "F6":
            self.shipShowHide()

        if e.keysym == "Escape":
            GameStatus = GameStopped

    # ---------------------------------
    def shipShowHide(self):
        if GameStatus == GameStopped:
            for sh in self.ships:
                sh.draw(not sh.visible)

    # ---------------------------------
    def setAndShowBoats(self):        
        if self.setBoats():
            self.draw()
            for sh in self.ships:
                sh.draw(True)        

# ---------------------конец класса игрового поля-----------------------------


# -------------------класс в котором всё окошко живёт--------------------
class Field(Frame):

    # ------------------------собственно конструктор класса-------------------------------------------------
    def __init__(self, master):
        self.lwin = self.rwin = 0
        self.aft = None        

        super().__init__(master)
        self.pack(fill='both', expand='yes')

        fr_top = Frame(self, bg=col[0], height=30, bd=10)
        fr_top.pack(fill='both', side = TOP)
        
        self.butt = Button(fr_top, text = but_txt[GameStatus], command = self.butt_click)
        self.butt.pack()        
        # fr_top.place(height=200, width= 500, anchor = 'c')

        fr_bot = Frame(self)
        fr_bot.pack(fill=BOTH, side = BOTTOM, expand=1)

        #---------------------------------------------
        fr_1m = Frame(fr_bot)
        fr_1m.pack(fill='both', side=LEFT, expand=1)

        fr_1u = Frame(fr_1m, bg=col[0], height=20, bd=10)
        fr_1u.pack(fill=BOTH, side=TOP)
        self.l1_Text = StringVar()
        self.l1_Text.set("Игрок № 1 ({})".format(self.lwin))
        self.l1 = Label(fr_1u, textvariable=self.l1_Text, bg=col[0])
        self.l1.pack()

        fr_1 = Frame(fr_1m, bg=col[0])
        fr_1.pack(fill=BOTH, side=BOTTOM, expand=1)

        self.c1 = Canvas(fr_1, bg=col[0], highlightcolor = col[2])
        self.c1.pack(fill='both', expand=1)
        self.left = BattleField(1, x, y, Player1, self.c1)
        #---------------------------------------------

        fr_2m = Frame(fr_bot)
        fr_2m.pack(fill='both', side=RIGHT, expand=1)

        fr_2u = Frame(fr_2m, bg=col[0], height=20, bd=10)
        fr_2u.pack(fill=BOTH, side=TOP)
        self.l2_Text = StringVar()
        self.l2_Text.set("Игрок № 2 ({})".format(self.rwin))
        self.l2 = Label(fr_2u, textvariable=self.l2_Text, bg=col[0])
        self.l2.pack()                
        
        fr_2 = Frame(fr_2m, bg=col[0])
        fr_2.pack(fill='both', side=BOTTOM, expand=1)

        self.c2 = Canvas(fr_2, bg=col[0], highlightcolor = col[2])
        self.c2.pack(fill='both', expand='yes')
        self.right = BattleField(1, x, y, Player2, self.c2)

        self.c1.bind("<Configure>", self.res)
        self.c1.focus_set()        

    # ----------------------------------------------------------------------------------------------------------
    def pc_move(self):
        global GameStatus

        if GameStatus == GameStopped:
            self.after_cancel(self.aft)
            self.aft = None
            self.butt.config(text = but_txt[GameStatus])
            return

        self.update()            
        
        i, mov = 1, 0
        
        if GameStatus == Player1 and self.left.plType : # ход левого ПК - стреляем в правого соперника
            self.left.canv.focus_set()
            while i == 1:
                i = self.right.getShot()
                
            mov = self.right.moves

        if GameStatus == Player2 and self.right.plType: # ход правого ПК - стреляем в левого соперника
            self.right.canv.focus_set()
            while i == 1:
                i = self.left.getShot()
                
            mov = self.left.moves

        if i == 2:
            if self.aft is not None :
                self.after_cancel(self.aft)
                self.aft = None

            print("Выиграл игрок № ", GameStatus, "за ", mov, " выстрелов")
            if GameStatus == Player1:
                self.lwin += 1
                self.l1_Text.set("Игрок № 1 ({})".format(self.lwin))
            else:
                self.rwin += 1
                self.l2_Text.set("Игрок № 2 ({})".format(self.rwin))
                
            GameStatus = GameStopped
            self.butt.config(text = but_txt[GameStatus])
            print()

            if self.left.plType and self.right.plType: # роботы дерутся бесконечно
                self.butt_click()
        else:
            self.aft = self.after(think_time, self.pc_move)

    #-----------   Game start/stop -------------------------------------------
    def butt_click(self):
        global GameStatus
        
        if GameStatus == GameStopped:
            GameStatus = random.randint( Player1, Player2 )
            self.c1.focus_set() if GameStatus == Player1 else self.c2.focus_set()
            print("Игра номер {}".format(self.lwin+self.rwin+1))
            print("Начинает игрок №", GameStatus)
            
            self.right.decksQ = self.left.decksQ = self.right.moves = self.left.moves = 0
            self.left.hitCells.clear()
            self.right.hitCells.clear()
            for sh in self.left.ships:
                sh.wounds.clear()
                self.left.decksQ += len(sh.cells)
                
            for sh in self.right.ships:
                sh.wounds.clear()
                self.right.decksQ += len(sh.cells)

            self.left.draw()
            self.right.draw()

            if self.right.plType or self.left.plType: # если хоть один из игроков - ПК, запускаем событие по таймеру
                self.aft = self.after_idle(self.pc_move)
            
        else:
            GameStatus = GameStopped
            if self.aft is not None :
                self.after_cancel(self.aft)
                self.aft = None

        self.butt.config(text = but_txt[GameStatus])

    # ---------------- реакция на изменение размеров окна-------------------
    def res(self, e):
        # вычисляем размеры клетки
        if e.width // self.left.x < e.height // self.left.y:
            self.right.size = self.left.size = (e.width / 1.03) // (self.left.x + 1)
        else:
            self.right.size = self.left.size = (e.height / 1.03) // (self.left.y + 1)

        # и перерисовываем левое и правое игровые поля
        self.left.draw()
        self.right.draw()
    # ----------------------------------------------------------------------


# -------конец класса окна---------------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed()  # запуск рандомайзера

    GameStatus = GameStopped

    window = Tk()
    window.title("Морской бой")

    # window.geometry("800x600+{}+{}".format((window.winfo_screenwidth()-800)//2,(window.winfo_screenheight()-600)//2))
    window.minsize(width=800, height=600)
    window.update_idletasks()

    app = Field(window)

    window.mainloop()
