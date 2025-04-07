# Macro Recorder

A Python-based macro recorder that captures and replays keyboard and mouse actions with high precision timing and smooth mouse movements.

## Features

- **Keyboard Recording**
  - Captures all keyboard inputs including special keys
  - Records precise timing of key presses and releases
  - Supports simultaneous key combinations

- **Mouse Recording**
  - Tracks mouse movements with smooth animation
  - Records mouse clicks (left and right)
  - Captures mouse scroll events
  - Natural movement simulation during replay

- **High Precision Timing**
  - Microsecond-level timing precision
  - Accurate event synchronization
  - Smooth playback of recorded actions

- **User-Friendly Controls**
  - Configurable hotkeys for all actions
  - Default hotkeys:
    - F7: Start Recording
    - F6: Stop Recording
    - F8: Replay Last Recording
    - Q: Quit Program
  - Ctrl+C: Emergency Exit

## Demo

![Macro Recorder Demo](demo.gif)

*Demo showing recording and replaying mouse movements and keyboard inputs*

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SimronJ/macro-recorder
cd macro-recorder
```

2. Install the required dependency:
```bash
pip install pynput
```

## Usage

1. Run the script:
```bash
python recordMacro.py
```

2. Recording:
   - Press the Start Recording hotkey (default: F7)
   - Perform your actions (keyboard and mouse)
   - Press the Stop Recording hotkey (default: F6)
   - The recording will be saved to `keyboard_recording.json`

3. Replay:
   - Press the Replay hotkey (default: F8)
   - The script will replay your actions with the same timing and movements

## Customizing Hotkeys

You can easily change the hotkeys by modifying the `HOTKEYS` dictionary at the top of the `recordMacro.py` file:

```python
HOTKEYS = {
    'start_recording': Key.f7,
    'stop_recording': Key.f6,
    'replay_recording': Key.f8,
    'quit_program': Key.q
}
```

Replace the key values with your preferred keys from the `pynput.keyboard.Key` class.

## Features in Detail

### Mouse Movement
- Tracks start and end positions of movements
- Calculates movement speed and direction
- Simulates natural mouse movement during replay
- Supports smooth acceleration and deceleration

### Keyboard Input
- Records all keyboard events
- Maintains precise timing between key presses
- Supports special keys and combinations
- Handles simultaneous key presses

### Recording Format
- Saves recordings in JSON format
- Includes precise timing information
- Stores mouse movement trajectories
- Maintains event order and synchronization

## Requirements

- Python 3.6 or higher
- pynput library for input capture

## Notes

- The script requires appropriate permissions to capture keyboard and mouse input
- Some systems may require running with administrator privileges
- Recordings are saved in the same directory as the script

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 