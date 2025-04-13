import streamlit as st
import random
import time
import numpy as np

# Set page config
st.set_page_config(
    page_title="Snake in Dholakpur",
    page_icon="🐍",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .game-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
    }
    .score {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    .game-over {
        font-size: 30px;
        color: #ff4b4b;
        text-align: center;
        margin: 20px;
    }
    .win-message {
        font-size: 30px;
        color: #28a745;
        text-align: center;
        margin: 20px;
    }
    .grid {
        display: grid;
        grid-template-columns: repeat(30, 20px);
        grid-template-rows: repeat(30, 20px);
        gap: 1px;
        background-image: url('https://img.freepik.com/free-vector/game-ground-cartoon-landscape_107791-1852.jpg');
        background-size: cover;
        padding: 10px;
        border: 10px solid #654321;
        border-radius: 5px;
        position: relative;
    }
    .cell {
        width: 20px;
        height: 20px;
        border-radius: 2px;
        background-color: transparent;
    }
    .snake-head {
        background-color: transparent;
        border-radius: 10px;
        position: relative;
    }
    .snake-head::before {
        content: "🐍";
        font-size: 16px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .snake-body {
        background-color: transparent;
        border-radius: 5px;
        position: relative;
    }
    .snake-body::before {
        content: "🟢";
        font-size: 14px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .human {
        background-color: transparent;
        position: relative;
    }
    .human::before {
        content: "🧑";
        font-size: 16px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .mountain {
        background-color: transparent;
        position: relative;
    }
    .mountain::before {
        content: "🏔️";
        font-size: 16px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .tree {
        background-color: transparent;
        position: relative;
    }
    .tree::before {
        content: "🌳";
        font-size: 16px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .house {
        background-color: transparent;
        position: relative;
    }
    .house::before {
        content: "🏠";
        font-size: 16px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .water {
        background-color: transparent;
        position: relative;
    }
    .water::before {
        content: "💧";
        font-size: 16px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .controls {
        display: flex;
        gap: 10px;
        margin-top: 20px;
    }
    .direction-button {
        width: 50px;
        height: 50px;
        font-size: 20px;
        margin: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Game constants
GRID_SIZE = 30
INITIAL_SNAKE_LENGTH = 3
MOVE_INTERVAL = 0.2  # seconds
OBSTACLE_COUNT = {
    'mountain': 5,
    'tree': 15,
    'house': 8,
    'water': 10
}

# Initialize session state
if 'game_state' not in st.session_state:
    # Create initial snake
    snake_initial = []
    head_x, head_y = GRID_SIZE//2, GRID_SIZE//2
    for i in range(INITIAL_SNAKE_LENGTH):
        snake_initial.append((head_x - i, head_y))
    
    # Setup boundary obstacles
    obstacles = []
    for i in range(GRID_SIZE):
        if i % 3 != 0:  # Leave some gaps for moving
            obstacles.extend([
                (i, 0),         # Top boundary
                (i, GRID_SIZE-1),  # Bottom boundary
                (0, i),         # Left boundary
                (GRID_SIZE-1, i)   # Right boundary
            ])
    
    # Generate village landscape elements
    landscape = {
        'mountains': [],
        'trees': [],
        'houses': [],
        'water': []
    }
    
    # Generate human position
    human_pos = None
    
    st.session_state.game_state = {
        'snake': snake_initial,
        'direction': (1, 0),
        'human': human_pos,
        'score': 0,
        'obstacles': obstacles,
        'landscape': landscape,
        'game_over': False,
        'win': False,
        'last_move_time': time.time(),
        'paused': False
    }

def generate_landscape():
    """Generate village landscape elements"""
    landscape = {
        'mountains': [],
        'trees': [],
        'houses': [],
        'water': []
    }
    
    occupied = set(st.session_state.game_state['snake'] + st.session_state.game_state['obstacles'])
    if st.session_state.game_state['human']:
        occupied.add(st.session_state.game_state['human'])
    
    # Add mountains (usually at edges)
    for _ in range(OBSTACLE_COUNT['mountain']):
        for attempt in range(100):
            # Place mountains around the edges
            if random.choice([True, False]):
                x = random.choice([1, 2, GRID_SIZE-3, GRID_SIZE-2])
                y = random.randint(1, GRID_SIZE-2)
            else:
                x = random.randint(1, GRID_SIZE-2)
                y = random.choice([1, 2, GRID_SIZE-3, GRID_SIZE-2])
                
            pos = (x, y)
            if pos not in occupied:
                landscape['mountains'].append(pos)
                occupied.add(pos)
                break
    
    # Add trees (forest clusters)
    forest_center_x = random.randint(5, GRID_SIZE-5)
    forest_center_y = random.randint(5, GRID_SIZE-5)
    
    for _ in range(OBSTACLE_COUNT['tree']):
        for attempt in range(100):
            # Create clusters of trees for forests
            x = min(max(1, forest_center_x + random.randint(-5, 5)), GRID_SIZE-2)
            y = min(max(1, forest_center_y + random.randint(-5, 5)), GRID_SIZE-2)
            pos = (x, y)
            if pos not in occupied:
                landscape['trees'].append(pos)
                occupied.add(pos)
                break
    
    # Add houses (village area)
    village_center_x = random.randint(10, GRID_SIZE-10)
    village_center_y = random.randint(10, GRID_SIZE-10)
    
    # Ensure village is not in the forest
    while abs(village_center_x - forest_center_x) < 8 and abs(village_center_y - forest_center_y) < 8:
        village_center_x = random.randint(10, GRID_SIZE-10)
        village_center_y = random.randint(10, GRID_SIZE-10)
        
    for _ in range(OBSTACLE_COUNT['house']):
        for attempt in range(100):
            # Create village of houses
            x = min(max(1, village_center_x + random.randint(-4, 4)), GRID_SIZE-2)
            y = min(max(1, village_center_y + random.randint(-4, 4)), GRID_SIZE-2)
            pos = (x, y)
            if pos not in occupied:
                landscape['houses'].append(pos)
                occupied.add(pos)
                break
    
    # Add water bodies
    water_center_x = random.randint(5, GRID_SIZE-5)
    water_center_y = random.randint(5, GRID_SIZE-5)
    
    # Ensure water is not in village or directly in forest
    while ((abs(water_center_x - village_center_x) < 7 and abs(water_center_y - village_center_y) < 7) or
           (abs(water_center_x - forest_center_x) < 5 and abs(water_center_y - forest_center_y) < 5)):
        water_center_x = random.randint(5, GRID_SIZE-5)
        water_center_y = random.randint(5, GRID_SIZE-5)
    
    for _ in range(OBSTACLE_COUNT['water']):
        for attempt in range(100):
            # Create water body
            x = min(max(1, water_center_x + random.randint(-3, 3)), GRID_SIZE-2)
            y = min(max(1, water_center_y + random.randint(-3, 3)), GRID_SIZE-2)
            pos = (x, y)
            if pos not in occupied:
                landscape['water'].append(pos)
                occupied.add(pos)
                break
    
    return landscape

def generate_human():
    """Generate a new position for the human"""
    # Prefer placing human near houses
    if len(st.session_state.game_state['landscape']['houses']) > 0:
        house = random.choice(st.session_state.game_state['landscape']['houses'])
        for attempt in range(100):
            x = min(max(1, house[0] + random.randint(-3, 3)), GRID_SIZE-2)
            y = min(max(1, house[1] + random.randint(-3, 3)), GRID_SIZE-2)
            pos = (x, y)
            
            obstacles = (st.session_state.game_state['obstacles'] + 
                        st.session_state.game_state['landscape']['mountains'] +
                        st.session_state.game_state['landscape']['trees'] +
                        st.session_state.game_state['landscape']['houses'] +
                        st.session_state.game_state['landscape']['water'])
            
            if pos not in obstacles and pos not in st.session_state.game_state['snake']:
                return pos
    
    # Fallback to random placement
    for attempt in range(100):
        x = random.randint(1, GRID_SIZE-2)
        y = random.randint(1, GRID_SIZE-2)
        pos = (x, y)
        
        obstacles = (st.session_state.game_state['obstacles'] + 
                    st.session_state.game_state['landscape']['mountains'] +
                    st.session_state.game_state['landscape']['trees'] +
                    st.session_state.game_state['landscape']['houses'] +
                    st.session_state.game_state['landscape']['water'])
        
        if pos not in obstacles and pos not in st.session_state.game_state['snake']:
            return pos
    
    # Default fallback position
    return (GRID_SIZE//2, GRID_SIZE//2 - 5)

def move_human():
    """Move the human character to escape from snake"""
    if not st.session_state.game_state['human']:
        return

    # Human only moves every few snake moves (slower than snake)
    if random.random() > 0.3:
        return

    human_pos = st.session_state.game_state['human']
    snake_head = st.session_state.game_state['snake'][0]
    
    # Get distance to snake
    dx = snake_head[0] - human_pos[0]
    dy = snake_head[1] - human_pos[1]
    
    # Try to move away from snake
    possible_moves = []
    for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        new_pos = (human_pos[0] + direction[0], human_pos[1] + direction[1])
        
        # Check if move is valid
        obstacles = (st.session_state.game_state['obstacles'] + 
                    st.session_state.game_state['landscape']['mountains'] +
                    st.session_state.game_state['landscape']['trees'] +
                    st.session_state.game_state['landscape']['houses'] +
                    st.session_state.game_state['landscape']['water'])
                    
        if (0 < new_pos[0] < GRID_SIZE-1 and 0 < new_pos[1] < GRID_SIZE-1 and
            new_pos not in obstacles and
            new_pos not in st.session_state.game_state['snake']):
            
            # Calculate if this move increases distance from snake
            new_dx = snake_head[0] - new_pos[0]
            new_dy = snake_head[1] - new_pos[1]
            old_dist = dx*dx + dy*dy
            new_dist = new_dx*new_dx + new_dy*new_dy
            
            if new_dist >= old_dist:
                possible_moves.append((new_pos, new_dist))
    
    if possible_moves:
        # Sort by distance (prefer moves that maximize distance)
        possible_moves.sort(key=lambda x: x[1], reverse=True)
        st.session_state.game_state['human'] = possible_moves[0][0]
    else:
        # If trapped, stay in place
        pass

def move_snake():
    if st.session_state.game_state['paused'] or st.session_state.game_state['game_over'] or st.session_state.game_state['win']:
        return
    
    current_time = time.time()
    if current_time - st.session_state.game_state['last_move_time'] < MOVE_INTERVAL:
        return
    
    st.session_state.game_state['last_move_time'] = current_time
    
    try:
        # Get current head position
        head = st.session_state.game_state['snake'][0]
        direction = st.session_state.game_state['direction']
        
        # Calculate new head position
        new_head = (head[0] + direction[0], head[1] + direction[1])
        
        # Get all obstacles
        obstacles = (st.session_state.game_state['obstacles'] + 
                   st.session_state.game_state['landscape']['mountains'] +
                   st.session_state.game_state['landscape']['trees'] +
                   st.session_state.game_state['landscape']['houses'] +
                   st.session_state.game_state['landscape']['water'])
        
        # Check for collisions with obstacles or self
        if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or
            new_head[1] < 0 or new_head[1] >= GRID_SIZE or
            new_head in st.session_state.game_state['snake'] or
            new_head in obstacles):
            st.session_state.game_state['game_over'] = True
            return
        
        # Move snake
        st.session_state.game_state['snake'].insert(0, new_head)
        
        # Check if human is caught
        if new_head == st.session_state.game_state['human']:
            st.session_state.game_state['score'] += 5
            
            # Check win condition - score reaches 20
            if st.session_state.game_state['score'] >= 20:
                st.session_state.game_state['win'] = True
                return
                
            st.session_state.game_state['human'] = generate_human()
            # Don't remove tail - snake grows
        else:
            st.session_state.game_state['snake'].pop()
        
        # Move human to escape
        move_human()
        
    except Exception as e:
        st.error(f"Game error: {str(e)}")
        # If any error occurs, reinitialize the game
        start_game()

def start_game():
    try:
        # Create initial snake
        snake_initial = []
        head_x, head_y = GRID_SIZE//2, GRID_SIZE//2
        for i in range(INITIAL_SNAKE_LENGTH):
            snake_initial.append((head_x - i, head_y))
        
        # Setup boundary obstacles
        obstacles = []
        for i in range(GRID_SIZE):
            if i % 3 != 0:  # Leave some gaps for moving
                obstacles.extend([
                    (i, 0),         # Top boundary
                    (i, GRID_SIZE-1),  # Bottom boundary
                    (0, i),         # Left boundary
                    (GRID_SIZE-1, i)   # Right boundary
                ])
        
        # Set state
        st.session_state.game_state = {
            'snake': snake_initial,
            'direction': (1, 0),
            'human': None,
            'score': 0,
            'obstacles': obstacles,
            'landscape': {},
            'game_over': False,
            'win': False,
            'last_move_time': time.time(),
            'paused': False
        }
        
        # Generate village landscape
        st.session_state.game_state['landscape'] = generate_landscape()
        
        # Generate human position
        st.session_state.game_state['human'] = generate_human()
        
    except Exception as e:
        st.error(f"Game initialization error: {str(e)}")

def toggle_pause():
    st.session_state.game_state['paused'] = not st.session_state.game_state['paused']

def change_direction(new_direction):
    # Prevent 180-degree turns
    current_direction = st.session_state.game_state['direction']
    if (new_direction[0] != -current_direction[0] or new_direction[1] != -current_direction[1]):
        st.session_state.game_state['direction'] = new_direction

# Title and instructions
st.title("🐍 Snake in Dholakpur Village")
st.markdown("""
    In this game, you control a hungry snake in the village of Dholakpur. Your goal is to catch the running villager!
    Navigate through mountains, houses, trees, and water. Use the direction buttons to control the snake.
    
    **Win by catching the villager 4 times to reach a score of 20.**
    
    Beware of obstacles and don't hit yourself!
""")

# Game controls
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Game", key="start_game_button"):
        start_game()
with col2:
    if st.button("Pause/Resume", key="pause_button"):
        toggle_pause()

# Game display
if 'game_state' in st.session_state and st.session_state.game_state['snake']:
    # Ensure human exists
    if st.session_state.game_state['human'] is None:
        st.session_state.game_state['human'] = generate_human()
        
    move_snake()
    
    # Display score
    st.markdown(f"<div class='score'>Score: {st.session_state.game_state['score']} / 20</div>", unsafe_allow_html=True)
    
    try:
        # Create game grid
        grid_html = "<div class='grid'>"
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_class = "cell"
                
                # Check cell type
                if (x, y) == st.session_state.game_state['snake'][0]:
                    cell_class += " snake-head"
                elif (x, y) in st.session_state.game_state['snake'][1:]:
                    cell_class += " snake-body"
                elif st.session_state.game_state['human'] and (x, y) == st.session_state.game_state['human']:
                    cell_class += " human"
                elif (x, y) in st.session_state.game_state['landscape'].get('mountains', []):
                    cell_class += " mountain"
                elif (x, y) in st.session_state.game_state['landscape'].get('trees', []):
                    cell_class += " tree"
                elif (x, y) in st.session_state.game_state['landscape'].get('houses', []):
                    cell_class += " house"
                elif (x, y) in st.session_state.game_state['landscape'].get('water', []):
                    cell_class += " water"
                elif (x, y) in st.session_state.game_state['obstacles']:
                    # Random obstacles at the edge
                    obstacle_types = [" mountain", " tree"]
                    cell_class += random.choice(obstacle_types)
                
                grid_html += f"<div class='{cell_class}'></div>"
        grid_html += "</div>"
        
        st.markdown(grid_html, unsafe_allow_html=True)
    except Exception as e:
        # If render fails, show reset button
        st.error(f"Error rendering game: {str(e)}. Please reset.")
        if st.button("Reset Game", key="reset_error"):
            start_game()
    
    # Direction buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.button("↑", key="up", on_click=change_direction, args=((0, -1),))
        col_left, col_mid, col_right = st.columns(3)
        with col_left:
            st.button("←", key="left", on_click=change_direction, args=((-1, 0),))
        with col_mid:
            st.button("↓", key="down", on_click=change_direction, args=((0, 1),))
        with col_right:
            st.button("→", key="right", on_click=change_direction, args=((1, 0),))
    
    # Display game over or win message
    if st.session_state.game_state['game_over']:
        st.markdown(f"<div class='game-over'>Game Over! Final Score: {st.session_state.game_state['score']}</div>", unsafe_allow_html=True)
        if st.button("Play Again"):
            start_game()
    
    if st.session_state.game_state['win']:
        st.markdown("<div class='win-message'>You Win! You've captured enough villagers!</div>", unsafe_allow_html=True)
        if st.button("Play Again", key="play_again_win"):
            start_game()
    
    # Display pause message
    if st.session_state.game_state['paused']:
        st.markdown("<div class='game-over'>Game Paused</div>", unsafe_allow_html=True)
