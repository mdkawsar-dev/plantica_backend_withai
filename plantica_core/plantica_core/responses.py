from rest_framework.response import Response
from rest_framework import status as http_status

def custom_response(data=None, message="Success", status=True, code=http_status.HTTP_200_OK, headers=None):
    """
    Standardized API Response helper across all Plantica endpoints.
    Format:
    {
        "status": True / False,
        "message": "Response message",
        "data": { ... } or [ ... ] or None,
        "code": 200 / 400 / etc.
    }
    """
    response_payload = {
        "status": status,
        "message": message,
        "data": data,
        "code": code
    }
    return Response(response_payload, status=code, headers=headers)


def success_response(data=None, message="Success", code=http_status.HTTP_200_OK, headers=None):
    """Shortcut helper for success responses."""
    return custom_response(data=data, message=message, status=True, code=code, headers=headers)


def error_response(message="An error occurred", data=None, code=http_status.HTTP_400_BAD_REQUEST, headers=None):
    """Shortcut helper for error responses."""
    return custom_response(data=data, message=message, status=False, code=code, headers=headers)
