import time
import json
from datetime import datetime
import threading
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import signal
import sys
import math

# Configurable hotkeys
HOTKEYS = {
    'start_recording': Key.f7,
    'stop_recording': Key.f6,
    'replay_recording': Key.f8,
    'quit_program': keyboard.KeyCode.from_char('q')
}

class InputRecorder:
    def __init__(self):
        self.recorded_keys = []
        self.start_time = None
        self.is_recording = False
        self.output_file = "keyboard_recording.json"
        self.pressed_keys = {}
        self.pressed_mouse_buttons = {}
        self.running = True
        self.last_mouse_position = None
        self.last_mouse_time = None
        self.is_mouse_moving = False
        self.mouse_move_start_time = None
        self.mouse_move_start_pos = None
        
        # Initialize controllers
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()
        
        # Initialize listeners
        self.keyboard_listener = None
        self.mouse_listener = None

    def get_current_time(self):
        """Get current time in high precision"""
        return time.perf_counter()

    def on_key_press(self, key):
        if not self.is_recording:
            return
            
        current_time = self.get_current_time()
        relative_time = current_time - self.start_time

        try:
            # Convert key to string representation
            key_char = key.char if hasattr(key, 'char') else str(key)
            
            if key_char not in self.pressed_keys:
                self.pressed_keys[key_char] = relative_time
                print(f"Key pressed: {key_char} at {relative_time:.6f}s")
        except AttributeError:
            pass

    def on_key_release(self, key):
        if not self.is_recording:
            return
            
        current_time = self.get_current_time()
        relative_time = current_time - self.start_time

        try:
            # Convert key to string representation
            key_char = key.char if hasattr(key, 'char') else str(key)
            
            if key_char in self.pressed_keys:
                press_time = self.pressed_keys.pop(key_char)
                duration = relative_time - press_time
                
                key_info = {
                    'key': key_char,
                    'press_time': round(press_time, 6),
                    'release_time': round(relative_time, 6),
                    'duration': round(duration, 6)
                }
                self.recorded_keys.append(key_info)
                print(f"Key released: {key_char} - Duration: {duration:.6f}s")
        except AttributeError:
            pass

    def on_mouse_click(self, x, y, button, pressed):
        if not self.is_recording:
            return
            
        current_time = self.get_current_time()
        relative_time = current_time - self.start_time

        # Convert button to string name
        if button == Button.left:
            button_name = 'left'
        elif button == Button.right:
            button_name = 'right'
        else:
            button_name = str(button)
        
        if pressed and button_name not in self.pressed_mouse_buttons:
            self.pressed_mouse_buttons[button_name] = relative_time
            print(f"Mouse {button_name} pressed at {relative_time:.6f}s")
            
        elif not pressed and button_name in self.pressed_mouse_buttons:
            press_time = self.pressed_mouse_buttons.pop(button_name)
            duration = relative_time - press_time
            
            click_info = {
                'key': f'mouse_{button_name}',
                'press_time': round(press_time, 6),
                'release_time': round(relative_time, 6),
                'duration': round(duration, 6)
            }
            self.recorded_keys.append(click_info)
            print(f"Mouse {button_name} released - Duration: {duration:.6f}s")

    def on_mouse_scroll(self, x, y, dx, dy):
        if not self.is_recording:
            return
            
        current_time = self.get_current_time()
        relative_time = current_time - self.start_time

        scroll_info = {
            'key': 'scroll',
            'direction': 'up' if dy > 0 else 'down',
            'press_time': round(relative_time, 6),
            'release_time': round(relative_time, 6),
            'duration': 0.0
        }
        self.recorded_keys.append(scroll_info)
        print(f"Mouse scrolled {scroll_info['direction']} at {relative_time:.6f}s")

    def on_mouse_move(self, x, y):
        if not self.is_recording:
            return
            
        current_time = self.get_current_time()
        relative_time = current_time - self.start_time

        # If mouse wasn't moving before, this is the start of movement
        if not self.is_mouse_moving:
            self.is_mouse_moving = True
            self.mouse_move_start_time = current_time
            self.mouse_move_start_pos = (x, y)
            print(f"Mouse movement started at ({x}, {y})")
            return

        # Check if mouse has stopped moving (no movement for 0.1 seconds)
        if self.last_mouse_position is not None:
            dx = x - self.last_mouse_position[0]
            dy = y - self.last_mouse_position[1]
            time_diff = current_time - self.last_mouse_time
            
            # If mouse has stopped moving (very small movement)
            if abs(dx) < 2 and abs(dy) < 2 and time_diff > 0.1:
                if self.is_mouse_moving:
                    self.is_mouse_moving = False
                    total_time = current_time - self.mouse_move_start_time
                    total_distance = ((x - self.mouse_move_start_pos[0])**2 + 
                                   (y - self.mouse_move_start_pos[1])**2)**0.5
                    avg_speed = total_distance / total_time if total_time > 0 else 0
                    direction = math.atan2(y - self.mouse_move_start_pos[1],
                                        x - self.mouse_move_start_pos[0])
                    
                    move_info = {
                        'key': 'mouse_move',
                        'start_x': self.mouse_move_start_pos[0],
                        'start_y': self.mouse_move_start_pos[1],
                        'end_x': x,
                        'end_y': y,
                        'total_distance': total_distance,
                        'avg_speed': avg_speed,
                        'direction': direction,
                        'duration': round(total_time, 6),
                        'time': round(relative_time - total_time, 6)
                    }
                    self.recorded_keys.append(move_info)
                    print(f"Mouse movement ended: Distance: {total_distance:.1f}px, "
                          f"Avg Speed: {avg_speed:.1f}px/s, "
                          f"Direction: {math.degrees(direction):.1f}°")

        self.last_mouse_position = (x, y)
        self.last_mouse_time = current_time

    def start_recording(self):
        self.recorded_keys = []
        self.pressed_keys = {}
        self.pressed_mouse_buttons = {}
        self.last_mouse_position = None
        self.last_mouse_time = None
        self.is_mouse_moving = False
        self.mouse_move_start_time = None
        self.mouse_move_start_pos = None
        self.start_time = self.get_current_time()
        self.is_recording = True
        
        # Start listeners
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release)
        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll,
            on_move=self.on_mouse_move)
            
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        print("Recording started... Press 'F6' to stop recording.")

    def stop_recording(self):
        self.is_recording = False
        
        # Stop listeners
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        # Handle any remaining pressed keys/buttons
        current_time = self.get_current_time()
        relative_time = current_time - self.start_time
        
        for key, press_time in self.pressed_keys.items():
            key_info = {
                'key': key,
                'press_time': round(press_time, 6),
                'release_time': round(relative_time, 6),
                'duration': round(relative_time - press_time, 6)
            }
            self.recorded_keys.append(key_info)
            
        for button, press_time in self.pressed_mouse_buttons.items():
            click_info = {
                'key': f'mouse_{button}',
                'press_time': round(press_time, 6),
                'release_time': round(relative_time, 6),
                'duration': round(relative_time - press_time, 6)
            }
            self.recorded_keys.append(click_info)
            
        self.pressed_keys = {}
        self.pressed_mouse_buttons = {}
        
        if self.recorded_keys:
            # Sort recordings by time, handling both press_time and time fields
            def get_event_time(event):
                return event.get('press_time', event.get('time', 0))
            
            self.recorded_keys.sort(key=get_event_time)
            
            # Save to file
            with open(self.output_file, 'w') as f:
                json.dump(self.recorded_keys, f, indent=2)
            print(f"\nRecording saved to {self.output_file}")
            self.analyze_recording()
        else:
            print("\nNo keys were recorded.")

    def analyze_recording(self):
        if not self.recorded_keys:
            return

        # Calculate statistics
        total_duration = self.recorded_keys[-1]['release_time']
        key_stats = {}
        
        for record in self.recorded_keys:
            key = record['key']
            if key not in key_stats:
                key_stats[key] = {
                    'count': 0,
                    'total_duration': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0
                }
            
            stats = key_stats[key]
            duration = record['duration']
            stats['count'] += 1
            stats['total_duration'] += duration
            stats['min_duration'] = min(stats['min_duration'], duration)
            stats['max_duration'] = max(stats['max_duration'], duration)

        print("\nRecording Analysis:")
        print(f"Total duration: {total_duration:.2f} seconds")
        print(f"Total key events: {len(self.recorded_keys)}")
        print("\nKey Statistics:")
        
        for key, stats in key_stats.items():
            avg_duration = stats['total_duration'] / stats['count']
            print(f"\nKey: {key}")
            print(f"  Press count: {stats['count']}")
            print(f"  Average duration: {avg_duration:.6f}s")
            print(f"  Min duration: {stats['min_duration']:.6f}s")
            print(f"  Max duration: {stats['max_duration']:.6f}s")

    def load_recording(self):
        """Load the recording from the JSON file"""
        try:
            with open(self.output_file, 'r') as f:
                self.recorded_keys = json.load(f)
            print(f"Loaded recording from {self.output_file}")
            print(f"Total events: {len(self.recorded_keys)}")
            return True
        except FileNotFoundError:
            print(f"No recording file found at {self.output_file}")
            return False
        except json.JSONDecodeError:
            print(f"Error reading recording file {self.output_file}")
            return False

    def replay_recording(self, speed_multiplier=1.0):
        # Try to load the recording if we don't have any events
        if not self.recorded_keys:
            if not self.load_recording():
                print("No recording to replay!")
                return

        print(f"Replaying recording at {speed_multiplier}x speed...")
        print("Press 'ESC' to stop replay")
        
        # Wait for 3 seconds before starting replay
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)

        replay_start_time = self.get_current_time()
        active_keys = set()
        active_mouse_buttons = set()

        def smooth_mouse_move(start_x, start_y, end_x, end_y, duration):
            """Move mouse smoothly from start to end position"""
            steps = 60  # Number of steps for smooth movement
            for i in range(steps + 1):
                if keyboard.Key.esc in active_keys:
                    return
                t = i / steps
                # Use easing function for more natural movement
                t = t * t * (3 - 2 * t)  # Smoothstep interpolation
                current_x = start_x + (end_x - start_x) * t
                current_y = start_y + (end_y - start_y) * t
                self.mouse_controller.position = (int(current_x), int(current_y))
                time.sleep(duration / steps)

        try:
            # Group events by their press time to handle simultaneous inputs
            events_by_time = {}
            for event in self.recorded_keys:
                press_time = event['press_time'] if 'press_time' in event else event['time']
                if press_time not in events_by_time:
                    events_by_time[press_time] = []
                events_by_time[press_time].append(event)

            # Sort press times
            press_times = sorted(events_by_time.keys())

            for press_time in press_times:
                if keyboard.Key.esc in active_keys:
                    print("Replay stopped by user")
                    break

                # Calculate the adjusted wait time
                current_time = self.get_current_time() - replay_start_time
                target_time = press_time / speed_multiplier
                
                # Wait until it's time for these events
                if target_time > current_time:
                    time.sleep(target_time - current_time)

                # Handle all events that should occur at this time
                current_events = events_by_time[press_time]
                for event in current_events:
                    if event['key'] == 'scroll':
                        # Handle scroll wheel events
                        print(f"Replaying: Scrolling {event['direction']} at {self.get_current_time() - replay_start_time:.6f}s")
                        self.mouse_controller.scroll(0, 1 if event['direction'] == 'up' else -1)
                    elif event['key'] == 'mouse_move':
                        # Handle mouse movement events with smooth animation
                        print(f"Replaying: Moving mouse from ({event['start_x']}, {event['start_y']}) to ({event['end_x']}, {event['end_y']}) at {self.get_current_time() - replay_start_time:.6f}s")
                        smooth_mouse_move(
                            event['start_x'], event['start_y'],
                            event['end_x'], event['end_y'],
                            event['duration'] / speed_multiplier
                        )
                    elif event['key'].startswith('mouse_'):
                        # Handle mouse click events
                        button_name = event['key'].split('_')[1]
                        if button_name == 'left':
                            button = Button.left
                        elif button_name == 'right':
                            button = Button.right
                        else:
                            button = getattr(Button, button_name)
                            
                        print(f"Replaying: Clicking mouse {button_name} at {self.get_current_time() - replay_start_time:.6f}s")
                        self.mouse_controller.press(button)
                        active_mouse_buttons.add(button)
                        
                        # Schedule mouse release
                        def release_mouse_with_log(button):
                            print(f"Replaying: Releasing mouse {button} at {self.get_current_time() - replay_start_time:.6f}s")
                            try:
                                self.mouse_controller.release(button)
                                active_mouse_buttons.discard(button)
                            except:
                                pass
                        
                        threading.Timer(event['duration'] / speed_multiplier, release_mouse_with_log, args=[button]).start()
                    else:
                        # Handle keyboard events
                        key_str = event['key']
                        print(f"Replaying: Pressing {key_str} at {self.get_current_time() - replay_start_time:.6f}s")
                        
                        # Convert string key to Key object if needed
                        try:
                            # Handle special keys
                            if key_str.startswith('Key.'):
                                key_obj = getattr(Key, key_str[4:])  # Remove 'Key.' prefix
                            else:
                                key_obj = key_str
                            
                            self.keyboard_controller.press(key_obj)
                            active_keys.add(key_obj)
                            
                            # Schedule key release
                            def release_key_with_log(key_obj):
                                print(f"Replaying: Releasing {key_obj} at {self.get_current_time() - replay_start_time:.6f}s")
                                try:
                                    self.keyboard_controller.release(key_obj)
                                    active_keys.discard(key_obj)
                                except:
                                    pass
                            
                            threading.Timer(event['duration'] / speed_multiplier, release_key_with_log, args=[key_obj]).start()
                        except Exception as e:
                            print(f"Error handling key {key_str}: {str(e)}")
                
        finally:
            # Clean up: release any keys that might still be pressed
            print("Cleaning up: releasing any remaining pressed keys")
            for key in active_keys.copy():
                try:
                    self.keyboard_controller.release(key)
                    print(f"Released remaining key: {key}")
                except:
                    pass
            
            # Clean up: release any mouse buttons that might still be pressed
            print("Cleaning up: releasing any remaining pressed mouse buttons")
            for button in active_mouse_buttons.copy():
                try:
                    self.mouse_controller.release(button)
                    print(f"Released remaining mouse button: {button}")
                except:
                    pass
            
            print("\nReplay completed!")
            print("\nAvailable commands:")
            print(f"{HOTKEYS['start_recording']} - Start Recording")
            print(f"{HOTKEYS['stop_recording']} - Stop Recording")
            print(f"{HOTKEYS['replay_recording']} - Replay Last Recording")
            print(f"{HOTKEYS['quit_program']} - Quit Program")

    def cleanup(self):
        """Clean up any pressed keys or mouse buttons"""
        print("\nCleaning up...")
        # Release any pressed keys
        for key in self.pressed_keys.copy():
            try:
                self.keyboard_controller.release(key)
            except:
                pass
        
        # Release any pressed mouse buttons
        for button in self.pressed_mouse_buttons.copy():
            try:
                self.mouse_controller.release(button)
            except:
                pass
        
        # Stop listeners if they're running
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        self.running = False

