# Infrastructure Templates

This directory contains deployment configuration templates for setting up the CatchList Todo application with nginx, systemd, and Jenkins.

---

## Template Files

### `sites-available.txt`
Nginx reverse proxy configuration template for routing traffic to the API and webapp.

**Key features:**
- HTTP to HTTPS redirect
- SSL/TLS configuration (assumes Let's Encrypt certificates)
- Reverse proxy setup for webapp (port 8000) and API (port 5000)
- Static file serving
- Bot filtering

**Quick setup:**
Replace the example domain with your own using vim or whatever regex tool you like:
```

:%s/webappsubdomain.example.com/yourdomainhere/g
```
---

### `systemd_api.txt` & `systemd_webapp.txt`
Systemd service unit files for running the API and webapp as background services.

**Important notes:**
- Port numbers are hardcoded (API: 5000, WebApp: 8000)
- Ports must match your nginx configuration
- Both services use Gunicorn with 3 workers
- Services auto-restart on failure

---

### `infrastructure/config/.env.api`
Environment configuration file for the API service.

**Purpose:**
- Sets the `JWT_SECRET_KEY` environment variable
- Referenced by the systemd API service file

**Alternative:**
You can remove this file and set environment variables directly in your deployment script if preferred.

---

### `jenkins_job.sh`
Jenkins deployment job template with automated testing.

**Prerequisites:**
- Allure plugin for Jenkins

**Features:**
- Automated git pull and dependency installation
- Systemd service management (stop → deploy → start)
- Health check verification
- API smoke tests on every deployment
- Configurable test markers for flexible test execution

**WebApp testing:**
Selenium tests are currently commented out and will be re-enabled after the webapp refactor is complete.

---

## Quick Start

1. Copy the nginx template to `/etc/nginx/sites-available/`
2. Update domain names and paths in all templates
3. Copy systemd service files to `/etc/systemd/system/`
4. Create and configure the `.env` file with your JWT secret
5. Set up your Jenkins job using the provided script template

---

## Configuration Checklist

- [ ] Update domain names in nginx config
- [ ] Verify port numbers match across nginx and systemd configs
- [ ] Set JWT_SECRET_KEY in environment file
- [ ] Configure Jenkins job paths and service names
- [ ] Obtain SSL certificates (e.g., via certbot)
- [ ] Enable and start systemd services
