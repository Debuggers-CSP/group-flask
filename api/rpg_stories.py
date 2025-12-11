# RPG Story Elements Data Management
# This file handles story element data storage and voting (love/skip counts)
# Updated to limit each category to 5 items

import random, json, os, fcntl
from flask import current_app

# ============================================================================
# INITIAL STORY DATA - LIMITED TO 5 ITEMS PER CATEGORY
# ============================================================================
story_data_initial = {
    "Main Plot Hooks": [
        "A mysterious plague is turning villagers to stone",
        "An ancient prophecy predicts the chosen one's arrival",
        "The king has been replaced by a doppelganger",
        "A dragon demands tribute from the local village",
        "Strange portals are opening across the realm"
    ],
    "Side Quests": [
        "Help the baker retrieve stolen recipes from bandits",
        "Investigate mysterious sounds in the abandoned mill",
        "Escort a merchant caravan through dangerous territory",
        "Find a rare herb to cure the herbalist's sick child",
        "Solve the riddle of the ancient standing stones"
    ],
    "Character Motivations": [
        "Seeking revenge for a loved one's death",
        "Trying to prove themselves to their family",
        "Running from a dark past",
        "Searching for a missing person",
        "Driven by insatiable curiosity"
    ],
    "Locations": [
        "A bustling port city with diverse cultures",
        "An ancient forest filled with magical creatures",
        "A mysterious floating island in the sky",
        "Underground caverns with bioluminescent fungi",
        "A desert oasis hiding ancient secrets"
    ],
    "NPCs": [
        "A wise old wizard with a mysterious past",
        "A cunning thief with a heart of gold",
        "A gruff blacksmith hiding a gentle soul",
        "A cheerful innkeeper who knows everyone's secrets",
        "A noble knight struggling with their vows"
    ],
    "Twists": [
        "The villain is actually trying to prevent a greater evil",
        "The quest giver has been lying about their true intentions",
        "The artifact is cursed and corrupts those who possess it",
        "Time is running backwards in this location",
        "The party member is secretly a spy"
    ]
}

# ============================================================================
# FILE MANAGEMENT FUNCTIONS
# ============================================================================

def get_story_file():
    """Get the path to the story elements JSON file"""
    data_folder = current_app.config['DATA_FOLDER']
    return os.path.join(data_folder, 'story_elements.json')

def _read_story_file():
    """Read story elements from JSON file with file locking"""
    STORY_FILE = get_story_file()
    if not os.path.exists(STORY_FILE):
        return []
    with open(STORY_FILE, 'r') as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            data = json.load(f)
        except Exception:
            data = []
        fcntl.flock(f, fcntl.LOCK_UN)
    return data

def _write_story_file(data):
    """Write story elements to JSON file with file locking"""
    STORY_FILE = get_story_file()
    with open(STORY_FILE, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f, indent=2)
        fcntl.flock(f, fcntl.LOCK_UN)

# ============================================================================
# INITIALIZATION
# ============================================================================

def initStoryElements():
    """Initialize story elements JSON file if it doesn't exist"""
    STORY_FILE = get_story_file()
    # Only initialize if file does not exist
    if os.path.exists(STORY_FILE):
        return
    
    story_data = []
    item_id = 0
    for category, elements in story_data_initial.items():
        for element_text in elements:
            story_data.append({
                "id": item_id,
                "category": category,
                "element": element_text,
                "love": 0,
                "skip": 0
            })
            item_id += 1
    
    # Prime some love/skip responses for initial data
    for i in range(10):
        id = random.randint(0, len(story_data) - 1)
        story_data[id]['love'] += 1
    for i in range(5):
        id = random.randint(0, len(story_data) - 1)
        story_data[id]['skip'] += 1
    
    _write_story_file(story_data)

# ============================================================================
# DATA RETRIEVAL FUNCTIONS
# ============================================================================

def getStoryElements():
    """Get all story elements"""
    return _read_story_file()

def getStoryElement(id):
    """Get a specific story element by ID"""
    elements = _read_story_file()
    if 0 <= id < len(elements):
        return elements[id]
    return None

def getRandomStoryElement():
    """Get a random story element"""
    elements = _read_story_file()
    if elements:
        return random.choice(elements)
    return None

def getStoryElementsByCategory(category):
    """Get all story elements in a specific category"""
    elements = _read_story_file()
    return [elem for elem in elements if elem['category'] == category]

def getMostLovedElement():
    """Get the story element with the most love votes"""
    elements = _read_story_file()
    if not elements:
        return None
    return max(elements, key=lambda x: x['love'])

def getMostSkippedElement():
    """Get the story element with the most skip votes"""
    elements = _read_story_file()
    if not elements:
        return None
    return max(elements, key=lambda x: x['skip'])

# ============================================================================
# VOTING FUNCTIONS
# ============================================================================

def _vote_story(id, field):
    """Internal function to increment love or skip count"""
    STORY_FILE = get_story_file()
    with open(STORY_FILE, 'r+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        elements = json.load(f)
        if 0 <= id < len(elements):
            elements[id][field] += 1
            # Move file pointer to start before writing updated JSON
            f.seek(0)
            json.dump(elements, f, indent=2)
            # Truncate file to remove any leftover data from previous content
            f.truncate()
            fcntl.flock(f, fcntl.LOCK_UN)
            return elements[id][field]
        fcntl.flock(f, fcntl.LOCK_UN)
    return None

def addStoryLove(id):
    """Increment the love count for a story element"""
    return _vote_story(id, 'love')

def addStorySkip(id):
    """Increment the skip count for a story element"""
    return _vote_story(id, 'skip')

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def printStoryElement(element):
    """Print story element details"""
    if element:
        print(f"ID: {element['id']}")
        print(f"Category: {element['category']}")
        print(f"Element: {element['element']}")
        print(f"Love: {element['love']}, Skip: {element['skip']}\n")

def countStoryElements():
    """Get total count of story elements"""
    elements = _read_story_file()
    return len(elements)

def getCategories():
    """Get list of all unique categories"""
    elements = _read_story_file()
    categories = list(set(elem['category'] for elem in elements))
    return sorted(categories)

# ============================================================================
# MAIN - FOR TESTING
# ============================================================================

if __name__ == "__main__":
    # Use for reference only
    print("Story elements data management module")
    print("This module requires Flask app context to run")
    print("\nCategories: 6")
    print("Items per category: 5")
    print("Total items: 30")
