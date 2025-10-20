"""Supabase client initialization and utilities."""
import os
from typing import Optional
from supabase import create_client, Client
from supabase_auth import SyncGoTrueClient
from loguru import logger

from .config import settings


class SupabaseClient:
    """Singleton Supabase client manager."""
    
    _instance: Optional[Client] = None
    _auth_client: Optional[SyncGoTrueClient] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance."""
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_ANON_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
        return cls._instance
    
    @classmethod
    def get_admin_client(cls) -> Client:
        """Get Supabase client with service role key for admin operations."""
        try:
            admin_client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
            )
            logger.info("Supabase admin client initialized")
            return admin_client
        except Exception as e:
            logger.error(f"Failed to initialize Supabase admin client: {e}")
            raise
    
    @classmethod
    def get_auth_client(cls) -> SyncGoTrueClient:
        """Get GoTrue auth client for authentication operations."""
        if cls._auth_client is None:
            client = cls.get_client()
            cls._auth_client = client.auth
        return cls._auth_client


# Convenience function for getting the client
def get_supabase() -> Client:
    """Get Supabase client instance."""
    return SupabaseClient.get_client()


def get_supabase_admin() -> Client:
    """Get Supabase admin client instance."""
    return SupabaseClient.get_admin_client()
