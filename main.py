#!/usr/bin/env python3

import time
import subprocess
import dbus
import sys

# Define the target application
APP_NAME = "WEBRTC VoiceEngine"
# Define the desired volume levels
VOL_LISTENING = 15
VOL_NOT_LISTENING = 50

# Flag to track if Player is currently listening
is_listening = False

def get_player_sink_input_id():
    """
    Finds the PulseAudio sink input ID for Player.
    """
    try:
        # Use pactl to list sink inputs and find Player's
        pactl_output = subprocess.check_output(['pactl', 'list', 'sink-inputs'], text=True)
        lines = pactl_output.splitlines()

        for i, line in enumerate(lines):
            if "Sink Input #" in line:
                # Get the sink input ID
                sink_input_id = line.strip().split('#')[1]
            elif f"application.name = \"{APP_NAME}\"" in line:
                # Find the application name and return the ID
                return sink_input_id
    except (subprocess.CalledProcessError, IndexError):
        return None

def set_volume(volume):
    """
    Sets the volume for media using playerctl.
    """
    print(f"Setting Player volume to {volume}...")
    try:
        # Check if Player is running
        subprocess.check_output(['playerctl', 'status'])
        # Set the volume
        subprocess.run(['playerctl', 'volume', str(volume / 100)], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Player is not running or playerctl is not installed. Skipping volume change.")

def main():
    """
    Main loop to monitor PulseAudio and adjust Player volume.
    """
    global is_listening
    print("Starting Player microphone monitor daemon...")

    while True:
        try:
            # Check for Player's sink input
            player_id = get_player_sink_input_id()

            if player_id and not is_listening:
                # Player is now listening, lower the volume
                print(f"Player sink input detected: {player_id}. Lowering volume.")
                set_volume(VOL_LISTENING)
                is_listening = True
            elif not player_id and is_listening:
                # Player is no longer listening, raise the volume
                print("Player sink input no longer detected. Raising volume.")
                set_volume(VOL_NOT_LISTENING)
                is_listening = False

        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            # Raise an error to the stderr so it can be logged by the systemd daemon
            sys.stderr.write(str(e) + '\n')

        # Wait a few seconds before checking again
        time.sleep(2)

if __name__ == "__main__":
    main()