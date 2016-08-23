This tool is intended to read a swagger 2.0 spec compliant yaml file and dynamically generate tests.
The tests will use any test data listed in the spec file and compare defined responses to actual responses.


This tool currently only supports get requests and 200 responses.


For the future:
- support all http method requests
- test for error cases
- test for permissions
- allow verbosity levels to be set
  - print definitions as they are tested
  - print response with definition as its tested
  - print url and request parameters



How to run this tool:

python manage.py test --api <swagger_file.yaml>