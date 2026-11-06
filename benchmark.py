import os
import sys

# SUMO Environment Setup
if "SUMO_HOME" not in os.environ:
    for default_path in [r"C:\Program Files (x86)\SUMO", r"C:\Program Files\SUMO"]:
        if os.path.exists(default_path):
            os.environ["SUMO_HOME"] = default_path
            break

tools = os.path.join(os.environ["SUMO_HOME"], "tools")
if tools not in sys.path:
    sys.path.append(tools)

import traci

# Headless mode 'sumo' fast evaluation ke liye (GUI open nahi hoga, direct numbers aayenge)
sumo_binary = "sumo" 
sumo_cmd = [sumo_binary, "-c", "simulation.sumocfg", "--no-warnings", "true"]

def run_simulation(mode="dynamic"):
    traci.start(sumo_cmd)
    tl_id = "center"
    yellow_time = 3
    total_green = 70.0
    
    total_halting_vehicles = 0
    total_waiting_time = 0.0
    samples = 0
    step = 0
    
    while step < 3600 and traci.simulation.getMinExpectedNumber() > 0:
        # Queues count
        q_ns = traci.edge.getLastStepHaltingNumber("N2C") + traci.edge.getLastStepHaltingNumber("S2C")
        q_ew = traci.edge.getLastStepHaltingNumber("E2C") + traci.edge.getLastStepHaltingNumber("W2C")
        
        # Cumulative waiting delay
        w_ns = traci.edge.getWaitingTime("N2C") + traci.edge.getWaitingTime("S2C")
        w_ew = traci.edge.getWaitingTime("E2C") + traci.edge.getWaitingTime("W2C")
        
        total_halting_vehicles += (q_ns + q_ew)
        total_waiting_time += (w_ns + w_ew)
        samples += 1
        
        # Split decision
        if mode == "static":
            # Fixed 50-50 timer
            green_ns, green_ew = 35.0, 35.0
        else:
            # Hamara dynamic queue-proportional logic
            tot = q_ns + q_ew
            if tot == 0:
                green_ns, green_ew = 35.0, 35.0
            else:
                green_ns = max(15.0, min(55.0, (q_ns / tot) * total_green))
                green_ew = total_green - green_ns

        # N-S Green
        traci.trafficlight.setPhase(tl_id, 0)
        for _ in range(int(green_ns)):
            traci.simulationStep()
            step += 1
            
        # N-S Yellow
        traci.trafficlight.setPhase(tl_id, 1)
        for _ in range(yellow_time):
            traci.simulationStep()
            step += 1
            
        # E-W Green
        traci.trafficlight.setPhase(tl_id, 2)
        for _ in range(int(green_ew)):
            traci.simulationStep()
            step += 1
            
        # E-W Yellow
        traci.trafficlight.setPhase(tl_id, 3)
        for _ in range(yellow_time):
            traci.simulationStep()
            step += 1

    traci.close()
    
    avg_queue = total_halting_vehicles / max(1, samples)
    avg_delay = total_waiting_time / max(1, samples)
    return avg_queue, avg_delay

print("\nRunning Baseline Test: Static Signal (35s/35s Fixed)...")
static_q, static_d = run_simulation(mode="static")

print("Running Proposed Model: Dynamic Queue Solver...")
dyn_q, dyn_d = run_simulation(mode="dynamic")

# Percentage Reductions
q_reduction = ((static_q - dyn_q) / static_q) * 100
d_reduction = ((static_d - dyn_d) / static_d) * 100

print("\n" + "=" * 62)
print("          HACKATHON SIMULATION BENCHMARK SUMMARY")
print("=" * 62)
print(f"{'Performance Metric':<25} | {'Static':<10} | {'Dynamic':<10} | {'Reduction (%)'}")
print("-" * 62)
print(f"{'Avg Queue (vehs)':<25} | {static_q:<10.2f} | {dyn_q:<10.2f} | {q_reduction:>6.1f}%")
print(f"{'Avg Delay (seconds)':<25} | {static_d:<10.2f} | {dyn_d:<10.2f} | {d_reduction:>6.1f}%")
print("=" * 62)