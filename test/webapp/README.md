# Testing Catchlist

This directory contains a webapp testing suite.

It was built with python, pytest, and selenium.

# Setting up webapp testing from scratch
- on the deploy server, add the necessary key and repo to install google chrome
- create a python virtualenv in this directory using the provided requirements file
- edit the environment files in test/webapp/environments
  - URLs for all three environments will need to change
  - ports will likely need to change for local/dev
  - ideally, bring these environment files into postman to edit them more easily

That should be it

# Running the tests 
Running the tests looks like this:

`pytest -m smoke --env=local_web_env.json`

The value provided to the env flag is assumed to match a filename in test/webapp/environments.

Tests are grouped with 'markers', and you can use the -m flag to specify which tests to run.

You can do fun things like use "and" and "not" when specifying markers. 
For more info see https://docs.pytest.org/en/stable/example/markers.html

Pytest will complain about markers which have not been registered;

register new markers in test/webapp/pytest.ini

Note the devtest marker; it's recommended that you create new tests under this marker to run them alone.

You can copy the good parts to other tests after whittling the chaos and exploration down to something that works.



