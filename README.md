# Flask JSONAPI Trivial

Provides Flask with *very basic* compliance with JSONAPI.org. It enables easy
construction of APIs that return JSON.

Statuses or exceptions generated by the following modules are automatically
transformed to JSONAPI while keeping the correct HTTP headers:

- http.HTTPStatus
- Jose (for JWT exceptions)
- Werkzeug (for Flask itself)

Note, all exceptions raised by Jose (for JWT exceptions) are converted to
Werkzeug Unauthorized 401 exceptions. Extra information about the JWT
error is added to the returned JSON.


## Example

See [example.py](example.py) for example implementation.