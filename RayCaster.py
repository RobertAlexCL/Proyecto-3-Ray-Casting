import pygame as pg
#import pygame.gfxdraw as gfx


from math import cos, sin, pi, trunc

from pygame.constants import K_DOWN, SWSURFACE

RAY_AMOUNT = 60
WHITE = pg.Color('white')
BLACK = pg.Color('black')
GRAY = pg.Color("gray")
SADDLEBROWN = pg.Color("saddlebrown")
DIMGRAY = pg.Color("dimgray")
PAUSE = False

wallcolors = {
    '1': pg.Color('red'),
    '2': pg.Color('green'),
    '3': pg.Color('blue'),
    '4': pg.Color('yellow'),
    '5': pg.Color('purple')
    }

wallTextures = {
    '1': pg.image.load('wall1.png'),
    '2': pg.image.load('wall2.png'),
    '3': pg.image.load('wall3.png'),
    '4': pg.image.load('wall4.png'),
    '5': pg.image.load('wall5.png'),
    ' ':pg.image.load('blank.png')
    }


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.blocksize = 50
        self.wallheight = 50

        self.maxdistance = 300

        self.stepSize = 5
        self.turnSize = 5

        self.player = {
           'x' : 100,
           'y' : 175,
           'fov': 60,
           'angle': 0 }


    def load_map(self, filename):
        with open(filename) as file:
            if len(self.map) > 0:
                self.map = []
            for line in file.readlines():
                self.map.append( list(line.rstrip()) )

    def drawBlock(self, x, y, id, scale):
        tex = wallTextures[id]
        tex = pg.transform.scale(tex, (self.blocksize*scale, self.blocksize*scale) )
        rect = tex.get_rect()
        rect = rect.move((x,y))
        self.screen.blit(tex, rect)


    def drawPlayerIcon(self, color, offsetx = 0, minimapScale = 1):
        self.screen.fill(color, (offsetx+(self.player['x'] - 2)*minimapScale, (self.player['y'] - 2)*minimapScale, 5,5))

    def castRay(self, angle):
        rads = angle * pi / 180
        dist = 0
        stepSize = 2
        stepX = stepSize * cos(rads)
        stepY = stepSize * sin(rads)

        playerPos = (self.player['x'],self.player['y'] )

        x = playerPos[0]
        y = playerPos[1]
        
        while True:   

            x += stepX
            y += stepY

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if j < len(self.map):
                if i < len(self.map[j]):
                    if self.map[j][i] != ' ':

                        hitX = x - i*self.blocksize
                        hitY = y - j*self.blocksize

                        hit = 0

                        if 1 < hitX < self.blocksize-1:
                            if hitY < 1:
                                hit = self.blocksize - hitX
                            elif hitY >= self.blocksize-1:
                                hit = hitX
                        elif 1 < hitY < self.blocksize-1:
                            if hitX < 1:
                                hit = hitY
                            elif hitX >= self.blocksize-1:
                                hit = self.blocksize - hitY

                        tx = hit / self.blocksize
                        #pg.draw.line(self.screen, WHITE, playerPos, (x,y))
                        
                        return dist, self.map[j][i], tx
            dist += stepSize


    def render(self):
        halfHeight = int(self.height / 2)
        minimapOff = int(self.width/4*3)

        


        rayWidth = int(( 1 / RAY_AMOUNT) * self.width)
        h_precalc = self.height * self.wallheight
        for column in range(RAY_AMOUNT):
            angle = self.player['angle'] - (self.player['fov'] / 2) + (self.player['fov'] * column / RAY_AMOUNT)
            dist, id, tx = self.castRay(angle)


            startX = int(0 + column*rayWidth)

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle)) * wallHeight
            h = h_precalc / (dist * cos( (angle - self.player["angle"]) * pi / 180)) 
            startY = int(halfHeight - h/2)

            color_k = (1 - min(1, dist / self.maxdistance)) * 255

            tex = wallTextures[id]
            tex = pg.transform.scale(tex, (tex.get_width() * rayWidth, int(h)))
            tex.fill((color_k,color_k,color_k), special_flags=pg.BLEND_MULT)
            tx = int(tx * tex.get_width())
            self.screen.blit(tex, (startX, startY), (tx,0,rayWidth,tex.get_height()))
        
        #minimapa
        for j in range(len(self.map)):
            for i in range(len(self.map[j])):
                x = j*self.blocksize*0.25+minimapOff
                y = i*self.blocksize*0.25
                self.drawBlock(x, y, self.map[i][j], 0.25)
        self.drawPlayerIcon(BLACK, minimapOff, minimapScale=0.25)

