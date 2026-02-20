"""
Shared utility functions for PitLane project.
"""
import uuid


def generate_id():
    """
    Generate a standard 32-character UUID for database IDs.
    This ensures global uniqueness across historical and social data scales.
    """
    return uuid.uuid4().hex
