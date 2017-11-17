from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
import pymysql
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text

# Create your views here.
def login_view(request):
	context = {}
	return 	render(request, 'log/login.html', context)

def logout_view(request):
	logout(request)
	if request.GET and 'next' in request.GET:
		return HttpResponseRedirect(request.GET['next'])
	else:
		return HttpResponseRedirect(reverse('shop:home_url'))



