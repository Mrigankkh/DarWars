from behavior_gene import BehaviorGene

def get_dominant_traits(chromosome, top_n=6):
    trait_names = {
        0: "Aggressive", 1: "Defensive", 3: "Tactical", 4: "Kamikaze",
        5: "Adaptive", 10: "Zigzag", 11: "Circle", 12: "Stop",
        13: "Shoot Straight", 14: "Spread Shot", 15: "Burst Shot",
        16: "Dodge", 18: "Ambush", 17: "Group"
    }

    active_traits = [
        (i, chromosome[i]) for i in trait_names
        if i in chromosome and chromosome[i] > 0
    ]
    active_traits.sort(key=lambda x: x[1], reverse=True)

    top_traits = active_traits[:top_n]
    return [f"{trait_names[i]} ({v:.2f})" for i, v in top_traits]

def get_role_name(val):
    return "Leader" if val > 0.7 else "Middle" if val > 0.3 else "Edge"

def get_pattern_name(idx):
    patterns = ["Line", "Circle", "Triangle", "Grid"]
    return patterns[idx] if 0 <= idx < len(patterns) else "Unknown"
