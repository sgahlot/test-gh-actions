#!/usr/bin/env python3
"""
Core Thanos Query Service
Moved from metrics_api.py to separate business logic
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import configuration
from .config import PROMETHEUS_URL, THANOS_TOKEN, VERIFY_SSL as verify

def query_thanos_with_promql(promql_queries: List[str], start_ts: int, end_ts: int) -> Dict[str, Any]:
    """
    Query Thanos with multiple PromQL queries and return structured data
    """
    print(f"🔍 Querying Thanos with {len(promql_queries)} queries")
    print(f"⏰ Time range: {datetime.fromtimestamp(start_ts)} to {datetime.fromtimestamp(end_ts)}")
    
    headers = {"Authorization": f"Bearer {THANOS_TOKEN}"} if THANOS_TOKEN else {}
    
    results = {}
    
    for i, promql in enumerate(promql_queries):
        if not promql or promql.strip() == "":
            continue
            
        print(f"📊 Query {i+1}: {promql}")
        
        try:
            # Query Thanos
            response = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query_range",
                headers=headers,
                params={
                    "query": promql,
                    "start": start_ts,
                    "end": end_ts,
                    "step": "60s"  # 1-minute intervals
                },
                verify=verify,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "success":
                result_data = data.get("data", {})
                results[get_metric_key(promql)] = {
                    "promql": promql,
                    "data": result_data,
                    "status": "success"
                }
                print(f"✅ Query {i+1} successful")
            else:
                print(f"❌ Query {i+1} failed: {data.get('error', 'Unknown error')}")
                results[get_metric_key(promql)] = {
                    "promql": promql,
                    "data": {},
                    "status": "error",
                    "error": data.get("error", "Unknown error")
                }
                
        except requests.exceptions.Timeout:
            print(f"⏰ Query {i+1} timed out")
            results[get_metric_key(promql)] = {
                "promql": promql,
                "data": {},
                "status": "timeout"
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Query {i+1} failed: {e}")
            results[get_metric_key(promql)] = {
                "promql": promql,
                "data": {},
                "status": "error",
                "error": str(e)
            }
        except Exception as e:
            print(f"❌ Query {i+1} failed: {e}")
            results[get_metric_key(promql)] = {
                "promql": promql,
                "data": {},
                "status": "error",
                "error": str(e)
            }
    
    print(f"📋 Completed {len(results)} queries")
    return results


def get_metric_key(promql: str) -> str:
    """
    Generate a unique key for a PromQL query
    """
    # Remove common prefixes and suffixes for cleaner keys
    key = promql.strip()
    
    # Remove common prefixes
    prefixes_to_remove = [
        "sum(", "avg(", "count(", "rate(", "histogram_quantile(0.95, ",
        "sum(rate(", "avg(rate(", "count(rate("
    ]
    
    for prefix in prefixes_to_remove:
        if key.startswith(prefix):
            key = key[len(prefix):]
            break
    
    # Remove common suffixes
    suffixes_to_remove = [
        ")", "))", ")))"
    ]
    
    for suffix in suffixes_to_remove:
        if key.endswith(suffix):
            key = key[:-len(suffix)]
            break
    
    # Clean up the key
    key = key.replace(" ", "_").replace("{", "_").replace("}", "_").replace('"', "")
    key = key.replace("namespace=", "ns_").replace("model_name=", "model_")
    key = key.replace("phase=", "phase_")
    
    # Remove multiple underscores
    while "__" in key:
        key = key.replace("__", "_")
    
    # Remove leading/trailing underscores
    key = key.strip("_")
    
    return key or "unknown_metric"


def find_primary_promql_for_question(question: str, promql_queries: List[str]) -> str:
    """
    Find the most relevant PromQL query for the given question
    """
    if not promql_queries:
        return ""
    
    question_lower = question.lower()
    
    # Priority order based on question keywords
    priority_patterns = [
        # GPU-related
        (["gpu", "temperature", "utilization"], ["DCGM_FI_DEV_GPU", "gpu"]),
        # vLLM-related
        (["vllm", "llm", "model", "inference"], ["vllm:"]),
        # Kubernetes-related
        (["pod", "pods", "deployment", "service"], ["kube_"]),
        # Alert-related
        (["alert", "alerts", "firing"], ["ALERTS"]),
        # Network-related
        (["network", "bandwidth", "traffic"], ["network", "net_"]),
        # Memory-related
        (["memory", "mem", "ram"], ["memory", "mem"]),
        # CPU-related
        (["cpu", "processor"], ["cpu"]),
    ]
    
    # Find the highest priority match
    for question_keywords, promql_keywords in priority_patterns:
        if any(keyword in question_lower for keyword in question_keywords):
            for promql in promql_queries:
                if any(keyword in promql for keyword in promql_keywords):
                    return promql
    
    # If no specific match, return the first non-empty query
    for promql in promql_queries:
        if promql and promql.strip():
            return promql
    
    return "" 