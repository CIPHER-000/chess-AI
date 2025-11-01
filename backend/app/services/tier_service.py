"""
Tier Management Service for handling Free vs Pro user logic.
"""
from datetime import datetime, timezone
from typing import Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger

from ..models.user import User


class TierService:
    """Service for managing user subscription tiers and limits."""
    
    # Tier limits configuration
    FREE_AI_ANALYSIS_LIMIT = 5
    PRO_AI_ANALYSIS_LIMIT = -1  # Unlimited
    
    def __init__(self, db: Session):
        self.db = db
    
    def can_use_ai_analysis(self, user: User) -> bool:
        """
        Check if user can use AI-powered analysis.
        
        Args:
            user: User model instance
            
        Returns:
            True if user can use AI analysis, False otherwise
        """
        if user.is_pro:
            return True
        
        # Free user with trial remaining
        return user.ai_analyses_used < user.ai_analyses_limit
    
    def get_tier_status(self, user: User) -> Dict:
        """
        Get comprehensive tier status for user.
        
        Args:
            user: User model instance
            
        Returns:
            Dictionary with tier information
        """
        return {
            "tier": user.tier,
            "is_pro": user.is_pro,
            "can_use_ai": self.can_use_ai_analysis(user),
            "ai_analyses_used": user.ai_analyses_used,
            "ai_analyses_limit": user.ai_analyses_limit,
            "remaining_ai_analyses": user.remaining_ai_analyses,
            "trial_exhausted": user.ai_analyses_used >= user.ai_analyses_limit and not user.is_pro,
            "trial_exhausted_at": user.trial_exhausted_at.isoformat() if user.trial_exhausted_at else None
        }
    
    def increment_ai_usage(self, user: User) -> bool:
        """
        Increment AI analysis usage counter for user.
        
        Args:
            user: User model instance
            
        Returns:
            True if increment was successful, False if limit reached
        """
        if user.is_pro:
            # Pro users have unlimited usage
            logger.info(f"Pro user {user.chesscom_username} using AI analysis (unlimited)")
            return True
        
        if user.ai_analyses_used >= user.ai_analyses_limit:
            logger.warning(
                f"Free user {user.chesscom_username} has exhausted AI analysis trial "
                f"({user.ai_analyses_used}/{user.ai_analyses_limit})"
            )
            return False
        
        # Increment usage
        user.ai_analyses_used += 1
        
        # Mark trial as exhausted if limit reached
        if user.ai_analyses_used >= user.ai_analyses_limit and not user.trial_exhausted_at:
            user.trial_exhausted_at = datetime.now(timezone.utc)
            logger.info(
                f"Free user {user.chesscom_username} has exhausted AI analysis trial "
                f"({user.ai_analyses_used}/{user.ai_analyses_limit})"
            )
        else:
            logger.info(
                f"Free user {user.chesscom_username} AI analysis usage: "
                f"{user.ai_analyses_used}/{user.ai_analyses_limit}"
            )
        
        self.db.commit()
        return True
    
    def upgrade_to_pro(self, user: User) -> None:
        """
        Upgrade user to Pro tier.
        
        Args:
            user: User model instance
        """
        user.tier = "pro"
        user.ai_analyses_limit = -1  # Unlimited
        logger.info(f"User {user.chesscom_username} upgraded to Pro tier")
        self.db.commit()
    
    def downgrade_to_free(self, user: User, reset_trial: bool = False) -> None:
        """
        Downgrade user to Free tier.
        
        Args:
            user: User model instance
            reset_trial: Whether to reset trial counter
        """
        user.tier = "free"
        user.ai_analyses_limit = self.FREE_AI_ANALYSIS_LIMIT
        
        if reset_trial:
            user.ai_analyses_used = 0
            user.trial_exhausted_at = None
            logger.info(f"User {user.chesscom_username} downgraded to Free tier (trial reset)")
        else:
            logger.info(f"User {user.chesscom_username} downgraded to Free tier")
        
        self.db.commit()
    
    def get_upgrade_message(self, user: User) -> Optional[str]:
        """
        Get appropriate upgrade message for user based on their tier status.
        
        Args:
            user: User model instance
            
        Returns:
            Upgrade message or None if user is Pro
        """
        if user.is_pro:
            return None
        
        if user.ai_analyses_used >= user.ai_analyses_limit:
            return (
                "🎯 You've used all your free AI analyses! "
                "Upgrade to Pro for unlimited AI coaching and YouTube recommendations."
            )
        
        remaining = user.remaining_ai_analyses
        return (
            f"💡 You have {remaining} AI analysis trial{'s' if remaining != 1 else ''} remaining. "
            "Upgrade to Pro for unlimited access!"
        )


# Factory function
def get_tier_service(db: Session) -> TierService:
    """Get TierService instance with database session."""
    return TierService(db)
