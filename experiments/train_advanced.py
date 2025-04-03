# train.py
import random
import math

# =========================================
# CONFIG
# =========================================
GRID_SIZE = 15
N_ITEMS = 8
SIM_STEPS = 100
POP_SIZE = 20
N_GENERATIONS = 100
TOURNAMENT_SIZE = 3
MUTATION_RATE = 0.3
ELITISM = 1

BEST_GENES_FILE = "best_genes.txt"

"""
Chromosome (genes):
[ rawSpeed, rawRadius, turnProb, searchThreshold, avoidRevisitWeight, guardWeight ]

Where:
- rawSpeed in [0.5..2.5], for instance
- rawRadius in [2.0..6.0]
- turnProb in [0..1]
- searchThreshold in [5..20]
- avoidRevisitWeight in [0..5]
- guardWeight in [0..5]

We define a trade-off: 
effectiveSpeed = clamp( rawSpeed - alpha*(rawRadius - baselineRadius), minSpeed, maxSpeed )
If rawRadius is large, speed is forced lower. 
Hence the AI can't exploit big radius + big speed simultaneously.
"""

# ranges
MIN_SPEED_GENE, MAX_SPEED_GENE = 0.5, 1.5
MIN_RADIUS,     MAX_RADIUS     = 2.0, 4.0
TURNP_MIN,      TURNP_MAX      = 0.0, 1.0
SEARCH_THR_MIN, SEARCH_THR_MAX = 5,   20
AVOIDW_MIN,     AVOIDW_MAX     = 0.0, 5.0
GUARDW_MIN,     GUARDW_MAX     = 0.0, 5.0

# For the trade-off
ALPHA            = 0.5
BASELINE_RADIUS  = 3.0
MIN_SPEED        = 0.5
MAX_SPEED        = 2.0

def clamp(v,mn,mx):
    return max(mn,min(v,mx))

