# CrudBase
At its core, this is a personal development task manager. 

However, whereas most CRUD todo apps stop at a kind of MVP product
(a single page with no frontend/backend split, no accounts, no deploy infrastructure),
this one is meant to be closer to a production-ready application; 
a realistic starting point for building something useful.

Please see the [system requirements document](/docs/system_requirements.md) for detailed information about the application's purpose and features.

EG this project has
- webapp (frontend) and API (backend) split into different source directories
- user registration, todos only visible to the user who created them
- systemd services to run the apps on production, runscripts for local testing
- baseline sites-available file to use with nginx
- baseline jenkins file to build staging/production deploy jobs
- api (backend) and selenium (frontend) test suites

It is not meant to be a feature-rich application, 
but rather a starting point from which to develop one. 

The dream is that this project can be forked, 
you can change the urls in the infra config files,
implement the site on your vps, and then begin making changes such as 
new db models, html templates, api/webapp endpoints, etc.  

# Installing From Scratch

## Installing the webapp and API from scratch
- Register a VPS running ubuntu server (other linux distros may require slight config adjustments)
- Register a domain name and point an A record to the VPS
  - may as well point a jenkins subodmain as well, and perhaps a staging subdomain
- Install nginx, open necessary ports with `sudo ufw allow 'Nginx Full`
  - Open port 8080 as well; jenkins will initially run on this port
- make a directory for /var/www/yourdomain
  - at this point you may want to make a group to own that directory (and put yourself in that group)
  - make sure the group has write permissions on the directory
  - and set the guid bit for that directory so that all files under are owned by the group
- create a basic /etc/nginx/sites-available file for the domain
  - do not copy the sites-available example from the infrastructure directory yet
- symlink from sites-available to sites-enabled
- put a basic index.html file in the /var/www/yourdomain directory
- reload nginx and visit the domain, test your configuration
- copy the sites-available file from the infrastructure directory
  - paste over the existing sites-available file; edit where necessary (eg the domain)
  - visiting the site will not work until gunicorn and the flask app are set up
- run `git clone yourrepo .` in your domain's /var/www directory
- install python3-venv and gunicorn
- create a virtual environment in the project root dir and install the reqs from requirements.txt
- use the examples in /infrastructure to create systemd service files for the api and webapp
- edit the environment files in /src/config/environments (correct the API url)
- run the api and webapp services manually; confirm the webapp now loads by visiting the domain 

## Setting api/webapp testing up from scratch
- For API Testing setup, see the README in the test/api directory 
- For Webapp testing setup, see the README in the test/webapp directory

## Setting up jenkins
- Install java and jenkins
- (you may configure jenkins to run on a subdomain here if you want)
- use visudo to add a new sudoers file for jenkins 
  - Allow the jenkins user to use passwordless sudo for start/stop/restart of the service files
- add the jenkins user to the group that owns the /var/www/yourdomain directory
- Configure jenkins to run as an agent instead of using the built-in node
  - if you do not do this, jenkins will not have group perms and your builds will fail.
- create a new jenkins freestyle job; use the example infrastructure/jenkins_job.sh file as a guide

---- 

After successfully completing these steps, 

any time you push to the branch jenkins is watching, you may kick off a job that will:
- stop the API and webapp services
- pull the latest commit
- start the API and webapp services
- run api and webapp testing

This will allow you to build out new features without unknowingly breaking the old ones,
provided that you build tests for each feature as you go.

# Running the app

## In a word
### Running locally
To run the API locally:
`./run_api.sh`
To run the webapp locally:
`./run_webapp.sh`

The webapp will be available at 
http://127.0.0.1:5000/

### Running on a server
This should be managed via systemd services per the setup instructions.


## How it runs
The systemd services run the api and web server using gunicorn. 
Both services are reverse proxied via a web server (assumed to be nginx)

Some examples of running the app without systemd services:

To run the webapp:

`gunicorn --config gunicorn_config_webapp.py --workers 3 --bind 127.0.0.1:8000 webapp:app`

To run the API:

`gunicorn --config gunicorn_config_api.py --workers 3 --bind 127.0.0.1:5001 api:app`


