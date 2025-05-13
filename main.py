# Module Imports
import pygame
import random
import data

# Module Init
pygame.init()

# Game Assets and Objects
class Ship:
    def __init__(self,name,img,pos,size):
        """Khởi tạo đối tượng ship

        Args:
            name: Tên 
            img : Ảnh
            pos : Vị trí 
            size: Kích cỡ
        """
        self.name=name
        self.pos = pos
        # Load ảnh dọc
        self.vImage = loadImage(img,size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect()
        self.vImageRect.topleft = pos 
        # Load ảnh ngang
        self.hImage = pygame.transform.rotate(self.vImage,-90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = pos
        # Image and Rectangle
        self.image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        # Chọn ship
        self.active = False
        
    def SelectAndMove(self):
        """Chọn Ship và di chuyển theo con trỏ chuột"""
        while self.active==True:
            self.rect.center = pygame.mouse.get_pos()
            updateGameScreen(GAMESCREEN,GAMESTAGE)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.checkForCollisons(pFleet): 
                        if event.button == 1: # Nếu nhấn chuột trái thì di chuyển tàu
                            self.hImageRect.center = self.vImageRect.center = self.rect.center
                            self.active = False
                            
                    if event.button == 3: # Nếu nhấn chuột phải thì xoay tàu
                        self.rotateShip()
        
    def rotateShip(self,rotate=False):  
        """Xoay ship ngang và dọc"""     
        if self.active or rotate == True:
            if self.rotation == False:
                self.rotation = True
            else:
                self.rotation = False
        self.switchAndRect()
        
    def switchAndRect(self):
        """Chuyển ngang sang dọc và lấy hình chữ nhật của ship"""
        if self.rotation == True:
            self.image = self.hImage
            self.rect = self.hImageRect
        else:
            self.image = self.vImage
            self.rect = self.vImageRect
        self.hImageRect.center = self.vImageRect.center = self.rect.center
          
    def checkForCollisons(self,shiplist):
        """Kiểm tra các ship không đụng nhau"""
        slist=shiplist.copy()
        slist.remove(self) 
        for item in slist:
            if self.rect.colliderect(item.rect):
                return True
        return False
    
    def checkForRotateCollisions(self, shiplist):
        """Kiểm tra các thuyền không đụng nhau trước khi xoay"""
        slist = shiplist.copy()
        slist.remove(self)
        for ship in slist:
            if self.rotation == True:
                if self.vImageRect.colliderect(ship.rect):
                    return True
            else:
                if self.hImageRect.colliderect(ship.rect):
                    return True
        return False
        
    def returnToDefaultPosition(self):
        """Đưa các thuyền về vị trí ban đầu"""
        if self.rotation == True:
            self.rotateShip(True)
            
        self.rect.topleft = self.pos
        self.hImageRect.center = self.vImageRect.center = self.rect.center
        
    def snapToGridEdge(self,gridCoords):
        """Ship tự động tra vào lưới khi đưa gần sát vào lưới và thả ra"""
        if self.rect.topleft != self.pos:
            
            # check if ship pos outside the grid
            if self.rect.left > gridCoords[0][-1][0]+50 or \
                self.rect.right < gridCoords[0][0][0] or \
                self.rect.top > gridCoords[-1][0][1] +50 or \
                self.rect.bottom < gridCoords[0][0][1]:
                    self.returnToDefaultPosition()

            elif self.rect.right > gridCoords[0][-1][0] + 50:
                self.rect.right = gridCoords[0][-1][0] + 50
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + 50 :
                self.rect.bottom = gridCoords[-1][0][1] +50
            self.vImageRect.center = self.hImageRect.center=self.rect.center
    
    def snapToGrid(self,gridCoords):
        """Tìm ô gần nhất và tự tra Ship vào ô"""
        for row in gridCoords:
            for cell in row:
                if self.rect.left >= cell[0] and self.rect.left < cell[0] + CELLSIZE \
                    and self.rect.top >=cell[1] and self.rect.top < cell[1] + CELLSIZE:
                    if self.rotation == False:
                        self.rect.topleft = (cell[0] + (CELLSIZE - self.image.get_width())//2,cell[1])
                    else:
                        self.rect.topleft = (cell[0],cell[1]+(CELLSIZE-self.image.get_height())//2)
                    
        self.hImageRect.center = self.vImageRect.center = self.rect.center
        
    def draw(self,window):
        """Vẽ Ship lên màn hình"""
        # draw to screen:
        window.blit(self.image,self.rect)
      
class Button:
    def __init__(self,img,size,pos,msg):
        """Khởi tạo những thuộc tính của button

        Args:
            img (_type_): Ảnh
            size (_type_): Kích cỡ
            pos (_type_): Vị trí
            msg (_type_): Message của button
        """
        self.name=msg
        self.image=img
        self.imageLarger=self.image
        self.imageLarger=pygame.transform.scale(self.imageLarger,(size[0]+10,size[1]+10)) # Khi di chuột vào thì nút sẽ phóng to
        self.rect=self.image.get_rect()
        self.rect.topleft=pos
        self.radarUsed = 0
        self.active = False
          
        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.rect.center)
    
    def addText(self,msg):
        """Định dạng chữ

        Args:
            msg (_type_): message

        Returns:
            trả về font chữ và kích cỡ
        """
        font = pygame.font.SysFont('Stencil',18)
        message = font.render(msg,1,(255,255,255))
        return message
    
    def focusOnButton(self,window):
        """Cho biết nút nào đang được chọn"""
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            current_image = self.imageLarger
            current_rect = self.imageLarger.get_rect(center=self.rect.center)
        else:
            current_image = self.image
            current_rect = self.rect

        window.blit(current_image, current_rect)
        self.msgRect.center = current_rect.center
            
    def actionOnPress(self):
        """Hành động sẽ xảy ra nếu nhấn vào các nút"""
        if self.name == 'Randomize':
            self.randomizeShipPos(pFleet,pGameGrid)
            self.randomizeShipPos(cFleet,cGameGrid)
        elif self.name == 'Reset':
            self.reset(pFleet)
        elif self.name == 'Start':
            self.startPhase(START)
        elif self.name == 'Quit':
            pass
        elif self.name == 'Again':
            self.restartGame()
            
    def randomizeShipPos(self,shiplist,gameGrid):
        """Gọi hàm đặt thuyền ngẫu nhiên"""
        if START == True:
            randomShipPos(shiplist,gameGrid) 
        
    def reset(self,shiplist):
        """Đặt lại thuyền ở vị trí ban đầu"""
        if START == True:
            for ship in shiplist:
                ship.returnToDefaultPosition()
     
    def startPhase(self,start):
        pass
    
    def restartGame(self):
        TOKENS.clear()
        self.reset(pFleet)
        self.randomizeShipPos(cFleet,cGameGrid)
        updateGameLogic(cGameGrid,cFleet,cGameLogic)
        updateGameLogic(pGameGrid,pFleet,pGameLogic)  
        
    def updateButtons(self,gameStatus):
        """Update nút với mỗi trạng thái của trò chơi"""
        if self.name == 'Start' and gameStatus == False:
            self.name = 'Again'
        elif self.name == 'Again' and gameStatus == True:
            self.name= 'Start'
        
        if self.name == 'Reset' and gameStatus== False:
            self.name='Hint'
        elif self.name=='Hint' and gameStatus== True:
            self.name='Reset'
            
        if self.name=='Randomize' and gameStatus == False:
            self.name = 'Quit'
        elif self.name=='Quit' and gameStatus == True:
            self.name='Randomize'
            
            
        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)    

    def draw(self,window):
        """Vẽ nút"""
        self.updateButtons(START)
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)
    
class Player:
    def __init__(self):
        """Thuộc tính của người chơi là đến lượt hay chưa"""
        self.turn = True
    
    def makeAttack(self,grid,logicgrid):
        """Khi đến lượt, người chơi thực hiện tấn công vào 1 ô của computer grid"""
        X,Y=pygame.mouse.get_pos()
        if X>=grid[0][0][0] and X<=grid[0][-1][0]+50 and \
            Y>=grid[0][0][1] and Y<=grid[-1][0][1]+50:
                for i,rowX in enumerate(grid):
                    for j,colX in enumerate(rowX):
                        if X>=colX[0] and X<=colX[0]+50 and \
                            Y>=colX[1] and Y<=colX[1]+50:
                                if logicgrid[i][j] != ' ':
                                    if logicgrid[i][j] == 'O':
                                        print('Hit')
                                        TOKENS.append(Tokens(FIRE,grid[i][j],'HIT',None))
                                        logicgrid[i][j]='T'
                                        self.turn=False
                                else:   
                                    logicgrid[i][j]='X'
                                    print('Miss')
                                    TOKENS.append(Tokens(WATER,grid[i][j],'Miss',None))
                                    self.turn= False
    
class EasyComputer:
    def __init__(self):
        """Thuộc tính của mức độ Dễ"""
        self.turn = False
        self.status = self.computerStatus('Thinking')
        self.name = 'Easy'


    def computerStatus(self, msg):
        """Định dạng chữ của dòng trạng thái Thinking"""
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message


    def makeAttack(self, gamelogic):
        """Máy tính thực hiện bắn ngẫu nhiên vào 1 ô của người chơi"""
        COMPTURNTIMER = pygame.time.get_ticks()
        if COMPTURNTIMER - TURNTIMER >= 3000:
            validChoice = False
            while not validChoice:
                rowX = random.randint(0, 9)
                colX = random.randint(0, 9)

                if gamelogic[rowX][colX] == ' ' or gamelogic[rowX][colX] == 'O':
                    validChoice = True

            if gamelogic[rowX][colX] == 'O':
                TOKENS.append(Tokens(FIRE, pGameGrid[rowX][colX], 'Hit', None))
                gamelogic[rowX][colX] = 'T'
                self.turn = False
            else:
                gamelogic[rowX][colX] = 'X'
                TOKENS.append(Tokens(WATER, pGameGrid[rowX][colX], 'Miss', None))
                self.turn = False
        return self.turn


    def draw(self, window):
        if self.turn:
            window.blit(self.status, (cGameGrid[0][0][0] - CELLSIZE, cGameGrid[-1][-1][1] + CELLSIZE))
   
class HardComputer(EasyComputer):
    def __init__(self):
        """Khởi tạo mức độ Khó, kế thừa từ Easy"""
        super().__init__()
        self.moves = []


    def makeAttack(self, gamelogic):
        """Bắn ngẫu nhiên cho đến khi trúng, rồi thực hiện bắn các ô liền kề"""
        if len(self.moves) == 0:
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 3000:
                validChoice = False
                while not validChoice:
                    rowX = random.randint(0, 9)
                    rowY = random.randint(0, 9)

                    if gamelogic[rowX][rowY] == ' ' or gamelogic[rowX][rowY] == 'O':
                        validChoice = True

                if gamelogic[rowX][rowY] == 'O':
                    TOKENS.append(
                        Tokens(FIRE, pGameGrid[rowX][rowY], 'Hit', None,None, None))
                    gamelogic[rowX][rowY] = 'T'
                    self.generateMoves((rowX, rowY), gamelogic)
                    self.turn = False
                else:
                    gamelogic[rowX][rowY] = 'X'
                    TOKENS.append(Tokens(WATER, pGameGrid[rowX][rowY], 'Miss', None, None, None))
                    self.turn = False

        elif len(self.moves) > 0:
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 2000:
                rowX, rowY = self.moves[0]
                TOKENS.append(Tokens(FIRE, pGameGrid[rowX][rowY], 'Hit', None,None, None))
                gamelogic[rowX][rowY] = 'T'
                self.moves.remove((rowX, rowY))
                self.turn = False
        return self.turn


    def generateMoves(self, coords, grid, lstDir=None):
        x, y = coords
        nx, ny = 0, 0
        for direction in ['Up', 'Down', 'Right', 'Left']:
            if direction == 'Up' and lstDir != 'Up':
                nx = x - 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'Down')

            if direction == 'Down' and lstDir != 'Down':
                nx = x + 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'Up')

            if direction == 'Right' and lstDir != 'Right':
                nx = x
                ny = y + 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'Left')

            if direction == 'Left' and lstDir != 'Left':
                nx = x
                ny = y - 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'Right')

        return
                                                   