width = 500
height = 500
selectedLevel = 'level1.txt'
pg.init()
screen = pg.display.set_mode((width,height), pg.DOUBLEBUF | pg.HWACCEL )
screen.set_alpha(None)

menuRunning = True
isRunning = True
restart = True
def rungame():
    global PAUSE
    global restart
    global isRunning
    global menuRunning
    restart = False
    

    rCaster = Raycaster(screen)
    rCaster.load_map(selectedLevel)


    clock = pg.time.Clock()
    font = pg.font.SysFont("Arial", 25)
    restartfont = pg.font.SysFont("Arial", 25)
    quitfont = pg.font.SysFont("Arial", 25)
    restartfont.set_bold(True)
    restartfont.set_underline(True)

    pauseTitle = pg.font.SysFont("Arial", 45).render('Pause', 1, WHITE)
    restartdisp = restartfont.render('Restart', 1, WHITE)
    quitdisp = quitfont.render('Quit', 1, WHITE)
    button_state = False

    def updateFPS():
        fps = str(int(clock.get_fps()))
        fps = font.render(fps, 1, WHITE)
        return fps
    newX = rCaster.player['x']
    newY = rCaster.player['y']
    while isRunning:

        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                isRunning = False

            elif ev.type == pg.KEYDOWN:
                
                forward = rCaster.player['angle'] * pi / 180
                right = (rCaster.player['angle'] + 90) * pi / 180

                if ev.key == pg.K_ESCAPE:
                    isRunning = False
                elif ev.key == pg.K_w or (PAUSE and (ev.key == pg.K_UP or ev.key == pg.K_DOLLAR)):
                    if PAUSE:
                        restartfont.set_bold(button_state)
                        restartfont.set_underline(button_state)
                        button_state = button_state == False
                        quitfont.set_bold(button_state)
                        quitfont.set_underline(button_state)

                        restartdisp = restartfont.render('Restart', 1, WHITE)
                        quitdisp = quitfont.render('Quit', 1, WHITE)
                    else:
                        newX += cos(forward) * rCaster.stepSize
                        newY += sin(forward) * rCaster.stepSize
                elif ev.key == pg.K_s:
                    if PAUSE:
                        restartfont.set_bold(button_state)
                        restartfont.set_underline(button_state)
                        button_state = button_state == False
                        quitfont.set_bold(button_state)
                        quitfont.set_underline(button_state)

                        restartdisp = restartfont.render('Restart', 1, WHITE)
                        quitdisp = quitfont.render('Quit', 1, WHITE)
                    else:
                        newX -= cos(forward) * rCaster.stepSize
                        newY -= sin(forward) * rCaster.stepSize
                elif ev.key == pg.K_a and not(PAUSE):
                    newX -= cos(right) * rCaster.stepSize
                    newY -= sin(right) * rCaster.stepSize
                elif ev.key == pg.K_d and not(PAUSE):
                    newX += cos(right) * rCaster.stepSize
                    newY += sin(right) * rCaster.stepSize
                elif ev.key == pg.K_q and not(PAUSE):
                    rCaster.player['angle'] -= rCaster.turnSize
                elif ev.key == pg.K_e and not(PAUSE):
                    rCaster.player['angle'] += rCaster.turnSize
                elif ev.key == pg.K_p:
                    PAUSE = PAUSE == False
                elif ev.key == pg.K_RETURN and PAUSE:
                    isRunning = False
                    PAUSE = False
                    if not(button_state):
                        restart = True
                        menuRunning = True

                
                    

        if not(PAUSE):
            i = int(newX/rCaster.blocksize)
            j = int(newY/rCaster.blocksize)
            if rCaster.map[j][i] == ' ':
                rCaster.player['x'] = newX
                rCaster.player['y'] = newY
            screen.fill(GRAY)

            # Techo
            screen.fill(SADDLEBROWN, (0, 0,  width, int(height / 2)))

            # Piso
            screen.fill(DIMGRAY, (0, int(height / 2),  width, int(height / 2)))

        
            rCaster.render()
            #FPS
            screen.fill(BLACK, (0,0,30,30) )
            screen.blit(updateFPS(), (0,0))
            clock.tick(60)
        if PAUSE:
            screen.fill(BLACK)
            screen.blit(pauseTitle, (100, 100))
            screen.blit(restartdisp, (300, 120))
            screen.blit(quitdisp, (300, 200))

        pg.display.flip()

