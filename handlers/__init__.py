from handlers.start import register_handlers as register_start_handlers
from handlers.profile import register_handlers as register_profile_handlers
from handlers.ideas import register_handlers as register_ideas_handlers
from handlers.admin import register_handlers as register_admin_handlers

__all__ = [
    'register_start_handlers',
    'register_profile_handlers',
    'register_ideas_handlers',
    'register_admin_handlers'
]