# Testing the Internet

Test case demonstrations for common webpage features

test target: https://the-internet.herokuapp.com/

## Running tests

Tests can be run by executing the pytest command in the project root directory. 

## Command Line Options

Command line options (defined in conftest.py) can be used to specify a test environment
    (e.g. run tests remotely or locally, in which browser, on what operating system, etc.)

The command line option "host" determines whether tests will be run locally or on saucelabs.
    host is set to saucelabs by default. To test locally, you can run specify that like so:
    `$pytest --host=localhost`

To run tests on saucelabs, you need to set the environment variables SAUCE_USERNAME and SAUCE_ACCESS_KEY
To configure these environment variables in jenkins, see: https://docs.saucelabs.com/ci/jenkins/

## Markers
Pytest markers (defined in pytest.ini) are used to categorize tests by feature and by test depth.
Use these markers to select a suite of tests to run

`$pytest -m "dynamicLoading" --host=localhost`

"and/or/not" may be used to create more specific groupings of tests

`$pytest -m "login and smoke" --host=localhost`