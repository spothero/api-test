This tool is intended to read a swagger 2.0 spec compliant yaml file and dynamically generate tests.
The tests will use any test data listed in the spec file and compare defined responses to actual responses.

This tool currently only supports get requests and 200 responses.

How to run this tool:
python manage.py test --api <swagger_file.yaml>

Test Tool Roadmap:
- test that all endpoints are documented
- support all http method requests
- test for error responses (400, 422, 428...) 
  - test that not passing listed required params results in field errors for each method
- test for permissions
  - set of test users to try for all endpoints
- documentation
  - document x-test inputs and format
  - document test_data_loader functonality
- allow verbosity levels to be set
  - print definitions as they are tested
  - print response with definition as its tested
  - print url and request parameters
- allow subsets of tests to be selected
  - select by tag
  - select by endpoint
  - select by endpoint, type, and response (e.g. /reservations/.get.200)
- support assert criteria
  - min/max, pattern checking
  - result list length
- tag tests
  - name each test data entry (test data is a list)
  - report the test data tag on test failure
- improve error handling
  - errors generating tests should be handled so that the user knows why the test failed 
  - errors should not stop test processing
- adapt tool to hit real endpoints
  - configure base url to test
  - investigate test data insertion into target environment
  - use all response checking from unit tests

