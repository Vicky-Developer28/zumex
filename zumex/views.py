import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings 

API_BASE = settings.API_BASE

def index(request):
    if request.method == 'POST':
        # Handling the contact/inquiry form submission
        data = {
            'full_name': request.POST.get('name'),
            'email_address': request.POST.get('email'),
            'phone_number': request.POST.get('phone'),  # <-- Added this line
            'subject': 'Website Contact Form',
            'message': request.POST.get('message')
        }
        try:
            res = requests.post(f"{API_BASE}/inquiries/", json=data, timeout=5)
            if res.status_code == 201:
                messages.success(request, "Your message has been received. We'll be in touch soon!")
        except requests.exceptions.RequestException:
            messages.error(request, "Service unavailable. Please try again later.")
        return redirect('zumex:index')

    # Fetching active content for the frontend
    recent_projects = []
    testimonials = []
    
    try:
        response = requests.get(f"{API_BASE}/zumex/home-data/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            recent_projects = data.get('projects', [])
            testimonials = data.get('testimonials', [])
    except requests.exceptions.RequestException:
        pass # Handle gracefully on the template

    context = {
        'recent_projects': recent_projects,
        'testimonials': testimonials,
    }
    return render(request, 'zumex/index.html', context)
