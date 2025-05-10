from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Any, Dict, Optional, List
from datetime import date as dt_date
import asyncpg
import json

from backend.database import get_connection
from backend.utils.textutils import normalize_domain 

router = APIRouter(tags=["analysis"])

@router.get("/cross-source-analysis")
async def get_cross_source_analysis(
    date: Optional[dt_date] = Query(default=None, description="Date to retrieve analysis for (default: today)"),
    language: str = Query(default="hu", description="Language code (hu, en)"),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Retrieve the cross-source news analysis for a specific date.
    
    The analysis compares how different Hungarian news sources cover the same topics,
    highlighting differences in sentiment, political leaning, and framing.
    
    Returns:
        - JSON object containing unified topics across sources
        - Each topic includes coverage from different sources
        - Comparative analysis of how each topic is presented by different media outlets
    """
    current_date = date if date is not None else dt_date.today()

    if language not in ["hu", "en"]:
        language = "hu" #Default
    
    try:
        # Query the cross_source_analyses table
        row = await conn.fetchrow('''
            SELECT 
                id,
                date,
                analysis_json,
                language
                created_at
            FROM 
                cross_source_analyses
            WHERE 
                date = $1 AND
                language = $2
            ORDER BY 
                created_at DESC
            LIMIT 1
        ''', current_date, language)
        
        if not row:
            # If no analysis for the requested date, try to find the most recent one
            row = await conn.fetchrow('''
                SELECT 
                    id,
                    date,
                    analysis_json,
                    language,
                    created_at
                FROM 
                    cross_source_analyses
                WHERE
                    language = $1
                ORDER BY 
                    date DESC, created_at DESC
                LIMIT 1
            ''')
            
            if not row:
                return {
                    "success": False,
                    "message": "No cross-source analysis found in the database",
                    "date": current_date.isoformat(),
                    "analysis": None
                }
        
        # Parse the JSON data
        analysis_data = json.loads(row['analysis_json'])

        # Normalize domain names in the data
        if "unified_topics" in analysis_data:
            for topic in analysis_data["unified_topics"]:
                if "source_coverage" in topic:
                    for source in topic["source_coverage"]:
                        if "domain" in source:
                            source["domain"] = normalize_domain(source["domain"])
        
        return {
            "success": True,
            "date": row['date'].isoformat(),
            "analysis": analysis_data,
            "language": row['language'],
            "created_at": row['created_at'].isoformat() if row['created_at'] else None,
            "requested_date": current_date.isoformat() if current_date != row['date'] else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch cross-source analysis: {str(e)}"
        )

@router.get("/unified-topics")
async def get_unified_topics(
    date: Optional[dt_date] = Query(default=None, description="Date to retrieve topics for (default: today)"),
    language: str = Query(default="hu", description="Language code (hu, en)"),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Retrieve just the list of unified topics for a specific date.
    
    This is a simplified endpoint that returns only the topic names without the full analysis details.
    """
    current_date = date if date is not None else dt_date.today()

    if language not in ["hu", "en"]:
        language = "hu" #Default
    
    try:
        # Query the cross_source_analyses table
        row = await conn.fetchrow('''
            SELECT 
                analysis_json
            FROM 
                cross_source_analyses
            WHERE 
                date = $1 AND
                language = $2
            ORDER BY 
                created_at DESC
            LIMIT 1
        ''', current_date, language)
        
        if not row:
            return {
                "success": False,
                "message": f"No analysis found for date {current_date.isoformat()}",
                "topics": []
            }
        
        # Parse the JSON data and extract just the topic names
        analysis_data = json.loads(row['analysis_json'])
        topics = []
        
        if "unified_topics" in analysis_data:
            for topic in analysis_data["unified_topics"]:
                sources = [source["domain"] for source in topic.get("source_coverage", [])]
                topics.append({
                    "name": topic["name"],
                    "sources": sources,
                    "source_count": len(sources)
                })
        
        return {
            "success": True,
            "date": current_date.isoformat(),
            "topics": topics,
            "language": language,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch unified topics: {str(e)}"
        )

@router.get("/topic-coverage/{topic_name}")
async def get_topic_coverage(
    topic_name: str,
    date: Optional[dt_date] = Query(default=None, description="Date to retrieve topic coverage for (default: today)"),
    language: str = Query(default="hu", description="Language code (hu, en)"),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Retrieve detailed coverage information for a specific topic.
    
    Returns how different news sources covered the specified topic, 
    including sentiment, political leaning, and key phrases used.
    """
    current_date = date if date is not None else dt_date.today()
    
    if language not in ["hu", "en"]:
        language = "hu" #Default
    
    try:
        # Query the cross_source_analyses table
        row = await conn.fetchrow('''
            SELECT 
                analysis_json
            FROM 
                cross_source_analyses
            WHERE 
                date = $1 AND
                language = $2
            ORDER BY 
                created_at DESC
            LIMIT 1
        ''', current_date, language)
        
        if not row:
            return {
                "success": False,
                "message": f"No analysis found for date {current_date.isoformat()}",
                "topic": None,
                "coverage": []
            }
        
        # Parse the JSON data and find the requested topic
        analysis_data = json.loads(row['analysis_json'])
        
        for topic in analysis_data.get("unified_topics", []):
            # Case-insensitive partial matching for topic name
            if topic_name.lower() in topic["name"].lower():
                return {
                    "success": True,
                    "date": current_date.isoformat(),
                    "topic": topic["name"],
                    "coverage": topic.get("source_coverage", []),
                    "comparative_analysis": topic.get("comparative_analysis", ""),
                    "language": language,
                }
        
        return {
            "success": False,
            "message": f"Topic '{topic_name}' not found for date {current_date.isoformat()}",
            "topic": topic_name,
            "coverage": []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch topic coverage: {str(e)}"
        )