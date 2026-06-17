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
    # We attach this to the `requests` call so the BACKEND knows we are legit.

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
            'ppts': request.POST.get('ppts'),
        }

        try:
            res = requests.post(
                f"{settings.API_BASE}/api/inquiries/", 
                json=data, 
                headers=headers, 
                timeout=5

            )

            if res.status_code == 201:
                messages.success(request, "Your message has been received. We'll be in touch soon!")
            else:
                # Log the actual raw error for developers
                logger.error(f"API POST Error ({res.status_code}): {res.text}")
                # Attempt to extract a clean JSON error for the user, otherwise use a generic fallback
                try:
                    error_msg = res.json().get('error', 'An unexpected error occurred.')
                except ValueError:
                    error_msg = "We couldn't process your request right now."                
                messages.error(request, f"There was an issue submitting your form: {error_msg}")
        
        except RequestException:
            # logger.exception automatically includes the full traceback in the logs
            logger.exception("Frontend failed to reach API for POST.")
            messages.error(request, "Service unavailable. Please try again later.")

        # Always redirect after a successful POST (Post/Redirect/Get pattern)
        return redirect('zumex:index')

    # -------------------------------------------------------------------------
    # GET: Fetch Active Content for the Frontend
    # -------------------------------------------------------------------------
    recent_projects = []
    testimonials = []

    try:
        response = requests.get(
            f"{settings.API_BASE}/api/zumex-home/", 
            headers=headers, 
            timeout=5
        
        )
        
        if response.status_code == 200:
            data = response.json()
            recent_projects = data.get('projects', [])
            testimonials = data.get('testimonials', [])
        else:
            logger.warning(f"API returned status {response.status_code} on GET home-data. Response: {response.text}")
            
    except RequestException as e:
        logger.exception(f"Frontend failed to reach API for GET home-data : {e}")
        # We pass here because default empty lists are already set above, 
        # allowing the template to render gracefully even if the API is down.

    context = {
        'recent_projects': recent_projects,
        'testimonials': testimonials,
    }

    return render(request, 'zumex/index.html', context) 

