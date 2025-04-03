# play.py
import pygame
import math
import random

GRID_SIZE = 15
CELL_SIZE = 40
N_ITEMS = 8
FPS = 5
CATCH_DISTANCE = 0.1  # If AI is within 0.1 cells => caught

PLAYER_KEYS = {
    pygame.K_UP:    (0, -1),
    pygame.K_DOWN:  (0,  1),
    pygame.K_LEFT:  (-1, 0),
    pygame.K_RIGHT: (1,  0)
}

BEST_GENES_FILE = "best_genes.txt"

def clamp(v, mn, mx):
    return max(mn, min(v,mx))

def distance(a,b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def has_line_of_sight(ai_pos, player_pos, detect_r):
    """
    For both random & GA AI, let's unify this:
    Return True if distance <= detect_r (no obstacles in this example).
    """
    return distance(ai_pos, player_pos) <= detect_r

def play_game(use_random):
    """
    If use_random=True, we define some fixed "Random AI" parameters 
    that STILL do chase if in line-of-sight, but are not evolved.
    If use_random=False, load GA parameters from best_genes.txt.
    """

    if use_random:
        print("Using RANDOM AI (with LOS-based chase).")
        # We'll set some "random-chaser" parameters:
        # detection_radius, chase_speed, search_speed, turn_prob, search_thresh
        detection_radius = 3.0   # must see you within 3 cells
        chase_speed      = 1
        search_speed     = 1
        turn_prob        = 0.3
        search_thresh    = 10
    else:
        print("Using GA-EVOLVED AI.")
        # Load best genes from file:
        with open(BEST_GENES_FILE,"r") as f:
            line = f.read().strip()
        tokens = line.split()
        detection_radius = float(tokens[0])   # e.g. dr
        chase_speed      = float(tokens[1])   # e.g. base_spd
        search_speed     = float(tokens[2])   # e.g. search_spd
        turn_prob        = float(tokens[3])   # e.g. turn_prob
        search_thresh    = float(tokens[4])   # e.g. search_thr
        print("Loaded best genes:", [detection_radius, chase_speed, 
                                     search_speed, turn_prob, search_thresh])

    # Pygame init
    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE*CELL_SIZE, GRID_SIZE*CELL_SIZE))
    pygame.display.set_caption("Chase & Collect - Compare AI Approaches")
    clock = pygame.time.Clock()

    # Scatter items
    items = set()
    while len(items)<N_ITEMS:
        x = random.randint(0,GRID_SIZE-1)
        y = random.randint(0,GRID_SIZE-1)
        items.add((x,y))

    # Player & AI spawn
    player_pos = [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]
    ai_pos     = [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]
    while ai_pos == player_pos:
        ai_pos = [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]

    items_collected = 0

    # AI state
    time_since_seen = 999
    last_seen_pos   = ai_pos[:]
    state           = 'search'
    current_speed   = 0

    # search direction
    sdx,sdy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    running=True
    while running:
        clock.tick(FPS)

        # Events
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key in PLAYER_KEYS:
                    dx,dy = PLAYER_KEYS[event.key]
                    nx = clamp(player_pos[0]+dx,0,GRID_SIZE-1)
                    ny = clamp(player_pos[1]+dy,0,GRID_SIZE-1)
                    player_pos=[nx,ny]
                elif event.key==pygame.K_ESCAPE:
                    running=False

        # Check item collection
        if tuple(player_pos) in items:
            items.remove(tuple(player_pos))
            items_collected+=1
            if len(items)==0:
                print("You collected all items! You WIN!")
                running=False

        # AI line-of-sight check
        if has_line_of_sight(ai_pos, player_pos, detection_radius):
            last_seen_pos   = player_pos[:]
            time_since_seen = 0
            state           = 'chase'
        else:
            time_since_seen+=1
            if time_since_seen>search_thresh:
                state='search'

        if state=='chase':
            current_speed = int(chase_speed)
            dx = last_seen_pos[0] - ai_pos[0]
            dy = last_seen_pos[1] - ai_pos[1]
            for _ in range(current_speed):
                if abs(dx)>abs(dy):
                    step_x = 1 if dx>0 else -1
                    step_y = 0
                else:
                    step_x = 0
                    step_y = 1 if dy>0 else -1
                ai_pos[0] = clamp(ai_pos[0]+step_x, 0,GRID_SIZE-1)
                ai_pos[1] = clamp(ai_pos[1]+step_y, 0,GRID_SIZE-1)
        else:
            # search
            current_speed = int(search_speed)
            if random.random()<turn_prob:
                # turn left or right
                if random.random()<0.5:
                    sdx,sdy= (-sdy, sdx)
                else:
                    sdx,sdy= (sdy, -sdx)
            for _ in range(current_speed):
                nx=ai_pos[0]+sdx
                ny=ai_pos[1]+sdy
                nx=clamp(nx,0,GRID_SIZE-1)
                ny=clamp(ny,0,GRID_SIZE-1)
                ai_pos=[nx,ny]

        # check catch
        if distance(ai_pos, player_pos)<CATCH_DISTANCE:
            print("You got caught! Game Over.")
            running=False

        # draw
        screen.fill((0,0,0))

        for gx in range(GRID_SIZE):
            for gy in range(GRID_SIZE):
                rect=pygame.Rect(gx*CELL_SIZE, gy*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (50,50,50), rect,1)

        # items
        for (ix,iy) in items:
            cx=ix*CELL_SIZE + CELL_SIZE//2
            cy=iy*CELL_SIZE + CELL_SIZE//2
            pygame.draw.circle(screen, (0,255,0),(cx,cy),CELL_SIZE//5)

        # player
        px=player_pos[0]*CELL_SIZE + CELL_SIZE//2
        py=player_pos[1]*CELL_SIZE + CELL_SIZE//2
        pygame.draw.circle(screen, (0,0,255),(px,py),CELL_SIZE//3)

        # AI
        ax=ai_pos[0]*CELL_SIZE + CELL_SIZE//2
        ay=ai_pos[1]*CELL_SIZE + CELL_SIZE//2
        pygame.draw.circle(screen, (255,0,0),(ax,ay),CELL_SIZE//3)

        font=pygame.font.SysFont(None,24)
        info = (f"AI: {'RANDOM' if use_random else 'GA'}  Items={items_collected}/{N_ITEMS}")
        txt = font.render(info,True,(255,255,255))
        screen.blit(txt,(5,5))

        pygame.display.flip()

    pygame.quit()

if __name__=="__main__":
    choice = input("Choose AI: (1) Random or (2) GA? ")
    if choice.strip()=='1':
        use_rand=True
    else:
        use_rand=False

    play_game(use_rand)
