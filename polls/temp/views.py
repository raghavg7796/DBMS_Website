from django.shortcuts import render, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context, Template,RequestContext
import datetime
import hashlib
from random import randint
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template.context_processors import csrf
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound  
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from base64 import b64encode
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from collections import namedtuple
from django.template import RequestContext
import datetime
import pymysql

import MySQLdb;
def connect():
	db = pymysql.connect(host='localhost', user='root', passwd='Qwerty@123', db='dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	return db, cursor
# Create your views here.

@login_required
@csrf_protect
@csrf_exempt
def payment(request,username):
	db = pymysql.connect(host='localhost', user='root', passwd='Qwerty@123', db='dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	# Amount Calculaion
	company = request.POST['company']
	model = request.POST['model']
	address = request.POST['address']
	phone = request.POST['phone']
	quantity = int(request.POST['quantity'])
	user_id = request.user.id
	amount = float(request.POST['amount'])
	
	MERCHANT_KEY = "zkHhZ9b8"
	key="zkHhZ9b8"
	SALT = "DfbyayHWeu"
	PAYU_BASE_URL = "https://secure.payu.in/_payment"
	action = ''
	posted={}
	posted['email'] = str(request.user.email).upper()

	for i in request.POST:
		posted[i]=request.POST[i]

	hash_object = hashlib.sha256(b'randint(0,20)')
	txnid=hash_object.hexdigest()[0:20]
	hashh = ''
	posted['txnid']=txnid
	posted['amount']=amount
	posted['firstname']=str(request.user.first_name).upper()
	posted['lastname']=str(request.user.last_name).upper()
	hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
	posted['key']=key
	posted['surl']="https://127.0.0.1:8000/Failure"
	posted['furl']="127.0.0.1:8000/Failure"

	hash_string=''
	hashVarsSeq=hashSequence.split('|')
	for i in hashVarsSeq:
		try:
			hash_string+=str(posted[i])
		except Exception:
			hash_string+=''
		hash_string+='|'
	hash_string+=SALT
	#print "woo",hash_string,"woo"
	hashh=hashlib.sha512(hash_string).hexdigest().lower()
	#print "hii",hashh
	action = PAYU_BASE_URL

	if(posted.get("key")!=None and posted.get("txnid")!=None and posted.get("company")!=None and posted.get("model")!=None and posted.get("firstname")!=None and posted.get("email")!=None):

		datex=datetime.datetime.now()
		date=str(datex.day)+"/"+str(datex.month)+"/"+str(datex.year)
		addr=posted['address']
		#query="INSERT INTO orderx(order_date,shipping_address,amount,payment_left,shipping_status,reached) VALUES('%s','%s','%s','%s','%s','%s')"%(date,addr,amount,amount,0,0)
		#cur.execute(query)
		#db.commit()
		return render_to_response('polls/current_datetime.html',{'user':userx,"posted":posted,"hashh":hashh,"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,"action":"https://secure.payu.in/_payment" })
	else:
		return render_to_response('polls/current_datetime.html',{'user':userx,"posted":posted,"hashh":hashh,"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,"action":"." })

@csrf_protect
@csrf_exempt
def success(request):
	c = {}
    	c.update(csrf(request))
	status=request.POST["status"]
	firstname=request.POST["firstname"]
	amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="DfbyayHWeu"
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq).hexdigest().lower()
	if(hashh !=posted_hash):
		print "Invalid Transaction. Please try again"
	else:
		print "Thank You. Your order status is ", status
		print "Your Transaction ID for this transaction is ",txnid
		print "We have received a payment of Rs. ", amount ,". Your order will soon be shipped."
	return render_to_response('sucess.html',RequestContext(request,{"txnid":txnid,"status":status,"amount":amount}))


@csrf_protect
@csrf_exempt
def failure(request):
	c = {}
    	c.update(csrf(request))
	status=request.POST["status"]
	firstname=request.POST["firstname"]
	amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="DfbyayHWeu"
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq).hexdigest().lower()
	if(hashh !=posted_hash):
		print "Invalid Transaction. Please try again"
	else:
		print "Thank You. Your order status is ", status
		print "Your Transaction ID for this transaction is ",txnid
		print "We have received a payment of Rs. ", amount ,". Your order will soon be shipped."
 	return render_to_response("Failure.html",RequestContext(request,c))

	
