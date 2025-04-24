# ai_model/__init__.py

# Import submodules to make them available at the package level
from .collaborative_filtering import CollaborativeFiltering
from .content_based import ContentBasedRecommender
from .clustering import UserClustering
from .reinforcement_learning import TravelReinforcementLearner

# Define package-level variables or metadata
__version__ = '1.0.0'
__all__ = [
    'CollaborativeFiltering',
    'ContentBasedRecommender',
    'UserClustering',
    'TravelReinforcementLearner'
]

# Optional: Perform any package-level initialization if necessary
# For example, setting up a logger for the package
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("ai_model package initialized.")