class Tokens:
    def __init__(self,image,pos,action,imageList=None):
        """Khởi tạo các thuộc tính của Token, bao gồm image,vị trí, hành động"""
        self.image=image
        self.rect=self.image.get_rect()
        self.pos=pos
        self.rect.topleft=self.pos
        self.imageList=imageList
        self.action=action
        self.timer=pygame.time.get_ticks()
        self.imageIndex=0
        
    def draw(self,window):
        # draw the token
        if not self.imageList:
            window.blit(self.image,self.rect)
        else:
            self.image = self.animate_Explosion()
            self.rect[1]=self.pos[1]-10
            window.blit(self.image,self.rect)
    
# Game Ultility Functions

def createGameGrid(rows,cols,cellsize,pos):
    """Tạo lưới trò chơi với tọa độ cho mỗi lưới"""
    startX=pos[0]
    startY=pos[1]
    coordGrid=[]
    for row in range(rows):
        rowX=[]
        for col in range(cols):
            rowX.append((startX,startY))
            startX+=cellsize
        coordGrid.append(rowX)
        startX=pos[0]
        startY+=cellsize
    return coordGrid

def creategameLogic(rows,cols):
    """Tạo logic game, thêm space vào lưới"""
    # Updates
    gamelogic=[]
    for row in range(rows):
        rowX=[]
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic

def updateGameLogic(coordGrid,shiplist,gamelogic):
    """Update thêm logic với vị trí của Ship, đặt là X"""
    for i,row in enumerate(coordGrid):
        for j,col in enumerate(row):
            if gamelogic[i][j] == 'T' or gamelogic[i][j] == 'X':
                continue
            else:
                gamelogic[i][j] = ' '
                for ship in shiplist:
                    if pygame.rect.Rect(col[0],col[1],CELLSIZE,CELLSIZE).colliderect(ship.rect):
                        gamelogic[i][j]= 'O'
                    
def showGrid(window,cellsize, playerGrid,computerGrid):
    """Vẽ lưới của người chơi và máy tính lên màn hình"""
    gamegrids=[playerGrid,computerGrid]
    for grid in gamegrids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window,(255,255,255),(col[0],col[1],cellsize,cellsize),1)

def printgamelogic():
    """in logic game vào terminal"""
    print('Player Grid'.center(50,'#'))
    for _ in pGameLogic:
        print(_)
    print('Computer Grid'.center(50,'#'))
    for _ in cGameLogic:
        print(_)

def loadImage(path,size,rotate=False):
    """Hàm load ảnh vào bộ nhớ"""
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img,size)
    if rotate==True:
        img = pygame.transform.rotate(img,-90)
    return img

