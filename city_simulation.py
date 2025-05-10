
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import streamlit as st

# PARAMETERS & STATE
CITY_SIZE   = 20     # grid dimensions
MAX_HEIGHT  = 10     # cap on building height
INIT_MAT    = 1000   # initial building materials
INIT_POP    = 5000   # initial max population

ZONES = ['residential', 'commercial', 'industrial']

# Parallel arrays for numeric & categorical data
heights = np.zeros((CITY_SIZE, CITY_SIZE), dtype=int)
zones   = np.empty((CITY_SIZE, CITY_SIZE), dtype='<U12')  # string up to length 12

# Resources
resources = {
    'material': INIT_MAT,
    'population': INIT_POP,
}

# INITIALIZATION
def initialize_city(max_height=MAX_HEIGHT):
    global heights, zones
    heights[:] = np.random.randint(1, max_height+1, size=(CITY_SIZE, CITY_SIZE))
    zones[:] = np.random.choice(ZONES, size=(CITY_SIZE, CITY_SIZE))

def add_roads():
    mid = CITY_SIZE // 2
    zones[mid, :] = 'road'
    zones[:, mid] = 'road'

def add_parks(p_park=0.05):
    mask = np.random.rand(CITY_SIZE, CITY_SIZE) < p_park
    zones[mask] = 'park'

# DYNAMICS
def get_zone_growth_rate(i, j, base_rates):
    return base_rates.get(zones[i, j], 0.0)

def check_resources():
    if resources['material'] < 1:
        return False
    resources['material'] -= 1
    return True

def simulate_demand():
    res_count = np.count_nonzero(zones == 'residential')
    return max(0, 1000 - res_count)

def calculate_pollution():
    return np.count_nonzero(zones == 'industrial')

def simulate_growth(base_rates, near_road_bonus=0.2):
    if not check_resources():
        return False
    for i in range(CITY_SIZE):
        for j in range(CITY_SIZE):
            rate = get_zone_growth_rate(i, j, base_rates)
            if rate > 0 and rate < 1.0:
                if (i > 0 and zones[i-1, j]=='road') or                    (i < CITY_SIZE-1 and zones[i+1, j]=='road') or                    (j > 0 and zones[i, j-1]=='road') or                    (j < CITY_SIZE-1 and zones[i, j+1]=='road'):
                    rate += near_road_bonus
            if np.random.rand() < rate:
                heights[i, j] = min(heights[i, j] + 1, MAX_HEIGHT)
    return True

# PLOTTING
def plot_city(ax, title):
    ax.clear()
    X, Y = np.meshgrid(np.arange(CITY_SIZE), np.arange(CITY_SIZE))
    ax.plot_surface(X, Y, heights, cmap='viridis', edgecolor='none')
    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Height')

# STREAMLIT APP
st.title("Interactive 3D City Growth Simulation")

growth_rate = st.sidebar.slider("Growth Rate", 0.0, 0.5, 0.1, step=0.01)
max_height  = st.sidebar.slider("Max Height", 5, 30, MAX_HEIGHT)
p_park      = st.sidebar.slider("Park Prob", 0.0, 0.2, 0.05, step=0.01)
steps       = st.sidebar.slider("Steps", 1, 200, 50)

if st.sidebar.button("Reset"):
    initialize_city(max_height)
    add_roads()
    add_parks(p_park)
    resources['material'] = INIT_MAT
    st.experimental_rerun()

MAX_HEIGHT = max_height
base_rates = {
    'residential': growth_rate * 0.5,
    'commercial':  growth_rate,
    'industrial':  growth_rate * 1.5,
    'road':        0.0,
    'park':        0.0,
}

if 'inited' not in st.session_state:
    initialize_city(max_height)
    add_roads()
    add_parks(p_park)
    st.session_state.inited = True

for t in range(steps):
    if not simulate_growth(base_rates):
        st.warning(f"Materials exhausted at step {t}")
        break

st.write(f"Materials: {resources['material']}")
st.write(f"Demand: {simulate_demand()}")
st.write(f"Pollution: {calculate_pollution()}")

fig = plt.figure(figsize=(7,5))
ax  = fig.add_subplot(111, projection='3d')
plot_city(ax, f"After {steps} steps")
st.pyplot(fig)
