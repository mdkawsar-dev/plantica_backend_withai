from rest_framework.views import exception_handler
from rest_framework import status as http_status
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework to format all errors
    into the standard Plantica JSON response structure:
    {
        "status": false,
        "message": "Error description",
        "data": error_details,
        "code": status_code
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        error_data = response.data

        # Extract readable error message
        if isinstance(error_data, dict):
            if 'detail' in error_data:
                message = str(error_data['detail'])
            elif 'non_field_errors' in error_data:
                message = str(error_data['non_field_errors'][0])
            else:
                first_key = next(iter(error_data))
                val = error_data[first_key]
                if isinstance(val, list) and len(val) > 0:
                    message = f"{first_key}: {val[0]}"
                else:
                    message = f"{first_key}: {val}"
        elif isinstance(error_data, list) and len(error_data) > 0:
            message = str(error_data[0])
        else:
            message = str(error_data)

        response.data = {
            "status": False,
            "message": message,
            "data": error_data,
            "code": status_code
        }
    else:
        # Fallback for unhandled 500 server errors
        response = Response(
            {
                "status": False,
                "message": f"Internal Server Error: {str(exc)}",
                "data": None,
                "code": http_status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
