"""
backend/middleware

Flask middleware and request/response hooks for the MedSave backend.

Middleware components apply cross-cutting concerns across all requests
such as logging, error handling, and request validation.

This layer is currently a placeholder. As the backend matures,
request logging and error handling middleware will be defined here.

Planned middleware:
    RequestLoggingMiddleware — log all incoming requests with timing.
    ErrorHandlerMiddleware   — standardize error response format.
"""
