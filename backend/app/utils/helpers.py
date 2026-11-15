"""Phase 1 placeholder utilities.

These utilities will be populated in later phases.
"""


def format_bytes(size: int, suffix: str = 'B') -> str:
    """Format a byte size into a human-readable string."""
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(size) < 1024:
            return f'{size:3.1f} {unit}{suffix}'
        size /= 1024
    return f'{size:3.1f} Y{suffix}'


def generate_embedding(text: str) -> list:
    """Generate an embedding for the given text.

    Phase 1 placeholder. Full embedding provider integration is in Phase 2.
    """
    raise NotImplementedError('Embedding generation is not implemented in Phase 1.')