def distance(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# =========================================
# GENOME OPS
# =========================================
def create_chromosome():
    rawSpd = random.uniform(MIN_SPEED_GENE, MAX_SPEED_GENE)
    rawRad = random.uniform(MIN_RADIUS,     MAX_RADIUS)
    tp     = random.uniform(TURNP_MIN,      TURNP_MAX)
    sthr   = random.randint(SEARCH_THR_MIN, SEARCH_THR_MAX)
    avw    = random.uniform(AVOIDW_MIN,     AVOIDW_MAX)
    gwr    = random.uniform(GUARDW_MIN,     GUARDW_MAX)

    return [ rawSpd, rawRad, tp, sthr, avw, gwr ]

def mutate(genes):
    # rawSpeed
    if random.random()<MUTATION_RATE:
        shift= random.choice([-0.1,0.1])
        genes[0]+= shift
        genes[0]= clamp(genes[0], MIN_SPEED_GENE, MAX_SPEED_GENE)
    # rawRadius
    if random.random()<MUTATION_RATE:
        shift= random.choice([-0.5,0.5])
        genes[1]+= shift
        genes[1]= clamp(genes[1], MIN_RADIUS, MAX_RADIUS)
    # turnProb
    if random.random()<MUTATION_RATE:
        shift= random.choice([-0.1,0.1])
        genes[2]+= shift
        genes[2]= clamp(genes[2], TURNP_MIN, TURNP_MAX)
    # searchThreshold
    if random.random()<MUTATION_RATE:
        shift= random.choice([-1,1])
        genes[3]+= shift
        genes[3]= clamp(genes[3], SEARCH_THR_MIN, SEARCH_THR_MAX)
    # avoidRevisitWeight
    if random.random()<MUTATION_RATE:
        shift= random.choice([-0.5,0.5])
        genes[4]+= shift
        genes[4]= clamp(genes[4], AVOIDW_MIN, AVOIDW_MAX)
    # guardWeight
    if random.random()<MUTATION_RATE:
        shift= random.choice([-0.5,0.5])
        genes[5]+= shift
        genes[5]= clamp(genes[5], GUARDW_MIN, GUARDW_MAX)

def crossover(p1,p2):
    child=[]
    for g1,g2 in zip(p1,p2):
        child.append(g1 if random.random()<0.5 else g2)
    return child

# =========================================
# SIMULATION
# =========================================

def simulate_chase(genes):
    """
    Genes = [ rawSpeed, rawRadius, turnProb, searchThreshold, avoidW, guardW ]
    We'll do the memory + item guard approach from before,
    but we compute:
      effectiveSpeed = clamp(rawSpeed - ALPHA*(rawRadius - BASELINE_RADIUS), MIN_SPEED, MAX_SPEED)
    detectionRadius = rawRadius

    Then do a standard 'Chase & Collect' with dummy player.
    """

    rawSpd, rawRad, turnP, sThr, avoidW, guardW = genes

    # compute synergy for speed
    effSpeed = rawSpd - ALPHA*(rawRad - BASELINE_RADIUS)
    effSpeed = clamp(effSpeed, MIN_SPEED, MAX_SPEED)

    # place items
    items = set()
    while len(items)<N_ITEMS:
        x= random.randint(0,GRID_SIZE-1)
        y= random.randint(0,GRID_SIZE-1)
        items.add((x,y))

    # dummy player
    player= [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]
    # AI
    ai_pos= [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]
    while ai_pos==player:
        ai_pos= [random.randint(0,GRID_SIZE-1), random.randint(0,GRID_SIZE-1)]

    visited_count= [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
    visited_count[ai_pos[1]][ai_pos[0]]+=1

    time_since_seen=999
    last_seen_pos= ai_pos[:]
    state='search'
    items_collected=0

    # search direction
    sdx,sdy= random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    for step in range(SIM_STEPS):
        # 1) random move for dummy player
        pdir = random.choice([(1,0),(-1,0),(0,1),(0,-1),(0,0)])
        nx= clamp(player[0]+pdir[0], 0, GRID_SIZE-1)
        ny= clamp(player[1]+pdir[1], 0, GRID_SIZE-1)
        player= [nx, ny]

        # check items
        if tuple(player) in items:
            items.remove(tuple(player))
            items_collected+=1

        # line-of-sight check with rawRad
        dist= distance(ai_pos, player)
        if dist<= rawRad:
            last_seen_pos= player[:]
            time_since_seen=0
            state='chase'
        else:
            time_since_seen+=1
            if time_since_seen> sThr:
                state='search'

        if state=='chase':
            # move 'effSpeed' steps
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
                ai_pos[0]= clamp(ai_pos[0]+ step_x,0,GRID_SIZE-1)
                ai_pos[1]= clamp(ai_pos[1]+ step_y,0,GRID_SIZE-1)
                visited_count[ai_pos[1]][ai_pos[0]]+=1
                if ai_pos==player:
                    # big reward for quick catch
                    return 2000 - step*10 - items_collected*50
        else:
            # search with memory + item guard
            speed= int(effSpeed)
            for _ in range(speed):
                # maybe random turn
                if random.random()<turnP:
                    if random.random()<0.5:
                        sdx,sdy= (-sdy, sdx)
                    else:
                        sdx,sdy= (sdy, -sdx)

                # pick best direction to move:
                best_dir= (sdx,sdy)
                best_cost= calc_dir_cost(ai_pos, best_dir, visited_count, avoidW, guardW, items)
                for dd in [(1,0),(-1,0),(0,1),(0,-1)]:
                    c= calc_dir_cost(ai_pos, dd, visited_count, avoidW, guardW, items)
                    if c< best_cost:
                        best_cost= c
                        best_dir= dd
                sdx,sdy= best_dir

                # move 1 step
                nx= clamp(ai_pos[0]+ sdx,0,GRID_SIZE-1)
                ny= clamp(ai_pos[1]+ sdy,0,GRID_SIZE-1)
                ai_pos=[nx, ny]
                visited_count[ny][nx]+=1
                if ai_pos==player:
                    return 2000 - step*10 - items_collected*50

    # never caught
    # penalize items collected & big revisit
    total_visits=0
    for row in visited_count:
        total_visits+= sum(row)
    revisit_penalty= (total_visits - SIM_STEPS)*2
    fitness= 500 - items_collected*50 - revisit_penalty

    return max(0, fitness)

def calc_dir_cost(ai_pos, ddir, visited_count, avoidW, guardW, items):
    x2= ai_pos[0]+ ddir[0]
    y2= ai_pos[1]+ ddir[1]
    if x2<0 or x2>=GRID_SIZE or y2<0 or y2>=GRID_SIZE:
        return 9999
    vcount= visited_count[y2][x2]
    cost= vcount - avoidW
    # item guard logic
    if guardW>0 and len(items)>0:
        # find closest item
        distClosest= 9999
        for (ix,iy) in items:
            dd= math.sqrt((x2- ix)**2 + (y2- iy)**2)
            if dd< distClosest:
                distClosest= dd
        # cost -= guardW*(max(0,3-distClosest))
        # if distClosest <3, strong negative cost
        cost -= guardW*( max(0, 3-distClosest) )

    return cost

# =========================================
# GA CORE
# =========================================
def evaluate_population(pop):
    return [simulate_chase(ch) for ch in pop]

def tournament_selection(pop, fits):
    idxs= random.sample(range(len(pop)), TOURNAMENT_SIZE)
    best= idxs[0]
    bestF= fits[best]
    for i in idxs[1:]:
        if fits[i]> bestF:
            best= i
            bestF= fits[i]
    return pop[best]

def run_ga():
    population= [create_chromosome() for _ in range(POP_SIZE)]
    for gen in range(N_GENERATIONS):
        fits= evaluate_population(population)
        bestF= max(fits)
        avgF= sum(fits)/ len(fits)
        print(f"[GEN {gen}] Best={bestF:.2f}, Avg={avgF:.2f}")

        new_pop=[]
        sorted_idx= sorted(range(len(population)), key=lambda i: fits[i], reverse=True)
        for e in range(ELITISM):
            new_pop.append(population[sorted_idx[e]][:])

        while len(new_pop)<POP_SIZE:
            p1= tournament_selection(population,fits)
            p2= tournament_selection(population,fits)
            child= crossover(p1,p2)
            mutate(child)
            new_pop.append(child)

        population= new_pop

    final_fits= evaluate_population(population)
    best_i= max(range(len(population)), key=lambda i: final_fits[i])
    best_chrom= population[best_i]
    best_score= final_fits[best_i]
    print("\n=== GA COMPLETE ===")
    print("Best Chromosome =", best_chrom)
    print("Best Fitness =", best_score)

    return best_chrom

if __name__=="__main__":
    best= run_ga()
    # Save best
    with open(BEST_GENES_FILE,"w") as f:
        f.write(" ".join(map(str,best)))
    print(f"\nSaved best genes to {BEST_GENES_FILE}.")