def runmenu():
    global isRunning
    global menuRunning
    global selectedLevel
    button_state = 0

    titlefont = pg.font.SysFont("Arial", 45)
    playfont1 = pg.font.SysFont("Arial", 25)
    playfont2 = pg.font.SysFont("Arial", 25)
    playfont3 = pg.font.SysFont("Arial", 25)
    quitfont = pg.font.SysFont("Arial", 25)
    playfont1.set_underline(True)
    playfont1.set_bold(True)
    title = titlefont.render('RayCaster', 1, WHITE)
    playdisplvl1 = playfont1.render('Play level 1', 1, WHITE)
    playdisplvl2 = playfont2.render('Play level 2', 1, WHITE)
    playdisplvl3 = playfont3.render('Play level 3', 1, WHITE)
    quitdisp = quitfont.render('Quit', 1, WHITE)
    while menuRunning:
        
        for ev in pg.event.get():
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_DOWN or ev.key == pg.K_UP or ev.key == pg.K_w or ev.key == pg.K_s:
                    if ev.key == pg.K_DOWN or ev.key == pg.K_s:
                        button_state = (button_state+1) % 4
                    if ev.key == pg.K_UP or ev.key == pg.K_w:
                        button_state -= 1
                        if button_state  == -1:
                            button_state = 3
                    if button_state == 0:
                        playfont1.set_bold(True)
                        playfont1.set_underline(True)
                        quitfont.set_bold(False)
                        quitfont.set_underline(False)
                        playfont2.set_bold(False)
                        playfont2.set_underline(False)
                    if button_state == 1:
                        playfont1.set_bold(False)
                        playfont1.set_underline(False)
                        playfont2.set_bold(True)
                        playfont2.set_underline(True)
                        playfont3.set_bold(False)
                        playfont3.set_underline(False)
                    if button_state == 2:
                        playfont2.set_bold(False)
                        playfont2.set_underline(False)
                        playfont3.set_bold(True)
                        playfont3.set_underline(True)
                        quitfont.set_bold(False)
                        quitfont.set_underline(False)
                    if button_state == 3:
                        playfont3.set_bold(False)
                        playfont3.set_underline(False)
                        quitfont.set_bold(True)
                        quitfont.set_underline(True)
                        playfont1.set_bold(False)
                        playfont1.set_underline(False)
                    
                    playdisplvl1 = playfont1.render('Play level 1', 1, WHITE)
                    playdisplvl2 = playfont2.render('Play level 2', 1, WHITE)
                    playdisplvl3 = playfont3.render('Play level 3', 1, WHITE)
                    quitdisp = quitfont.render('Quit', 1, WHITE)
                if ev.key == pg.K_RETURN:
                    menuRunning = False
                    if button_state == 0:
                        selectedLevel = 'level1.txt'
                    if button_state == 1:
                        selectedLevel = 'level2.txt'
                    if button_state == 2:
                        selectedLevel = 'level3.txt'
                    if button_state == 3:
                        isRunning = False
                    else:
                        isRunning = True
        screen.fill(BLACK)
        screen.blit(title, (100, 100))
        screen.blit(playdisplvl1, (300, 120))
        screen.blit(playdisplvl2, (300, 160))
        screen.blit(playdisplvl3, (300, 200))
        screen.blit(quitdisp, (300, 260))
        pg.display.flip()
    

while restart:

    runmenu()

    rungame()
pg.quit()
