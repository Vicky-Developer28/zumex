from django.urls import path, include

urlpatterns = [
    path('', include(('zumex.urls', 'zumex'), namespace="zumex")),
]
