# Newman API Testing

This directory contains collection and environment files for testing the API.


## Setting up API testing
The environment files contain API urls

You'll need to edit those before these tests will work

- install nodejs and NPM
- use npm to install newman
- edit the environments in the test/api directory as necessary
- run the newman tests in the test/api directory


## Running Tests

See the test_local.sh script. 

If the environments are set up correctly,
then it's as easy as pointing newman to the collection file and an environment.
