import socket

def is_online():
    """Check if the device has an active internet connection."""
    try:
        with socket.create_connection(("8.8.8.8", 53), timeout=3):
            return True
    except OSError:
        return False
