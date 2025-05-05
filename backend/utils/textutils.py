from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Any, Dict, Optional, List
from datetime import date as dt_date
import asyncpg
import json
import unicodedata
import re

from backend.database import get_connection

def normalize_domain(domain: str) -> str:
    """
    Normalize a domain name by:
    1. Removing TLDs (.hu, .com, etc.)
    2. Converting to lowercase
    3. Removing accents (ékezetek)
    4. Handling special cases
    """
    if not domain:
        return ""
        
    # Handle special case for 24.hu (keep the dot)
    if domain.startswith("24."):
        return "24.hu"
        
    # Remove http(s):// if present
    domain = re.sub(r'^https?:\/\/', '', domain)
    
    # Remove www. if present
    domain = re.sub(r'^www\.', '', domain)
    
    # Remove TLD (.hu, .com, etc.)
    domain = re.sub(r'\.\w+$', '', domain)
    
    # Convert to lowercase
    domain = domain.lower()
    
    # Remove accents
    domain = ''.join(c for c in unicodedata.normalize('NFD', domain)
                     if unicodedata.category(c) != 'Mn')
                     
    return domain