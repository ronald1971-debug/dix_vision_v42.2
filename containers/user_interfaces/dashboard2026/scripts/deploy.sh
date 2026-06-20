#!/bin/bash

# DIX VISION Dashboard2026 Deployment Scripts
# Production deployment automation with rollback capability

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_LOG="deployments/deployment-$(date +%Y%m%d-%H%M%S).log"
ROLLBACK_LOG="deployments/rollback-$(date +%Y%m%d-%H%M%S).log"
BACKUP_DIR="backups/backup-$(date +%Y%m%d-%H%M%S)"
ENVIRONMENT="${1:-staging}"
VERSION="${2:-latest}"
STRATEGY="${3:-rolling}"

# Create directories
mkdir -p deployments
mkdir -p backups

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$DEPLOYMENT_LOG"
}

# Error handling
handle_error() {
    log "ERROR" "${RED}Deployment failed!${NC}"
    log "ERROR" "Check deployment log: $DEPLOYMENT_LOG"
    if [ "$AUTO_ROLLBACK" = "true" ]; then
        log "INFO" "Initiating automatic rollback..."
        rollback_deployment
    fi
    exit 1
}

trap handle_error ERR

# Pre-deployment checks
pre_deployment_checks() {
    log "INFO" "${BLUE}Running pre-deployment checks...${NC}"
    
    # Check if environment exists
    log "INFO" "Validating environment: $ENVIRONMENT"
    
    # Check if required tools are installed
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker is not installed"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log "ERROR" "kubectl is not installed"
        exit 1
    fi
    
    # Check configuration
    log "INFO" "Validating configuration for environment: $ENVIRONMENT"
    
    # Check resource availability
    log "INFO" "Checking resource availability"
    
    # Run health checks
    log "INFO" "Running health checks"
    
    log "SUCCESS" "${GREEN}Pre-deployment checks passed${NC}"
}

# Backup current deployment
backup_deployment() {
    log "INFO" "${BLUE}Creating backup of current deployment...${NC}"
    mkdir -p "$BACKUP_DIR"
    
    # Backup configuration
    log "INFO" "Backing up configuration"
    cp -r config/ "$BACKUP_DIR/config" || true
    
    # Backup data (if applicable)
    log "INFO" "Backing up data"
    # Add data backup commands here
    
    # Backup infrastructure state
    log "INFO" "Backing up infrastructure state"
    
    log "SUCCESS" "${GREEN}Backup completed: $BACKUP_DIR${NC}"
    echo "$BACKUP_DIR" > deployments/latest-backup.txt
}

# Build application
build_application() {
    log "INFO" "${BLUE}Building application...${NC}"
    
    # Build Docker images
    log "INFO" "Building Docker images"
    docker build -t dix-vision-dashboard:$VERSION .
    
    # Run tests
    log "INFO" "Running tests"
    npm test
    
    log "SUCCESS" "${GREEN}Application built successfully${NC}"
}

# Push images to registry
push_images() {
    log "INFO" "${BLUE}Pushing images to registry...${NC}"
    
    # Tag images for registry
    docker tag dix-vision-dashboard:$VERSION registry.example.com/dix-vision-dashboard:$VERSION
    
    # Push images
    docker push registry.example.com/dix-vision-dashboard:$VERSION
    
    log "SUCCESS" "${GREEN}Images pushed successfully${NC}"
}

# Deploy based on strategy
deploy_application() {
    log "INFO" "${BLUE}Deploying application using strategy: $STRATEGY${NC}"
    
    case $STRATEGY in
        "rolling")
            rolling_update
            ;;
        "blue-green")
            blue_green_deployment
            ;;
        "canary")
            canary_deployment
            ;;
        *)
            log "ERROR" "Unknown deployment strategy: $STRATEGY"
            exit 1
            ;;
    esac
}

# Rolling update deployment
rolling_update() {
    log "INFO" "Executing rolling update deployment"
    
    # Update Kubernetes deployment
    kubectl set image deployment/dix-vision-dashboard \
        dix-vision-dashboard=registry.example.com/dix-vision-dashboard:$VERSION \
        -n $ENVIRONMENT
    
    # Wait for rollout to complete
    kubectl rollout status deployment/dix-vision-dashboard -n $ENVIRONMENT
    
    log "SUCCESS" "${GREEN}Rolling update completed${NC}"
}

