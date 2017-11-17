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
	if request.POST and 'username' in request.POST and 'password' in request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return HttpResponseRedirect(reverse('shop:home_url'))
		else:
			context = {'error_message': 'No such customer exists'}
			return render(request, 'log/login.html', context)
		
	else:
		context = {}
		return 	render(request, 'log/login.html', context)

def signup_view(request):
	if request.POST and 'email' in request.POST and 'password' in request.POST and 'fname' in request.POST and 'username' in request.POST:
		email = request.POST['email']
		password = request.POST['password']
		username = request.POST['username']
		fname = request.POST['fname']
		lname = request.POST['lname']

		if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
			return render(request, 'log/signup.html', {'error_message': 'Email or Username already exists'})
		else:
			user = User.objects.create_user(username=username, password=password, email=email, first_name=fname, last_name =lname)
			user.is_active = False
			user.save()
			current_site = get_current_site(request)
			message = render_to_string('log/acc_active_email.html', {
			    'user':user, 
			    'domain':current_site.domain,
			    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			    'token': account_activation_token.make_token(user),
			})
			mail_subject = 'Activate your Account.'
			email_message = EmailMessage(mail_subject, message, to=[email])
			try:
				email_message.send()
			except:
				context = {'error_message': 'Connection Error! Try Again.'}
				return render(request, 'log/signup_view.html', context)
			else:
				context = {'email': email}
				return render(request, 'log/verif_confirm.html', context)

	else:
		context = {}
		return render(request, 'log/signup.html', context)

def activate_view(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user, backend='django.contrib.auth.backends.ModelBackend')
		context = {'error_message': 'Email Verified! Log In to Continue.'}
		return render(request, 'log/login.html', context)
	# return redirect('home')

	else:
		return HttpResponse('Activation link is invalid!')

def logout_view(request):
	logout(request)
	if request.GET and 'next' in request.GET:
		return HttpResponseRedirect(request.GET['next'])
	else:
		return HttpResponseRedirect(reverse('shop:home_url'))



