"""Repository for API usage tracking operations."""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class APIUsageRepository(BaseRepository):
    """Repository for API usage tracking operations."""

    async def create_usage_record(
        self,
        user_id: Optional[int],
        service_type: str,
        provider: str,
        model: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        prompt_cost: Optional[float] = None,
        completion_cost: Optional[float] = None,
        total_cost: float = 0.0,
        request_type: Optional[str] = None,
        input_length: Optional[int] = None,
        output_length: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new API usage record."""
        async with self._pool.acquire() as conn:
            metadata_json = json.dumps(metadata) if metadata else None
            
            record = await conn.fetchrow(
                """
                INSERT INTO api_usage 
                (user_id, service_type, provider, model, prompt_tokens, completion_tokens, 
                 total_tokens, prompt_cost, completion_cost, total_cost, request_type, 
                 input_length, output_length, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14::jsonb, $15)
                RETURNING *
                """,
                user_id, service_type, provider, model, prompt_tokens, completion_tokens,
                total_tokens, prompt_cost, completion_cost, total_cost, request_type,
                input_length, output_length, metadata_json, datetime.utcnow()
            )
            
            return dict(record)

    async def get_usage_stats(
        self,
        user_id: Optional[int] = None,
        service_type: Optional[str] = None,
        provider: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get aggregated usage statistics."""
        async with self._pool.acquire() as conn:
            where_conditions = []
            params = []
            param_count = 0
            
            if user_id:
                param_count += 1
                where_conditions.append(f"user_id = ${param_count}")
                params.append(user_id)
            
            if service_type:
                param_count += 1
                where_conditions.append(f"service_type = ${param_count}")
                params.append(service_type)
                
            if provider:
                param_count += 1
                where_conditions.append(f"provider = ${param_count}")
                params.append(provider)
                
            if start_date:
                param_count += 1
                where_conditions.append(f"created_at >= ${param_count}")
                params.append(start_date)
                
            if end_date:
                param_count += 1
                where_conditions.append(f"created_at <= ${param_count}")
                params.append(end_date)
            
            where_clause = ""
            if where_conditions:
                where_clause = f"WHERE {' AND '.join(where_conditions)}"
            
            query = f"""
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(total_cost) as total_cost,
                    SUM(total_tokens) as total_tokens,
                    SUM(prompt_tokens) as total_prompt_tokens,
                    SUM(completion_tokens) as total_completion_tokens,
                    AVG(total_cost) as avg_cost_per_request,
                    service_type,
                    provider,
                    model
                FROM api_usage 
                {where_clause}
                GROUP BY service_type, provider, model
                ORDER BY total_cost DESC
            """
            
            records = await conn.fetch(query, *params)
            return [dict(record) for record in records]

    async def get_cost_breakdown(
        self,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get cost breakdown by service and model for the last N days."""
        async with self._pool.acquire() as conn:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            where_conditions = ["created_at >= $1"]
            params = [start_date]
            
            if user_id:
                where_conditions.append("user_id = $2")
                params.append(user_id)
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}"
            
            # Get breakdown by service type
            service_breakdown = await conn.fetch(f"""
                SELECT 
                    service_type,
                    COUNT(*) as request_count,
                    SUM(total_cost) as total_cost,
                    SUM(total_tokens) as total_tokens
                FROM api_usage 
                {where_clause}
                GROUP BY service_type
                ORDER BY total_cost DESC
            """, *params)
            
            # Get breakdown by provider
            provider_breakdown = await conn.fetch(f"""
                SELECT 
                    provider,
                    COUNT(*) as request_count,
                    SUM(total_cost) as total_cost,
                    SUM(total_tokens) as total_tokens
                FROM api_usage 
                {where_clause}
                GROUP BY provider
                ORDER BY total_cost DESC
            """, *params)
            
            # Get breakdown by model
            model_breakdown = await conn.fetch(f"""
                SELECT 
                    model,
                    provider,
                    service_type,
                    COUNT(*) as request_count,
                    SUM(total_cost) as total_cost,
                    SUM(total_tokens) as total_tokens
                FROM api_usage 
                {where_clause}
                GROUP BY model, provider, service_type
                ORDER BY total_cost DESC
                LIMIT 20
            """, *params)
            
            # Get daily costs
            daily_costs = await conn.fetch(f"""
                SELECT 
                    DATE(created_at) as date,
                    SUM(total_cost) as daily_cost,
                    COUNT(*) as daily_requests
                FROM api_usage 
                {where_clause}
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 30
            """, *params)
            
            return {
                "service_breakdown": [dict(row) for row in service_breakdown],
                "provider_breakdown": [dict(row) for row in provider_breakdown],
                "model_breakdown": [dict(row) for row in model_breakdown],
                "daily_costs": [dict(row) for row in daily_costs],
            }

    async def get_total_costs(
        self,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, float]:
        """Get total costs for the last N days."""
        async with self._pool.acquire() as conn:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            where_conditions = ["created_at >= $1"]
            params = [start_date]
            
            if user_id:
                where_conditions.append("user_id = $2")
                params.append(user_id)
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}"
            
            result = await conn.fetchrow(f"""
                SELECT 
                    COALESCE(SUM(total_cost), 0) as total_cost,
                    COUNT(*) as total_requests,
                    COALESCE(SUM(total_tokens), 0) as total_tokens
                FROM api_usage 
                {where_clause}
            """, *params)
            
            return dict(result) if result else {"total_cost": 0.0, "total_requests": 0, "total_tokens": 0}

    async def get_recent_usage(
        self,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent API usage records."""
        async with self._pool.acquire() as conn:
            where_clause = ""
            params = []
            
            if user_id:
                where_clause = "WHERE user_id = $1"
                params.append(user_id)
            
            records = await conn.fetch(f"""
                SELECT * FROM api_usage 
                {where_clause}
                ORDER BY created_at DESC 
                LIMIT {limit}
            """, *params)
            
            return [dict(record) for record in records]

    async def delete_old_records(self, days: int = 90) -> int:
        """Delete old usage records older than specified days."""
        async with self._pool.acquire() as conn:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await conn.execute(
                "DELETE FROM api_usage WHERE created_at < $1",
                cutoff_date
            )
            
            # Extract count from result like "DELETE 5"
            parts = result.split()
            return int(parts[-1]) if len(parts) > 1 else 0