def loadAnimationImages(path, aniNum,  size):
    """Hàm load ảnh động vào bộ nhớ bằng cách load nhiều ảnh"""
    imageList = []
    for num in range(aniNum):
        if num < 10:
            imageList.append(loadImage(f'{path}00{num}.png', size))
        elif num < 100:
            imageList.append(loadImage(f'{path}0{num}.png', size))
        else:
            imageList.append(loadImage(f'{path}{num}.png', size))
    return imageList

def increaseAnimationImage(imageList, ind):
    return imageList[ind]

def createFleet():
    """Tạo danh sách các ship"""
    fleet=[]
    for name in FLEET.keys():
        fleet.append(
            Ship(name,
                 FLEET[name][1],
                 FLEET[name][2],
                 FLEET[name][3])
        )
    return fleet

def sortFleet(ship, shiplist):
    """Sắp xếp lại danh sách ships"""
    shiplist.remove(ship)
    shiplist.append(ship)
 
def randomShipPos(shiplist,gamegrid):
    """Hàm random ship vào lưới"""
    # select random pos for ships
    placedships=[]
    for i,ship in enumerate(shiplist):
        validpos = False   
        while validpos == False:
            ship.returnToDefaultPosition()
            rotateShip=random.choice([True,False])
            if rotateShip == True:
                x = random.randint(0,9)
                y = random.randint(0,9 - (ship.hImage.get_width()//50))
                ship.rotateShip(True)
                ship.rect.topleft = gamegrid[y][x]
            else:
                y = random.randint(0,9-(ship.vImage.get_height()//50))
                x = random.randint(0,9)
                ship.rect.topleft = gamegrid[y][x]
                
            if len(placedships) > 0:
                for i in placedships:
                    if ship.rect.colliderect(i.rect):
                        validpos = False
                        break
                    else:
                        validpos = True
            else:
                validpos = True
        placedships.append(ship)
 
def startPhase(start):
    if start == True:
        return False
    else: 
        return True

def pickRandomShip(gamelogic):
    """Hàm chọn ship ngẫu nhiên"""
    validChoice = False
    while not validChoice:
        X=random.randint(0,9)
        Y=random.randint(0,9)
        if gamelogic[X][Y] == 'O':
            validChoice = True
    return (X,Y)

def displayRadarScanner(imagelist, indnum, SCAN):
    """Hàm hiển thị radar scan với 360 ảnh"""
    if SCAN == True and indnum <= 359:
        image = increaseAnimationImage(imagelist, indnum)
        return image
    else:
        return False
    
def displayRadarBlip(num, position):
    """Hàm hiển thị nút hint của radar"""
    if SCAN:
        image = None
        if position[0] >= 5 and position[1] >= 5:
            if num >= 0 and num <= 90:
                image = increaseAnimationImage(RADARBLIPIMAGES, num // 10)
        elif position[0] < 5 and position[1] >= 5:
            if num > 270 and num <= 360:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 4) // 10)
        elif position[0] < 5 and position[1] < 5:
            if num > 180 and num <= 270:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 3) // 10)
        elif position[0] >= 5 and position[1] < 5:
            if num > 90 and num <= 180:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 2) // 10)
        return image
         
def takeTurn(p1,p2):
    """Phân chia lượt chơi"""
    if p1.turn == True:
        p2.turn = False
    else:
        p2.turn = True
        if not p2.makeAttack(pGameLogic):
            p1.turn=True
  
def checkForWinners(grid):
    """Kiểm tra người thắng"""
    validGame = True
    for row in grid:
        if 'O' in row:
            validGame = False
    return validGame
 
def MenuScreen(window):
    """Màn hình Menu"""
    window.fill((0, 0, 0))
    window.blit(BACKGROUND, (0, 0))
    window.blit(MAINMENUIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Easy', 'Hard','View Stats']:
            button.active = True
            button.draw(window)
        else:
            button.active = False
        
def startScreen(window):
    """Màn hình Start của trò chơi"""
    window.fill((0,0,0))
    
    # Draw Grid
    window.blit(BACKGROUND, (0, 0))
    showGrid(window,CELLSIZE,pGameGrid,cGameGrid)
    window.blit(PGAMEGRID, (0, 0))
    window.blit(CGAMEGRID, (cGameGrid[0][0][0] - 50, cGameGrid[0][0][1] - 50))
    
    # Draw ships
    for ship in pFleet:
        ship.draw(window)  
        ship.snapToGridEdge(pGameGrid)
        ship.snapToGrid(pGameGrid)
        
    for ship in cFleet:
        # ship.draw(window)
        ship.snapToGridEdge(cGameGrid)
        ship.snapToGrid(pGameGrid)
        
    for button in BUTTONS:
        if button.name in ['Randomize', 'Reset', 'Start', 'Quit', 'Hint', 'Again']:
            button.active = True
            button.draw(window)
        else:
            button.active = False
    
    computer.draw(window)

    for token in TOKENS:
        token.draw(window)

    radarScan = displayRadarScanner(RADARGRIDIMAGES, INDNUM, SCAN)
    if not radarScan:
        pass
    else:
        window.blit(radarScan, (cGameGrid[0][0][0], cGameGrid[0][-1][1]))

    RBlip = displayRadarBlip(INDNUM, BLITPOS)
    if RBlip:
        window.blit(RBlip, (cGameGrid[BLITPOS[0]][BLITPOS[1]][0],
                            cGameGrid[BLITPOS[0]][BLITPOS[1]][1]))

    updateGameLogic(pGameGrid,pFleet,pGameLogic)
    updateGameLogic(cGameGrid,cFleet,cGameLogic)

def endScreen(window):
    """Màn hình kết thúc"""
    window.fill((0, 0, 0))
    window.blit(ENDSCREENIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Easy', 'Hard', 'Quit']:
            button.active = True
            button.draw(window)
        else:
            button.active = False
   
def updateGameScreen(window, GAMESTAGE):
    """Hiển thị màn hình theo biến trạng thái Game"""
    if GAMESTAGE == 'Menu':
        MenuScreen(window)
    elif GAMESTAGE == 'Start':
        startScreen(window)
    elif GAMESTAGE == 'Game Over':
        endScreen(window)
        
    pygame.display.update()
    
# Game setting and Variables 
SCREENWITDTH=1260
SCREENHEIGHT=960
ROWS=10
COLS=10
CELLSIZE=50
START = True
SCAN = False
BLITPOS = None
INDNUM = 0
TURNTIMER = pygame.time.get_ticks()
GAMESTAGE = 'Menu'
DIFFICULTY = None

# Pygame Display Initialization
GAMESCREEN = pygame.display.set_mode((SCREENWITDTH,SCREENHEIGHT))
pygame.display.set_caption('Battle Ship')

# Game Sounds and Images
BUTTONIMG = loadImage('battle_ship/img/button/button.png',(150,50))
BUTTONIMG1 = loadImage('battle_ship/img/button/button.png',(250,100))
BUTTONS= [
    Button(BUTTONIMG,(150,50),(25,850),'Randomize'),
    Button(BUTTONIMG,(150,50),(200,850),'Reset'),
    Button(BUTTONIMG,(150,50),(375,850),'Start'),
    Button(BUTTONIMG1, (300, 150), (900, SCREENHEIGHT // 2 - 200), 'Easy'),
    Button(BUTTONIMG1, (300, 150), (900, SCREENHEIGHT // 2 - 50), 'Hard'),
]
RADARGRIDIMAGES = loadAnimationImages('battle_ship/img/radar/radar_anim', 360, (ROWS * CELLSIZE, COLS * CELLSIZE))
RADARBLIPIMAGES = loadAnimationImages('battle_ship/img/Blip/Blip_', 11, (50, 50))
WATER=loadImage('battle_ship/img/token/water.png',(CELLSIZE,CELLSIZE))
FIRE=loadImage('battle_ship/img/token/fire.png',(CELLSIZE,CELLSIZE))
TOKENS=[]
MAINMENUIMAGE = loadImage('battle_ship/img/background/battleship.jpg', (SCREENWITDTH // 3 * 2, SCREENHEIGHT))
ENDSCREENIMAGE = loadImage('battle_ship/img/background/background.jpg',(SCREENWITDTH,SCREENHEIGHT))
BACKGROUND = loadImage('battle_ship/img/background/backgroundpink.jpg',(SCREENWITDTH,SCREENHEIGHT))
PGAMEGRID = loadImage('battle_ship/img/grid/grid.png', ((ROWS+1) * CELLSIZE, (COLS+1) * CELLSIZE))
CGAMEGRID = loadImage('battle_ship/img/grid/grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))


# Game Lists/Dictionaries

FLEET = {
    'boat1': ['boat1','battle_ship/img/ship/boat1.png',(40,600),(45,195)],
    'boat2': ['boat2','battle_ship/img/ship/boat2.png',(125,600),(45,195)],
    'boat3': ['boat3','battle_ship/img/ship/boat3.png',(200,600),(45,95)],
    'boat4': ['boat4','battle_ship/img/ship/boat4.png',(275,600),(45,145)]
        }

STAGE = ['Menu', 'Start', 'Game Over','Database']

# Loading Game Variables
pGameGrid= createGameGrid(ROWS,COLS,CELLSIZE,(50,50))
pGameLogic= creategameLogic(ROWS,COLS)
pFleet = createFleet()

cGameGrid= createGameGrid(ROWS,COLS,CELLSIZE,(SCREENWITDTH - (ROWS*CELLSIZE),50))
cGameLogic= creategameLogic(ROWS,COLS)
cFleet = createFleet()
randomShipPos(cFleet,cGameGrid)

printgamelogic()

# Players
player1=Player()
computer=EasyComputer()

# Main Game Loop
RUNGAME = True
while RUNGAME:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if START == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()):
                            ship.active = True
                            sortFleet(ship, pFleet)
                            ship.SelectAndMove()

                else:
                    if player1.turn == True:
                        player1.makeAttack(cGameGrid, cGameLogic)
                        if player1.turn == False:
                            TURNTIMER = pygame.time.get_ticks()

                for button in BUTTONS:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        if button.name == 'Start' and button.active == True:
                            status = startPhase(START)
                            START = status
                        elif button.name == 'Again' and button.active == True:
                            status = startPhase(START)
                            START = status
                        elif button.name == 'Quit' and button.active == True:
                            RUNGAME = False
                        elif button.name == 'Hint' and button.active == True:
                            SCAN = True
                            INDNUM = 0
                            BLITPOS = pickRandomShip(cGameLogic)      
                        elif (button.name == 'Easy' or button.name == 'Hard') and button.active == True:
                            if button.name == 'Easy':
                                computer = EasyComputer()
                                DIFFICULTY = 'Easy'
                            elif button.name == 'Hard':
                                computer = HardComputer()
                                DIFFICULTY = 'Hard'
                            if GAMESTAGE == 'Game Over':
                                TOKENS.clear()
                                for ship in pFleet:
                                    ship.returnToDefaultPosition()
                                randomShipPos(cFleet, cGameGrid)
                                pGameLogic = creategameLogic(ROWS, COLS)
                                updateGameLogic(pGameGrid, pFleet, pGameLogic)
                                cGameLogic = creategameLogic(ROWS, COLS)
                                updateGameLogic(cGameGrid, cFleet, cGameLogic)
                                status = startPhase(START)
                                START = status
                        GAMESTAGE = STAGE[1]
                        button.actionOnPress()


            elif event.button == 2:
                printgamelogic()


            elif event.button == 3:
                if START == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()) and not ship.checkForRotateCollisions(pFleet):
                            ship.rotateShip(True)

    updateGameScreen(GAMESCREEN, GAMESTAGE)
    if SCAN == True:
        INDNUM += 1

    if GAMESTAGE == 'Start' and START != True:
        player1Wins = checkForWinners(cGameLogic)
        computerWins = checkForWinners(pGameLogic)
        if player1Wins == True or computerWins == True:
            if player1Wins == True:
                data.add_game_result('WIN',DIFFICULTY)
            else:
                data.add_game_result('LOSE',DIFFICULTY)
            GAMESTAGE = STAGE[2]



    takeTurn(player1, computer)
    
pygame.quit()
    