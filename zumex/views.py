import logging
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

# Set up logging for the frontend
logger = logging.getLogger(__name__)

def index(request):
    """
    Main landing page view. 
    Handles fetching data from the internal API and submitting inquiry forms.
    """
    # 1. Prepare the authorization header using the secret from .env
    # This proves to the backend API that this request is legitimate
    headers = {
        "Authorization": f"Bearer {settings.API_SHARED_SECRET}"
    }

    # -------------------------------------------------------------------------
    # POST: Handle Contact/Inquiry Form Submission
    # -------------------------------------------------------------------------
    if request.method == 'POST':
        data = {
            'full_name': request.POST.get('name'),
            'email_address': request.POST.get('email'),
            'phone_number': request.POST.get('phone'),
            'subject': request.POST.get('subject'),
            'message': request.POST.get('message'),
            'ppts':request.POST.get('ppts'),
        }
        
        try:
            res = requests.post(
                f"{settings.API_BASE}/inquiries/", 
                json=data, 
                headers=headers, 
                timeout=5
            )
            
            if res.status_code == 201:
                messages.success(request, "Your message has been received. We'll be in touch soon!")
            else:
                logger.error(f"API returned status {res.status_code} on POST: {res.text}")
                messages.error(request, "There was an issue submitting your form. Please try again.")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Frontend failed to reach API for POST: {e}")
            messages.error(request, "Service unavailable. Please try again later.")
            
        # Redirect back to the index page to prevent form re-submission on refresh
        return redirect('zumex:index')

    # -------------------------------------------------------------------------
    # GET: Fetch Active Content for the Frontend
    # -------------------------------------------------------------------------
    recent_projects = []
    testimonials = []
    
    try:
        response = requests.get(
            f"{settings.API_BASE}/zumex/home-data/", 
            headers=headers, 
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            recent_projects = data.get('projects', [])
            testimonials = data.get('testimonials', [])
        else:
            logger.warning(f"API returned status {response.status_code} on GET home-data.")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Frontend failed to reach API for GET: {e}")
        # We pass here gracefully so the page still loads (just without projects/testimonials) 
        # rather than crashing the whole site.
        pass 

    # -------------------------------------------------------------------------
    # RENDER: Pass data to the template
    # -------------------------------------------------------------------------
    context = {
        'recent_projects': recent_projects,
        'testimonials': testimonials,
    }
    
    return render(request, 'zumex/index.html', context)
