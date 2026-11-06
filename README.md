# Dynamic Traffic Signal Optimization via Queueing Theory & SUMO Simulation

An applied operations research and simulation project demonstrating dynamic traffic signal control using queue-proportional phase allocation and M/M/c queueing dynamics, benchmarked against static timing models in Eclipse SUMO.

## 📌 Project Overview
Traditional fixed-timer signals fail under asymmetric traffic demand, causing queue explosions and prolonged commuter delays. This project implements a real-time dynamic controller via Python TraCI that samples approach queues and adaptively rebalances phase green splits within strict safety bounds.

## 🔬 Methodology & Core Formulation
- **Arrival & Service Modeling:** Modeled using M/M/c multi-server queues to constrain traffic intensity ($\rho < 1$) and prevent saturation.
- **Dynamic Green Split Allocation:**
  - Active sampling of vehicle queues across North-South and East-West corridors.
  - Green time dynamically stretched up to $g_{\max} = 55\text{s}$ for congested corridors.
  - Safety baseline constraint ($g_{\min} = 15\text{s}$) to avoid secondary traffic starvation.
  - Clearance timing calibrated to minimize dilemma-zone emergency braking.

## 📊 Benchmark Results (1-Hour Simulation | 2,651 Vehicles)
Benchmarked against standard 35s/35s fixed-time cycle under identical synthetic asymmetric demand (900 veh/hr vs 450 veh/hr):

| Performance Metric | Static Baseline (35s/35s) | Dynamic Model | Reduction (%) |
| :--- | :--- | :--- | :--- |
| **Avg Queue Length (vehs)** | 19.38 | 15.77 | **18.6%** |
| **Avg Cumulative Delay (s)** | 368.06 | 250.77 | **31.9%** |

## 🚀 How to Run Locally
1. Install Eclipse SUMO and verify `SUMO_HOME`.
2. Clone this repository:
```bash
   # Clone repository
   git clone https://github.com/NihelDuggal/dynamic-traffic-signal-sumo.git
   cd dynamic-traffic-signal-sumo

   # Run GUI simulation
   python runner.py

   # Run statistical benchmark
   python benchmark.py
```
