# Game Storyline System

This project is a Python-based storyline system for a game, built using the `pygame` library. It allows players to experience immersive story sequences with images, text, and voiceovers for each level of the game.

## Features

- **Dynamic Story Slides**: Each level has a series of slides with images, text, and optional voiceovers.
- **Word Wrapping**: Text is rendered with word wrapping to fit the screen dimensions.
- **Voiceover Support**: Each slide can play a corresponding audio file for added immersion.
- **Keyboard Controls**: Players can progress through the story using the `SPACE` key or exit with the `ESC` key.

## File Structure

```
game/
├── assets/
│   ├── story/          # Images for story slides
│   └── scenes/         # Audio files for voiceovers
├── Nashdevs/
│   ├── storyline.py    # Main storyline logic
│   └── sound.py        # Sound handling module
└── README.md           # Project documentation
```

## How to Run

1. **Install Dependencies**:
   Ensure you have Python installed along with the `pygame` library. You can install `pygame` using:
   ```bash
   pip install pygame
   ```

2. **Run the Game**:
   Execute the `storyline.py` file to start the storyline system:
   ```bash
   python storyline.py
   ```

3. **Navigate Through the Story**:
   - Press `SPACE` to move to the next slide.
   - Press `ESC` to exit the storyline.

## Adding New Levels

To add a new level:
1. Create a new function in `storyline.py` (e.g., `play_levelX_story`).
2. Define a list of `StorySlide` objects with the appropriate image, text, and voiceover paths.
3. Add the function to the `storyline_functions` dictionary in the `play_level_story` function.

Example:
```python
def play_levelX_story(screen):
    levelX_slides = [
        StorySlide("assets/story/levelX_1.png", "Your custom story text here.", "scenes/levelX_1.mp3"),
        # Add more slides as needed
    ]
    return play_story_sequence(screen, levelX_slides)
```

## Dependencies

- Python 3.7+
- `pygame` library

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Credits

- **Developer**: Saiprasad, Sahil, Krishnakant, Rajnish
- **Assets**: Images and audio files used in the storyline are placeholders and should be replaced with your own assets.