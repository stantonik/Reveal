from Reveal.urls import path
from . import views

urlpatterns = [
        path("", views.home, name="home"),
        path("home", views.home, name="home"),
        path("contact", views.contact, name="contact"),
        path("covid19", views.covid19, name="covid19"),
        ]
