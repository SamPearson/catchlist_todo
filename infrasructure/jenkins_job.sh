###########################################
# Jenkins Deploy Template
#
# - copy this into the build steps "execute shell" field
# - edit the CONFIGURATION section to match your domain, systemd service names, etc
# - Look at the postman filenames, edit as needed.
# - delete this header, only copy from the binbash line down
###########################################


#!/bin/bash

# Fail the job on the first failure,
# throw errors for unset variables,
# fail if something was supposed to be piped to another command but failed
set -euo pipefail

# Use only newlines and tabs as string separators, not spaces (default)
IFS=$'\n\t'

# -----------------
# CONFIGURATION
# -----------------
BASE_DIR="/var/www/deployment.domain"
API_SERVICE="catchlist_api.service"
WEB_SERVICE="catchlist_web.service"
SERVICES=("$API_SERVICE" "$WEB_SERVICE")
GIT_BRANCH="production_build"

# -----------------
# UTILITY FUNCTIONS
# -----------------

log() {
    echo -e "\n🔹 $1"
}

manage_service() {
    local action=$1
    local service=$2

    log "${action^}ing $service..."
    if ! sudo systemctl "$action" "$service"; then
        echo "❌ Failed to $action $service!"
        exit 1
    fi
}


# -----------------
# DEPLOYMENT STEPS
# -----------------

# Avoid duplicate safe.directory entries
if ! git config --global --get-all safe.directory | grep -qx "$BASE_DIR"; then
    git config --global --add safe.directory "$BASE_DIR"
fi

cd "$BASE_DIR" || exit 1

# Stop services
for service in "${SERVICES[@]}"; do
    manage_service "stop" "$service"
done

log "Pulling latest code..."
if ! git pull origin "$GIT_BRANCH"; then
    echo "❌ Git pull failed!"
    exit 1
fi

log "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade -r requirements.txt
deactivate

# Start services
for service in "${SERVICES[@]}"; do
    manage_service "start" "$service"
done

# Check service statuses
for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "✅ $service is running."
    else
        echo "❌ $service failed to start!"
        exit 1
    fi
done

# Wait for API to be healthy
log "Waiting for API to be healthy..."
MAX_RETRIES=30
RETRY_INTERVAL=2
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f "https://deployment.domain/api/health" > /dev/null; then
        echo "✅ API is healthy!"
        break
    fi
    
    echo "Waiting for API to be healthy... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ API failed to become healthy after $MAX_RETRIES attempts"
    exit 1
fi

# -----------------
# TESTING
# -----------------

log "Activating virtual environment..."
source "$BASE_DIR/venv/bin/activate"

# ---- API Tests ----
TEST_API_DIR="$BASE_DIR/test/api"
cd "$TEST_API_DIR" || exit 1

log "🔹 Installing API test dependencies..."
pip install --upgrade -r requirements.txt

log "🔹 Cleaning up old test reports..."
REPORT_DIR="$WORKSPACE/allure-results"
rm -rf "$REPORT_DIR"

log "🔹 Running pytest API smoke tests..."
if ! pytest -m smoke_test --env="ENVIRONMENT NAME HERE" --alluredir="$REPORT_DIR" -v; then
    echo "❌ API smoke tests failed! Stopping deployment."
    deactivate
    exit 1
fi


log "✅ API smoke tests passed."

# ---- Webapp (Selenium) Tests ----
# temporarily disabled until webapp refactor
#TEST_WEBAPP_DIR="$BASE_DIR/test/webapp"
#cd "$TEST_WEBAPP_DIR" || exit 1
#
#log "🔹 Installing webapp test dependencies..."
#pip install --upgrade -r requirements.txt
#
#log "🔹 Running Selenium Webapp tests..."
#if ! pytest --headless="True" --env="production_web_env.json"; then
#    echo "❌ Selenium tests failed! Stopping deployment."
#    deactivate
#    exit 1
#fi
#log "✅ Selenium Webapp tests passed."

deactivate
log "✅ All tests passed. Deployment complete."