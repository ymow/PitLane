"""
Shared utility functions for PitLane project.
"""
import uuid


def generate_id():
    """
    Generate a custom 25-character UUID for database IDs.
    This is a consistent ID generation strategy used across all models.
    """
    return uuid.uuid4().hex[:25]
