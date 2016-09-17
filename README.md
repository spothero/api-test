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
- allow subsets of tests to be selected
- fail when response has more items than definition
- nbk: Force the tester to utilize all of the structure documented -> right now, if there is no associated test data, it still passes
- nbk: Some errors don't print correctly, for example: 
    ======================================================================
    ERROR: Testing path /facilities/rates/ for response code 200
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/nick/envs/spothero/src/api-test/api_test/test_cases.py", line 57, in runTest
        raise TestConfigurationException(msg=msg)
    TestConfigurationException
    ----------------------------------------------------------------------




How to run this tool:

python manage.py test --api <swagger_file.yaml>
