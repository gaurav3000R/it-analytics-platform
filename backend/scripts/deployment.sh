# Adding the missing ./backend/scripts/deployment.sh (already provided, but ensuring completeness)

#===== ./backend/scripts/deployment.sh =====

#!/bin/bash

# IT Analytics Platform Deployment Script
set -e

echo "🚀 Deploying IT Analytics Platform..."

# Configuration
APP_NAME="it-analytics-backend"
PORT=8000
ENVIRONMENT=${1:-development}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        log_error "pip is not installed"
        exit 1
    fi
    
    log_info "Prerequisites check passed ✅"
}

# Setup virtual environment
setup_venv() {
    log_info "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_info "Virtual environment created"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_info "Virtual environment setup completed ✅"
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    source venv/bin/activate
    python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
    
    log_info "Database setup completed ✅"
}

# Generate sample data for demo
setup_sample_data() {
    if [ "$ENVIRONMENT" == "development" ]; then
        log_info "Generating sample data for development environment..."
        source venv/bin/activate
        python app/main.py --setup-data
        log_info "Sample data generated ✅"
    fi
}

# Train ML models
train_models() {
    log_info "Training ML models..."
    
    source venv/bin/activate
    mkdir -p models
    python app/main.py --train-models
    
    log_info "ML models trained ✅"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Start server in background
    source venv/bin/activate
    python app/main.py --run-server --port $PORT &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 10
    
    # Check health endpoint
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        log_info "Health check passed ✅"
    else
        log_error "Health check failed ❌"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    # Stop server
    kill $SERVER_PID 2>/dev/null || true
}

# Deploy
deploy() {
    log_info "Starting deployment for $ENVIRONMENT environment..."
    
    check_prerequisites
    setup_venv
    setup_database
    setup_sample_data
    train_models
    health_check
    
    log_info "🎉 Deployment completed successfully!"
    log_info "Server will be available at: http://localhost:$PORT"
    log_info "API Documentation: http://localhost:$PORT/docs"
    
    if [ "$ENVIRONMENT" == "production" ]; then
        log_warn "Production deployment detected"
        log_warn "Please configure proper environment variables"
        log_warn "Consider using a process manager like systemd or supervisor"
    fi
}

# Start server
start_server() {
    log_info "Starting IT Analytics Platform server..."
    source venv/bin/activate
    python app/main.py --run-server --port $PORT
}

# Main execution
case "${2:-deploy}" in
    "deploy")
        deploy
        ;;
    "start")
        start_server
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 [environment] [action]"
        echo "Environment: development|production"
        echo "Action: deploy|start|health"
        exit 1
        ;;
esac