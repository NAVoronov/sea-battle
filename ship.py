from var import *

class Ship:
    #------------------------------------------------------------------------------------------
    def __init__(self, decks, orient, can):

        self.decks = decks
        self.orient = orient
        self.cells = []
        self.canv = can
        self.item = None
        self.visible = False
        self.wounds = []

    #------------------------------------------------------------------------------------------
    def draw(self, vis):

        if len(self.cells):

            coords, size = [], 0

            for cell in self.cells:
                item = self.canv.find_withtag(cell)  # нашли клетку на игровом поле
                k = self.canv.bbox(item[0])  # стащили её координаты, потом ниже по ним выстроим корабль
                coords.append((k[0]+1, k[1]+1, k[2]-1, k[1]+1, k[2]-1, k[3]-1, k[0]+1, k[3]-1, k[0]+1, k[1]+1))
                if not size:
                    size = k[2]-k[0]-2

            if self.item is not None:
                self.canv.delete(self.item)

            self.visible = vis
            self.item = self.canv.create_polygon(coords, fill=col[self.visible], activefill=af[bool(self.visible)], 
                                                                                          outline="black", tag="boat")
            for cell in self.wounds:
                b, a = ord(cell[:1])-64, int(cell[1:])
                self.canv.create_rectangle(a * size, b * size, (a+1) * size, (b+1) * size, tags=["field", cell], fill=col[2] )
    #------------------------------------------------------------------------------------------