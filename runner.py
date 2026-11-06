import os
import sys

# SUMO environment check
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Error: SUMO_HOME environment variable set nahi hai.")

import traci

# sumo-gui for visual demo, "sumo" for background fast mode
sumo_binary = "sumo-gui"
sumo_cmd = [
    sumo_binary, 
    "-c", "simulation.sumocfg", 
    "--start", 
    "--delay", "90",              # 90ms delay: smooth real-time visual speed
    "--window-size", "1000,700"   # Clean demo window size
]

def calculate_dynamic_splits(queue_ns, queue_ew, total_green=70, g_min=15):
    """
    Mathematical Split Allocation:
    Allocates green time proportional to demand with minimum safety bounds (g_min).
    """
    total_queue = queue_ns + queue_ew
    if total_queue == 0:
        # Default balanced split agar road empty hai
        return total_green / 2, total_green / 2

    # Proportional green split calculation
    ratio_ns = queue_ns / total_queue
    green_ns = ratio_ns * total_green
    green_ew = total_green - green_ns

    # Enforce minimum green guardrails (slack bounds)
    if green_ns < g_min:
        green_ns = g_min
        green_ew = total_green - g_min
    elif green_ew < g_min:
        green_ew = g_min
        green_ns = total_green - g_min

    return round(green_ns, 1), round(green_ew, 1)

def run():
    traci.start(sumo_cmd)
    tl_id = "center"
    
    yellow_time = 3
    all_red_time = 2
    clearance = yellow_time + all_red_time  # 5s per transition
    total_cycle_green = 70                  # Remaining green budget

    # SUMO intersection default phase definitions:
    # Phase 0: North-South Green (e.g., GGrrGGrr)
    # Phase 1: North-South Yellow (yyrryyrr)
    # Phase 2: East-West Green (rrGGrrGG)
    # Phase 3: East-West Yellow (rryyrryy)

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        # 1. Edge Camera sensing: Real-time halting queue length
        queue_ns = traci.edge.getLastStepHaltingNumber("N2C") + traci.edge.getLastStepHaltingNumber("S2C")
        queue_ew = traci.edge.getLastStepHaltingNumber("E2C") + traci.edge.getLastStepHaltingNumber("W2C")

        # 2. Dynamic optimization calculation
        green_ns, green_ew = calculate_dynamic_splits(queue_ns, queue_ew, total_green=total_cycle_green)

        print(f"\n[Cycle Update @ Step {step}s]")
        print(f"Queues -> N-S: {queue_ns} vehs | E-W: {queue_ew} vehs")
        print(f"Optimized Splits -> N-S Green: {green_ns}s | E-W Green: {green_ew}s")

        # --- PHASE 0: North-South Green ---
        traci.trafficlight.setPhase(tl_id, 0)
        for _ in range(int(green_ns)):
            traci.simulationStep()
            step += 1

        # --- PHASE 1: North-South Clearance (Yellow) ---
        traci.trafficlight.setPhase(tl_id, 1)
        for _ in range(yellow_time):
            traci.simulationStep()
            step += 1

        # --- PHASE 2: East-West Green ---
        traci.trafficlight.setPhase(tl_id, 2)
        for _ in range(int(green_ew)):
            traci.simulationStep()
            step += 1

        # --- PHASE 3: East-West Clearance (Yellow) ---
        traci.trafficlight.setPhase(tl_id, 3)
        for _ in range(yellow_time):
            traci.simulationStep()
            step += 1

    traci.close()

if __name__ == "__main__":
    run()