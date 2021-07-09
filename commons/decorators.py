from functools import wraps
from rest_framework.response import Response


def paginate(serializer_class):
    def decorator(func):
        @wraps(func)
        def wrapped(view, user, request):
            queryset = func(view, user, request)
            page = view.paginate_queryset(queryset)
            if page is not None:
                serializer = serializer_class(page, many=True)
                return view.get_paginated_response(serializer.data)
            serializer = serializer_class(queryset, many=True)
            return Response(serializer.data)
        return wrapped
    return decorator