def main():
    recorder = InputRecorder()
    
    def signal_handler(signum, frame):
        print("\nReceived exit signal. Cleaning up...")
        recorder.cleanup()
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Improved Input Recorder")
    print("----------------------")
    print(f"{HOTKEYS['start_recording']} - Start Recording")
    print(f"{HOTKEYS['stop_recording']} - Stop Recording")
    print(f"{HOTKEYS['replay_recording']} - Replay Last Recording")
    print(f"{HOTKEYS['quit_program']} - Quit Program")
    print("Ctrl+C - Emergency Exit")

    # Try to load any existing recording
    recorder.load_recording()

    def on_press(key):
        try:
            if key == HOTKEYS['start_recording']:
                recorder.start_recording()
            elif key == HOTKEYS['replay_recording']:
                recorder.replay_recording()
        except AttributeError:
            pass

    def on_release(key):
        try:
            if key == HOTKEYS['stop_recording'] and recorder.is_recording:
                recorder.stop_recording()
            elif key == HOTKEYS['quit_program']:
                print("\nQuitting program...")
                recorder.cleanup()
                return False  # Stop listener
        except AttributeError:
            pass

    # Set up keyboard listener
    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    
    keyboard_listener.start()
    
    try:
        # Keep the program running until 'q' is pressed or Ctrl+C is received
        while recorder.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nReceived Ctrl+C. Cleaning up...")
        recorder.cleanup()
    finally:
        print("Program terminated.")

if __name__ == "__main__":
    main()
