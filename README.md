# Catchlist_manager
Simple webapp to catch thoughts for short-term storage with minimal categorization

# Running the app

The app can be run on a web server using gunicorn (assuming nginx is
configured to serve from the directory this app is in), or it can be run 
locally without a web server. When running locally, the URL and port that 
the service can be accessed at will be output in the console.

There are different commands to run the app locally vs on a server, shown
in the sections below.

## Locally/Dev

The following commands will start the server locally

`$ python webapp.py`
or
`$ python api.py`

The webapp should run on port 5000 and the api on port 5001 (to avoid 
conflicts).

Different ports can be specified in the api.py and webapp.py files, 
but these should generally be open. 

## Server (staging/prod)
On staging and production, the webapp and api should be launched through 
gunicorn.

Note that we're binding the services to specific ports on the localhost ip.
This is done under the assumption that you'll be using nginx or something 
similar to actually serve them, so you'll have to point out these ports in
your sites-available file or change the ports in these commands to match
whatever you're serving at the target URL.

To run the webapp:

`gunicorn --config gunicorn_config_webapp.py --workers 3 --bind 127.0.0.1:8000 webapp:app`

To run the API:

`gunicorn --config gunicorn_config_api.py --workers 3 --bind 127.0.0.1:5001 api:app`

## Implementation
### Authentication
This application uses JWT (JSON Web Token) for authentication. Before deploying to production:

1. Set a secure JWT secret key:
   - Create a strong, random key (at least 32 characters)
   - Set it in your environment: `export JWT_SECRET_KEY='your-secure-key'`
   - Never use the default development key in production
   - Never commit your production key to version control

Example of generating a secure key:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

### Security Considerations
- The application requires authentication for all todo operations
- Each user can only access their own todos
- API endpoints are protected with JWT authentication
- Passwords are hashed using Werkzeug's security functions

