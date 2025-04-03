# play.py
import pygame
import math
import random

GRID_SIZE = 15
CELL_SIZE = 40
N_ITEMS = 8
FPS = 5
CATCH_DISTANCE = 0.1

BEST_GENES_FILE = "best_genes.txt"

# For speed-radius synergy
ALPHA           = 0.5
BASELINE_RADIUS = 3.0
MIN_SPEED       = 0.5
MAX_SPEED       = 2.0

PLAYER_KEYS = {
    pygame.K_UP:    (0,-1),
    pygame.K_DOWN:  (0, 1),
    pygame.K_LEFT:  (-1,0),
    pygame.K_RIGHT: (1, 0)
}

def clamp(v,mn,mx):
    return max(mn,min(v,mx))

def distance(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def play_game(genes):
    """
    Genes: [ rawSpeed, rawRadius, turnProb, searchThreshold, avoidW, guardW ]
    We'll replicate the synergy + memory + guard logic from training.
    """
    rawSpeed, rawRad, turnP, sThr, avoidW, guardW = genes

    # compute effective speed
    effSpeed = rawSpeed - ALPHA*(rawRad - BASELINE_RADIUS)
    effSpeed = clamp(effSpeed, MIN_SPEED, MAX_SPEED)

    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE*CELL_SIZE, GRID_SIZE*CELL_SIZE))
    pygame.display.set_caption("Chase & Collect (Speed-Radius Trade-off)")
    clock = pygame.time.Clock()

    # items
    items= set()
    while len(items)< N_ITEMS:
        x= random.randint(0,GRID_SIZE-1)
        y= random.randint(0,GRID_SIZE-1)
        items.add((x,y))

    # player & AI
    player_pos= [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]
    ai_pos= [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]
    while ai_pos==player_pos:
        ai_pos= [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]

    items_collected=0

    visited_count= [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
    visited_count[ai_pos[1]][ai_pos[0]]+=1

    time_since_seen=999
    last_seen_pos= ai_pos[:]
    state='search'

    # search direction
    sdx,sdy= random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    running=True
    while running:
        clock.tick(FPS)

        # player input
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key in PLAYER_KEYS:
                    dx,dy= PLAYER_KEYS[event.key]
                    nx= clamp(player_pos[0]+dx,0,GRID_SIZE-1)
                    ny= clamp(player_pos[1]+dy,0,GRID_SIZE-1)
                    player_pos=[nx,ny]

        # collect
        if tuple(player_pos) in items:
            items.remove(tuple(player_pos))
            items_collected+=1
            if len(items)==0:
                print("You collected all items! You WIN!")
                running=False

        # line-of-sight
        dist= distance(ai_pos, player_pos)
        if dist<= rawRad:
            last_seen_pos= player_pos[:]
            time_since_seen=0
            state='chase'
        else:
            time_since_seen+=1
            if time_since_seen> sThr:
                state='search'

        if state=='chase':
            speed= int(effSpeed)
            dx= last_seen_pos[0]- ai_pos[0]
            dy= last_seen_pos[1]- ai_pos[1]
            for _ in range(speed):
                if abs(dx)>abs(dy):
                    step_x= 1 if dx>0 else -1
                    step_y= 0
                else:
                    step_x= 0
                    step_y= 1 if dy>0 else -1
                ai_pos[0]= clamp(ai_pos[0]+step_x,0,GRID_SIZE-1)
                ai_pos[1]= clamp(ai_pos[1]+step_y,0,GRID_SIZE-1)
                visited_count[ai_pos[1]][ai_pos[0]]+=1
        else:
            # search
            speed= int(effSpeed)
            for _ in range(speed):
                # maybe random turn
                if random.random()< turnP:
                    if random.random()<0.5:
                        sdx,sdy= (-sdy, sdx)
                    else:
                        sdx,sdy= (sdy, -sdx)

                # pick best dir
                best_dir= (sdx,sdy)
                best_cost= calc_dir_cost(ai_pos, best_dir, visited_count, avoidW, guardW, items)
                for dd in [(1,0),(-1,0),(0,1),(0,-1)]:
                    c= calc_dir_cost(ai_pos, dd, visited_count, avoidW, guardW, items)
                    if c< best_cost:
                        best_cost= c
                        best_dir= dd
                sdx,sdy= best_dir

                nx= clamp(ai_pos[0]+sdx,0,GRID_SIZE-1)
                ny= clamp(ai_pos[1]+sdy,0,GRID_SIZE-1)
                ai_pos=[nx, ny]
                visited_count[ny][nx]+=1

        # check catch
        if distance(ai_pos, player_pos)< CATCH_DISTANCE:
            print("You got caught! Game Over.")
            running=False

        # draw
        screen.fill((0,0,0))
        for gx in range(GRID_SIZE):
            for gy in range(GRID_SIZE):
                rect= pygame.Rect(gx*CELL_SIZE, gy*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen,(50,50,50),rect,1)

        # items
        for (ix,iy) in items:
            cx= ix*CELL_SIZE+ CELL_SIZE//2
            cy= iy*CELL_SIZE+ CELL_SIZE//2
            pygame.draw.circle(screen,(0,255,0),(cx,cy), CELL_SIZE//5)

        # player
        px= player_pos[0]*CELL_SIZE+ CELL_SIZE//2
        py= player_pos[1]*CELL_SIZE+ CELL_SIZE//2
        pygame.draw.circle(screen,(0,0,255),(px,py), CELL_SIZE//3)

        # AI
        ax= ai_pos[0]*CELL_SIZE+ CELL_SIZE//2
        ay= ai_pos[1]*CELL_SIZE+ CELL_SIZE//2
        pygame.draw.circle(screen,(255,0,0),(ax,ay), CELL_SIZE//3)

        font= pygame.font.SysFont(None,24)
        info= f"Items={items_collected}/{N_ITEMS}, AI State={state}"
        txt= font.render(info, True,(255,255,255))
        screen.blit(txt,(5,5))

        pygame.display.flip()

    pygame.quit()

def calc_dir_cost(ai_pos, ddir, visited_count, avoidW, guardW, items):
    x2= ai_pos[0]+ ddir[0]
    y2= ai_pos[1]+ ddir[1]
    if x2<0 or x2>=GRID_SIZE or y2<0 or y2>=GRID_SIZE:
        return 9999
    vcount= visited_count[y2][x2]
    cost= vcount - avoidW
    # item guarding
    if guardW>0 and len(items)>0:
        distClosest= 9999
        for (ix,iy) in items:
            dd= math.sqrt((x2-ix)**2 + (y2-iy)**2)
            if dd< distClosest:
                distClosest= dd
        cost -= guardW*( max(0, 3-distClosest) )
    return cost

if __name__=="__main__":
    # load best genes
    with open(BEST_GENES_FILE, "r") as f:
        line= f.read().strip()
    tokens= line.split()
    rawS= float(tokens[0])
    rawR= float(tokens[1])
    turnP= float(tokens[2])
    sThr= float(tokens[3])
    avW=  float(tokens[4])
    guW=  float(tokens[5])

    best_genes= [rawS, rawR, turnP, sThr, avW, guW]
    print("Loaded best genes:", best_genes)

    play_game(best_genes)
