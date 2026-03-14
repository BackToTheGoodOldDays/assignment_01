import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse


def proxy_request(request, service_name, path=''):
    """Forward requests to the appropriate backend service."""
    base_url = settings.SERVICE_MAP.get(service_name)
    if not base_url:
        return JsonResponse({'error': f'Unknown service: {service_name}'}, status=404)

    # Build target URL - forward full path: /api/{service_name}/{rest_path}
    target_path = f"/api/{service_name}/{path}" if path else f"/api/{service_name}/"
    target_url = f"{base_url}{target_path}"

    # Forward headers (exclude host)
    headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ('host', 'content-length'):
            headers[key] = value

    try:
        method = request.method.lower()
        kwargs = {
            'headers': headers,
            'params': request.GET,
            'timeout': 10,
        }
        if method in ('post', 'put', 'patch'):
            kwargs['data'] = request.body
            if not headers.get('Content-Type'):
                headers['Content-Type'] = 'application/json'

        resp = getattr(requests, method)(target_url, **kwargs)

        return HttpResponse(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': f'Service {service_name} unavailable'}, status=503)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
