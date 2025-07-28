#!/usr/bin/env python3
"""
AstraTrade Prometheus Metrics Exporter
Exposes contract health metrics for Prometheus scraping
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

from contract_health_check import ContractHealthChecker, ContractHealthConfig

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
CONTRACT_STATUS = Gauge(
    'astratrade_contract_status',
    'Contract health status (1=healthy, 0=unhealthy)',
    ['contract_name', 'address', 'network']
)

CONTRACT_RESPONSE_TIME = Histogram(
    'astratrade_contract_response_time_ms',
    'Contract response time in milliseconds',
    ['contract_name', 'address', 'network'],
    buckets=[10, 50, 100, 500, 1000, 2000, 5000, 10000]
)

RPC_ENDPOINT_STATUS = Gauge(
    'astratrade_rpc_endpoint_status',
    'RPC endpoint status (1=healthy, 0=unhealthy)',
    ['endpoint']
)

RPC_RESPONSE_TIME = Histogram(
    'astratrade_rpc_response_time_ms', 
    'RPC endpoint response time in milliseconds',
    ['endpoint'],
    buckets=[10, 50, 100, 500, 1000, 2000, 5000]
)

NETWORK_BLOCK_HEIGHT = Gauge(
    'astratrade_network_block_height',
    'Latest network block height',
    ['network']
)

HEALTH_CHECK_FAILURES = Counter(
    'astratrade_health_check_failures_total',
    'Total number of health check failures',
    ['component', 'error_type']
)

HEALTH_CHECK_DURATION = Histogram(
    'astratrade_health_check_duration_seconds',
    'Time taken to complete health checks',
    buckets=[1, 5, 10, 30, 60, 120]
)

HEALTHY_CONTRACTS_COUNT = Gauge(
    'astratrade_healthy_contracts_count',
    'Number of healthy contracts'
)

OVERALL_HEALTH_STATUS = Gauge(
    'astratrade_overall_health_status',
    'Overall system health status (2=healthy, 1=degraded, 0=unhealthy)'
)

ACTIVE_ALERTS_COUNT = Gauge(
    'astratrade_active_alerts_count',
    'Number of active alerts'
)

class HealthMetricsExporter:
    """Prometheus metrics exporter for contract health"""
    
    def __init__(self):
        self.app = FastAPI(title="AstraTrade Health Metrics Exporter")
        self.config = ContractHealthConfig(
            rpc_endpoints=[
                "https://free-rpc.nethermind.io/sepolia-juno",
                "https://sepolia-rpc.starknet.io"
            ],
            explorer_api="https://sepolia.starkscan.co/api",
            timeout_seconds=30
        )
        self.contracts = self.load_contracts()
        self.setup_routes()
        
    def load_contracts(self) -> Dict[str, str]:
        """Load deployed contracts from configuration"""
        try:
            deployment_file = "deployment_logs/deployment_sepolia_20250720_151230.json"
            with open(deployment_file, 'r') as f:
                deployment_data = json.load(f)
                contracts = {
                    name: info['address'] 
                    for name, info in deployment_data.get('contracts', {}).items()
                }
            logger.info(f"Loaded {len(contracts)} contracts for monitoring")
            return contracts
        except Exception as e:
            logger.error(f"Failed to load contracts: {e}")
            return {}
            
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
            
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint"""
            try:
                # Run health check and update metrics
                await self.update_metrics()
                
                # Return Prometheus formatted metrics
                return Response(
                    content=generate_latest(),
                    media_type=CONTENT_TYPE_LATEST
                )
            except Exception as e:
                logger.error(f"Failed to generate metrics: {e}")
                HEALTH_CHECK_FAILURES.labels(
                    component="metrics_exporter",
                    error_type="generation_error"
                ).inc()
                return Response(
                    content="# Failed to generate metrics\n",
                    media_type=CONTENT_TYPE_LATEST,
                    status_code=500
                )
                
        @self.app.get("/status")
        async def status():
            """Current status overview"""
            return {
                "contracts_monitored": len(self.contracts),
                "rpc_endpoints": len(self.config.rpc_endpoints),
                "last_check": datetime.now().isoformat()
            }
            
    async def update_metrics(self):
        """Update all Prometheus metrics"""
        start_time = time.time()
        
        try:
            async with ContractHealthChecker(self.config) as checker:
                # Run comprehensive health check
                report = await checker.run_comprehensive_health_check(self.contracts)
                
                # Update contract metrics
                self.update_contract_metrics(report)
                
                # Update RPC metrics  
                self.update_rpc_metrics(report)
                
                # Update network metrics
                self.update_network_metrics(report)
                
                # Update summary metrics
                self.update_summary_metrics(report)
                
                logger.debug("Metrics updated successfully")
                
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            HEALTH_CHECK_FAILURES.labels(
                component="health_checker",
                error_type="update_error"
            ).inc()
        finally:
            # Record health check duration
            duration = time.time() - start_time
            HEALTH_CHECK_DURATION.observe(duration)
            
    def update_contract_metrics(self, report: Dict[str, Any]):
        """Update contract-specific metrics"""
        healthy_count = 0
        
        for contract_name, health_info in report.get('contract_health', {}).items():
            address = health_info.get('address', '')
            status = health_info.get('status', 'unknown')
            response_time = health_info.get('response_time_ms', 0)
            
            # Convert status to numeric
            status_value = 1 if status == 'healthy' else 0
            if status_value == 1:
                healthy_count += 1
                
            # Update metrics
            CONTRACT_STATUS.labels(
                contract_name=contract_name,
                address=address,
                network='sepolia'
            ).set(status_value)
            
            if response_time > 0:
                CONTRACT_RESPONSE_TIME.labels(
                    contract_name=contract_name,
                    address=address,
                    network='sepolia'
                ).observe(response_time)
                
            # Track failures
            if status != 'healthy':
                HEALTH_CHECK_FAILURES.labels(
                    component=f"contract_{contract_name}",
                    error_type=status
                ).inc()
                
        HEALTHY_CONTRACTS_COUNT.set(healthy_count)
        
    def update_rpc_metrics(self, report: Dict[str, Any]):
        """Update RPC endpoint metrics"""
        for endpoint, rpc_info in report.get('rpc_connectivity', {}).items():
            status = rpc_info.get('status', 'unknown')
            response_time = rpc_info.get('response_time_ms', 0)
            
            # Update status
            status_value = 1 if status == 'healthy' else 0
            RPC_ENDPOINT_STATUS.labels(endpoint=endpoint).set(status_value)
            
            # Update response time
            if response_time and response_time > 0:
                RPC_RESPONSE_TIME.labels(endpoint=endpoint).observe(response_time)
                
    def update_network_metrics(self, report: Dict[str, Any]):
        """Update network-level metrics"""
        network_info = report.get('network_status', {})
        latest_block = network_info.get('latest_block')
        
        if latest_block:
            NETWORK_BLOCK_HEIGHT.labels(network='sepolia').set(latest_block)
            
    def update_summary_metrics(self, report: Dict[str, Any]):
        """Update overall summary metrics"""
        overall_status = report.get('overall_status', 'unknown')
        
        # Convert to numeric
        status_mapping = {
            'healthy': 2,
            'degraded': 1,
            'unhealthy': 0
        }
        status_value = status_mapping.get(overall_status, 0)
        OVERALL_HEALTH_STATUS.set(status_value)
        
        # Count active alerts (simplified)
        issues_count = len(report.get('summary', {}).get('issues_detected', []))
        ACTIVE_ALERTS_COUNT.set(issues_count)
        
    async def start_background_monitoring(self):
        """Start background monitoring loop"""
        check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
        
        logger.info(f"Starting background monitoring (interval: {check_interval}s)")
        
        while True:
            try:
                await self.update_metrics()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                await asyncio.sleep(check_interval)


async def main():
    """Main application entry point"""
    exporter = HealthMetricsExporter()
    
    # Start background monitoring
    asyncio.create_task(exporter.start_background_monitoring())
    
    # Start web server
    config = uvicorn.Config(
        app=exporter.app,
        host="0.0.0.0",
        port=8080,
        log_level=os.getenv('LOG_LEVEL', 'INFO').lower(),
        access_log=True
    )
    
    server = uvicorn.Server(config)
    logger.info("Starting AstraTrade health metrics exporter on port 8080")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())