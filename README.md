This tool is intended to read a swagger 2.0 spec compliant yaml file and dynamically generate tests.
The tests will use any test data listed in the spec file and compare defined responses to actual responses.

This tool currently only supports get requests and 200 responses.

How to run this tool:
python manage.py test --api <swagger_file.yaml>


### x-test syntax
We extend swagger [Path Item Objects](http://swagger.io/specification/#operationObject) with an `x-test` key,
that contains information to form tests on that path. The `x-test` object is a list of "test" objects.
Each "test" object contains two keys: `data` and `parameters`:

 - `data` is a list of model objects (represented as dictionaries) that should be created in the setup of the test. 
 Each model object dictionary contains a `model` key, indicating the type of object, and the other keys represent 
 specifications about that model object, to be used on model creation.
 - `parameters` is a dictionary of request parameters (whether query, path, form, or otherwise) to be sent with the
 request used for that test.

When running each test, first the data will be loaded into the database, and then the request will be made with the 
specified parameters, and the defined response compared with actual response to determine success.


### Data Loader
`API_TEST_DATA_LOADER` is a settings config variable that must be set in the parent django app (i.e. the application
importing this plugin). It should point to a function used to import the "data" into the database in the setup of each test.

The function takes 2 inputs:

- `object_name`: a string representing the type of model object to be created, corresponding to the `model` key in 
the `data` dictionary above.
- `data`: a dict representing specifications about the model object being created, corresponding to everything in 
the `data` dict above, but without the `model` key.

The function should load the model object into the database with the specified data.


Test Tool Roadmap:
- test that all endpoints are documented
- support all http method requests
- test for error responses (400, 422, 428...) 
  - test that not passing listed required params results in field errors for each method
- test for permissions
  - set of test users to try for all endpoints
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

