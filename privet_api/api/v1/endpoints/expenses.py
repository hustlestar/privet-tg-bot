"""Expense tracking and analytics endpoints."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta

from privet_api.api.deps import get_api_usage_repository
from privet_api.repositories.api_usage_repository import APIUsageRepository

router = APIRouter()


@router.get("/cost-breakdown")
async def get_cost_breakdown(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    usage_repo: APIUsageRepository = Depends(get_api_usage_repository)
) -> Dict[str, Any]:
    """Get cost breakdown by service, provider, and model."""
    
    try:
        breakdown = await usage_repo.get_cost_breakdown(user_id=user_id, days=days)
        return {
            "status": "success",
            "data": breakdown,
            "period": {
                "days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cost breakdown: {str(e)}"
        )


@router.get("/total-costs")
async def get_total_costs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    usage_repo: APIUsageRepository = Depends(get_api_usage_repository)
) -> Dict[str, Any]:
    """Get total costs and usage statistics."""
    
    try:
        totals = await usage_repo.get_total_costs(user_id=user_id, days=days)
        return {
            "status": "success",
            "data": totals,
            "period": {
                "days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching total costs: {str(e)}"
        )


@router.get("/usage-stats")
async def get_usage_stats(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    usage_repo: APIUsageRepository = Depends(get_api_usage_repository)
) -> Dict[str, Any]:
    """Get detailed usage statistics."""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        stats = await usage_repo.get_usage_stats(
            user_id=user_id,
            service_type=service_type,
            provider=provider,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "status": "success",
            "data": stats,
            "filters": {
                "user_id": user_id,
                "service_type": service_type,
                "provider": provider
            },
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching usage stats: {str(e)}"
        )


@router.get("/recent-usage")
async def get_recent_usage(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=500, description="Number of records to return"),
    usage_repo: APIUsageRepository = Depends(get_api_usage_repository)
) -> Dict[str, Any]:
    """Get recent API usage records."""
    
    try:
        records = await usage_repo.get_recent_usage(user_id=user_id, limit=limit)
        return {
            "status": "success",
            "data": records,
            "count": len(records),
            "filters": {
                "user_id": user_id,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recent usage: {str(e)}"
        )


@router.get("/models")
async def get_model_usage(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    usage_repo: APIUsageRepository = Depends(get_api_usage_repository)
) -> Dict[str, Any]:
    """Get usage breakdown by model."""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        stats = await usage_repo.get_usage_stats(
            start_date=start_date,
            end_date=end_date
        )
        
        # Group by model
        model_stats = {}
        for stat in stats:
            model = stat['model']
            if model not in model_stats:
                model_stats[model] = {
                    'model': model,
                    'provider': stat['provider'],
                    'service_type': stat['service_type'],
                    'total_requests': 0,
                    'total_cost': 0.0,
                    'total_tokens': 0
                }
            
            model_stats[model]['total_requests'] += stat['total_requests']
            model_stats[model]['total_cost'] += stat['total_cost'] or 0.0
            model_stats[model]['total_tokens'] += stat['total_tokens'] or 0
        
        # Sort by cost
        sorted_models = sorted(
            model_stats.values(), 
            key=lambda x: x['total_cost'], 
            reverse=True
        )
        
        return {
            "status": "success",
            "data": sorted_models,
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching model usage: {str(e)}"
        )