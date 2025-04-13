import streamlit as st
import random
import time
import numpy as np

# Set page config
st.set_page_config(
    page_title="Snake Game",
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
    .grid {
        display: grid;
        grid-template-columns: repeat(20, 20px);
        grid-template-rows: repeat(20, 20px);
        gap: 1px;
        background-color: #8B4513;
        padding: 10px;
        border: 10px solid #654321;
        border-radius: 5px;
        position: relative;
    }
    .cell {
        width: 20px;
        height: 20px;
        background-color: #90EE90;
        border-radius: 2px;
    }
    .snake-head {
        background-color: #006400;
        border-radius: 10px;
        position: relative;
    }
    .snake-head::before {
        content: "👁️";
        font-size: 12px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .snake-body {
        background-color: #4CAF50;
        border-radius: 5px;
    }
    .food {
        background-color: transparent;
        position: relative;
    }
    .food::before {
        content: "🐸";
        font-size: 16px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .knife {
        background-color: transparent;
        position: relative;
    }
    .knife::before {
        content: "🔪";
        font-size: 14px;
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
GRID_SIZE = 20
INITIAL_SNAKE_LENGTH = 3
MOVE_INTERVAL = 0.2  # seconds

# Initialize session state
if 'game_state' not in st.session_state:
    # Create initial snake
    snake_initial = []
    head_x, head_y = GRID_SIZE//2, GRID_SIZE//2
    for i in range(INITIAL_SNAKE_LENGTH):
        snake_initial.append((head_x - i, head_y))
    
    # Create knives on the boundary
    knives = []
    for i in range(GRID_SIZE):
        knives.extend([
            (i, 0),         # Top boundary
            (i, GRID_SIZE-1),  # Bottom boundary
            (0, i),         # Left boundary
            (GRID_SIZE-1, i)   # Right boundary
        ])
    
    st.session_state.game_state = {
        'snake': snake_initial,
        'direction': (1, 0),
        'food': None,
        'score': 0,
        'game_over': False,
        'last_move_time': time.time(),
        'paused': False,
        'knives': knives
    }

def generate_food():
    try:
        food = (random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2))
        if 'knives' not in st.session_state.game_state:
            st.session_state.game_state['knives'] = []
        if (food not in st.session_state.game_state['snake'] and 
            food not in st.session_state.game_state['knives']):
            return food
        return (GRID_SIZE//2, GRID_SIZE//2 - 3)  # Default position
    except:
        return (GRID_SIZE//2, GRID_SIZE//2 - 3)  # Default fallback position

def move_snake():
    if st.session_state.game_state['paused'] or st.session_state.game_state['game_over']:
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
        
        # Make sure knives exist in state
        if 'knives' not in st.session_state.game_state:
            # Create knives
            knives = []
            for i in range(GRID_SIZE):
                knives.extend([
                    (i, 0),         # Top boundary
                    (i, GRID_SIZE-1),  # Bottom boundary
                    (0, i),         # Left boundary
                    (GRID_SIZE-1, i)   # Right boundary
                ])
            st.session_state.game_state['knives'] = knives
        
        # Check for collisions with walls or knives
        if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or
            new_head[1] < 0 or new_head[1] >= GRID_SIZE or
            new_head in st.session_state.game_state['snake'] or
            new_head in st.session_state.game_state['knives']):
            st.session_state.game_state['game_over'] = True
            return
        
        # Move snake
        st.session_state.game_state['snake'].insert(0, new_head)
        
        # Check if food is eaten
        if new_head == st.session_state.game_state['food']:
            st.session_state.game_state['score'] += 1
            st.session_state.game_state['food'] = generate_food()
        else:
            st.session_state.game_state['snake'].pop()
    except:
        # If any error occurs, reinitialize the game
        start_game()

def start_game():
    try:
        # Create initial snake
        snake_initial = []
        head_x, head_y = GRID_SIZE//2, GRID_SIZE//2
        for i in range(INITIAL_SNAKE_LENGTH):
            snake_initial.append((head_x - i, head_y))
        
        # Create knives on the boundary
        knives = []
        for i in range(GRID_SIZE):
            knives.extend([
                (i, 0),         # Top boundary
                (i, GRID_SIZE-1),  # Bottom boundary
                (0, i),         # Left boundary
                (GRID_SIZE-1, i)   # Right boundary
            ])
        
        # Generate food first
        food_pos = (random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2))
        while food_pos in snake_initial or food_pos in knives:
            food_pos = (random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2))
        
        # Set state
        st.session_state.game_state = {
            'snake': snake_initial,
            'direction': (1, 0),
            'food': food_pos,
            'score': 0,
            'game_over': False,
            'last_move_time': time.time(),
            'paused': False,
            'knives': knives
        }
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
st.title("🐍 Snake Game")
st.markdown("""
    Use the direction buttons to control the snake. Eat the food to grow longer and increase your score.
    Avoid hitting the walls or yourself!
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
if st.session_state.game_state['snake']:
    # Ensure food exists
    if st.session_state.game_state['food'] is None:
        st.session_state.game_state['food'] = generate_food()
        
    move_snake()
    
    # Display score
    st.markdown(f"<div class='score'>Score: {st.session_state.game_state['score']}</div>", unsafe_allow_html=True)
    
    try:
        # Create game grid
        grid_html = "<div class='grid'>"
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_class = "cell"
                if (x, y) == st.session_state.game_state['snake'][0]:
                    cell_class += " snake-head"
                elif (x, y) in st.session_state.game_state['snake'][1:]:
                    cell_class += " snake-body"
                elif st.session_state.game_state['food'] and (x, y) == st.session_state.game_state['food']:
                    cell_class += " food"
                elif 'knives' in st.session_state.game_state and (x, y) in st.session_state.game_state['knives']:
                    cell_class += " knife"
                grid_html += f"<div class='{cell_class}'></div>"
        grid_html += "</div>"
        
        st.markdown(grid_html, unsafe_allow_html=True)
    except:
        # If render fails, show reset button
        st.error("Error rendering game. Please reset.")
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
    
    # Display game over message
    if st.session_state.game_state['game_over']:
        st.markdown(f"<div class='game-over'>Game Over! Final Score: {st.session_state.game_state['score']}</div>", unsafe_allow_html=True)
        if st.button("Play Again"):
            start_game()
    
    # Display pause message
    if st.session_state.game_state['paused']:
        st.markdown("<div class='game-over'>Game Paused</div>", unsafe_allow_html=True)

