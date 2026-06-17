import logging
import requests
from requests.exceptions import RequestException

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse

# Set up logging for the frontend
logger = logging.getLogger(__name__)

def index(request: HttpRequest) -> HttpResponse:
    """
    Main landing page view. 
    Handles fetching data from the internal API and submitting inquiry forms.
    """
    # 1. Prepare the authorization header using the secret from .env
    headers = {
        "Authorization": f"Bearer {getattr(settings, 'API_SHARED_SECRET', '')}",
        "Referer": getattr(settings, 'API_BASE',''),
    }

    # -------------------------------------------------------------------------
    # POST: Handle Contact/Inquiry Form Submission
    # -------------------------------------------------------------------------
    if request.method == 'POST':
        data = {
            'full_name': request.POST.get('name'),
            'email_address': request.POST.get('email'),
            'phone_number': request.POST.get('phone', ''),
            'subject': request.POST.get('subject'),
            'message': request.POST.get('message'),
            'ppts': request.POST.get('ppts') == 'true',
        }
        
        try:
            # REPLACE <YOUR_API_PREFIX> with the actual prefix from your main urls.py
            # Example: f"{settings.API_BASE}/v1/inquiries/"
            api_post_url = f"{settings.API_BASE}/inquiries/"
            
            res = requests.post(
                api_post_url, 
                json=data, 
                headers=headers, 
                timeout=5
            )
            
            if res.status_code == 201:
                messages.success(request, "Your message has been received. We'll be in touch soon!")
            else:
                logger.error(f"API POST Error ({res.status_code}): {res.text[:200]}")
                
                try:
                    error_msg = res.json().get('error', 'An unexpected error occurred.')
                except ValueError:
                    # Catches HTML error pages (like 403 CSRF or 404 Not Found)
                    error_msg = "We couldn't process your request right now due to a server configuration issue."
                    
                messages.error(request, f"There was an issue submitting your form: {error_msg}")
                
        except RequestException as e:
            logger.exception(f"Frontend failed to reach API for POST: {e}")
            messages.error(request, "Service unavailable. Please try again later.")
            
        # Always redirect after a successful POST (Post/Redirect/Get pattern)
        return redirect('zumex:index')

    # -------------------------------------------------------------------------
    # GET: Fetch Active Content for the Frontend
    # -------------------------------------------------------------------------
    recent_projects = []
    testimonials = []
    
    try:
        # REPLACE <YOUR_API_PREFIX> with the actual prefix from your main urls.py
        # Example: f"{settings.API_BASE}/v1/zumex-home/"
        api_get_url = f"{settings.API_BASE}/zumex-home/"
        
        response = requests.get(
            api_get_url, 
            headers=headers, 
            timeout=5
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                recent_projects = data.get('projects', [])
                testimonials = data.get('testimonials', [])
            except ValueError:
                # Catches cases where a 200 OK response is an HTML page (like the Admin Login)
                logger.error(f"Expected JSON but got HTML from GET. The API URL is likely incorrect. URL called: {api_get_url}. Snippet: {response.text[:200]}")
        else:
            logger.warning(f"API returned status {response.status_code} on GET. URL called: {api_get_url}")
            
    except RequestException as e:
        logger.exception(f"Frontend failed to reach API for GET: {e}")

    context = {
        'recent_projects': recent_projects,
        'testimonials': testimonials,
    }
    
    return render(request, 'zumex/index.html', context)