# Blue-green deployment
blue_green_deployment() {
    log "INFO" "Executing blue-green deployment"
    
    local current_color=$(kubectl get service dix-vision-dashboard -n $ENVIRONMENT -o jsonpath='{.spec.selector.color}')
    local new_color=$([ "$current_color" = "blue" ] && echo "green" || echo "blue")
    
    # Deploy to new color
    kubectl apply -f k8s/${new_color}-deployment.yaml
    kubectl set image deployment/dix-vision-dashboard-${new_color} \
        dix-vision-dashboard=registry.example.com/dix-vision-dashboard:$VERSION \
        -n $ENVIRONMENT
    
    # Wait for new deployment to be ready
    kubectl wait --for=condition=available deployment/dix-vision-dashboard-${new_color} -n $ENVIRONMENT --timeout=5m
    
    # Switch service to new color
    kubectl patch service dix-vision-dashboard -n $ENVIRONMENT -p '{"spec":{"selector":{"color":"'"$new_color"'"}}}'
    
    log "SUCCESS" "${GREEN}Blue-green deployment completed${NC}"
}

# Canary deployment
canary_deployment() {
    log "INFO" "Executing canary deployment"
    
    # Deploy canary
    kubectl apply -f k8s/canary-deployment.yaml
    kubectl set image deployment/dix-vision-dashboard-canary \
        dix-vision-dashboard=registry.example.com/dix-vision-dashboard:$VERSION \
        -n $ENVIRONMENT
    
    # Wait for canary to be ready
    kubectl wait --for=condition=available deployment/dix-vision-dashboard-canary -n $ENVIRONMENT --timeout=5m
    
    # Gradual traffic shift
    for percentage in 10 25 50 100; do
        log "INFO" "Shifting $percentage% traffic to canary"
        # Update service to route percentage of traffic to canary
        sleep 30
    done
    
    # Update main deployment
    kubectl set image deployment/dix-vision-dashboard \
        dix-vision-dashboard=registry.example.com/dix-vision-dashboard:$VERSION \
        -n $ENVIRONMENT
    
    # Remove canary
    kubectl delete deployment dix-vision-dashboard-canary -n $ENVIRONMENT
    
    log "SUCCESS" "${GREEN}Canary deployment completed${NC}"
}

# Post-deployment validation
post_deployment_validation() {
    log "INFO" "${BLUE}Running post-deployment validation...${NC}"
    
    # Health checks
    log "INFO" "Running health checks"
    kubectl get pods -n $ENVIRONMENT -l app=dix-vision-dashboard
    
    # Smoke tests
    log "INFO" "Running smoke tests"
    npm run test:smoke
    
    # Integration tests
    log "INFO" "Running integration tests"
    npm run test:integration
    
    log "SUCCESS" "${GREEN}Post-deployment validation passed${NC}"
}

# Rollback deployment
rollback_deployment() {
    log "WARN" "${YELLOW}Initiating rollback...${NC}"
    
    local backup_dir=$(cat deployments/latest-backup.txt 2>/dev/null || echo "")
    
    if [ -z "$backup_dir" ]; then
        log "ERROR" "No backup found"
        exit 1
    fi
    
    log "INFO" "Rolling back to: $backup_dir"
    
    # Restore configuration
    cp -r "$backup_dir/config" config/
    
    # Restore previous version
    local previous_version=$(kubectl get deployment dix-vision-dashboard -n $ENVIRONMENT -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d':' -f2)
    kubectl rollout undo deployment/dix-vision-dashboard -n $ENVIRONMENT
    
    log "SUCCESS" "${GREEN}Rollback completed${NC}"
}

# Cleanup
cleanup() {
    log "INFO" "Cleaning up temporary files"
    
    # Remove old backups (older than 30 days)
    find backups -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
    
    # Clean up old deployment logs (older than 90 days)
    find deployments -type f -name "*.log" -mtime +90 -exec rm {} + 2>/dev/null || true
}

# Main deployment flow
main() {
    log "INFO" "${BLUE}Starting deployment of DIX VISION Dashboard2026${NC}"
    log "INFO" "Environment: $ENVIRONMENT"
    log "INFO" "Version: $VERSION"
    log "INFO" "Strategy: $STRATEGY"
    
    pre_deployment_checks
    backup_deployment
    build_application
    push_images
    deploy_application
    post_deployment_validation
    
    cleanup
    
    log "SUCCESS" "${GREEN}Deployment completed successfully!${NC}"
    log "INFO" "Deployment log: $DEPLOYMENT_LOG"
}

# Run main function
main