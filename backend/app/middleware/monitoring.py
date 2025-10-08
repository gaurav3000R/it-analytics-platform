import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import psutil
import os

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
RISK_PREDICTIONS = Counter('risk_predictions_total', 'Total risk predictions', ['project_id'])
ANOMALIES_DETECTED = Counter('anomalies_detected_total', 'Total anomalies detected', ['type', 'severity'])
MODEL_ERRORS = Counter('model_prediction_errors_total', 'Model prediction errors', ['model_type'])

logger = logging.getLogger(__name__)

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get endpoint
        endpoint = request.url.path
        method = request.method
        
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
            
            return response
            
        except Exception as e:
            # Record error
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
            logger.error(f"Request failed: {e}")
            raise

def record_risk_prediction(project_id: int):
    """Record a risk prediction metric"""
    RISK_PREDICTIONS.labels(project_id=str(project_id)).inc()

def record_anomaly_detection(anomaly_type: str, severity: str):
    """Record an anomaly detection metric"""
    ANOMALIES_DETECTED.labels(type=anomaly_type, severity=severity).inc()

def record_model_error(model_type: str):
    """Record a model prediction error"""
    MODEL_ERRORS.labels(model_type=model_type).inc()

async def metrics_endpoint(request: Request):
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

def get_system_metrics():
    """Get system performance metrics"""
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'process_count': len(psutil.pids()),
        'load_average': os.getloadavg()
    }