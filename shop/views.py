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
import base64


def add_navbar_context(context):
	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)

	sql = """select c.name as company, c.image, count(i.model) as count
		from inverter_company as c
		left join inverter as i on c.name = i.company
		group by c.name
		"""
	cursor.execute(sql)
	context['inverter_company_list'] = cursor.fetchall()

	sql = """select c.name as company, c.image, count(i.model) as count
		from inverter_company as c
		left join inverter as i on c.name = i.company
		group by c.name
		having count > 0
		"""
	cursor.execute(sql)
	context['company_quant_list'] = cursor.fetchall()

	sql = "select distinct battery_system from inverter";
	cursor.execute(sql)
	context['inverter_battery_system_list'] = cursor.fetchall()

	db.close()

# Create your views here.
def home_view(request):
	context = {}
	add_navbar_context(context)
	return 	render(request, 'shop/home.html', context)

def inverter_view(request):
	context = {}
	add_navbar_context(context)

	if 'company_filter' in request.GET:
		company = request.GET['company_filter']
	else:
		company = '%'

	if 'battery_system_filter' in request.GET:
		battery_system = request.GET['battery_system_filter']
	else:
		battery_system = '%'

	sql = """
		select i.model, i.company, i.price, i.warranty, i.weight, i.battery_system, i.recharge_time, i.image, round(avg(r.star), 1) as star 
		from inverter as i
		left join inverter_review as r on i.company = r.company and i.model = r.model
		where i.company like '%s' and i.battery_system like '%s'
		group by i.model, i.company, i.price, i.warranty, i.weight, i.battery_system, i.recharge_time, i.image
		"""%(company, battery_system);
	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	cursor.execute(sql)
	result = cursor.fetchall()
	db.close()
	
	context['inverter_list'] = result
	context['company'] = company
	context['battery_system'] = battery_system
	return render(request, 'shop/inverter.html', context)

def inverter_product_view(request, company, model):
	context = {}
	add_navbar_context(context)

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	if request.POST and 'rating' in request.POST and request.POST['rating'] and 'title' in request.POST and request.POST['title'] and 'text' in request.POST and request.POST['text']:
		star = int(request.POST['rating'])
		title = request.POST['title']
		text = request.POST['text']
		user_id = int(request.user.id)

		sql = """
			select *
			from inverter_review
			where company like '%s' and model like '%s' and user_id = %d
			"""%(company, model, user_id)

		cursor.execute(sql)
		result = cursor.fetchall()
		if len(result) >= 1:
			context['error_message'] = 'You have already reviewed the Product.'

		else:
			sql = """
				insert into inverter_review(company, model, user_id, star, title, text)
				values('%s', '%s', %d, %d, '%s', '%s')
				"""%(str(company), str(model), user_id, star, str(title), str(text))		
			cursor.execute(sql)
			db.commit()

	sql = """
		select i.model, i.company, i.price, i.warranty, i.weight, i.battery_system, i.image, i.recharge_time, i.quantity, round(avg(r.star), 1) as star, i.description
		from inverter as i
		left join inverter_review as r on i.company = r.company and i.model = r.model 
        inner join inverter_company as c on i.company = c.name
		where i.company like '%s' and i.model like '%s'
		group by i.model, i.company, i.price, i.warranty, i.weight, i.battery_system, i.recharge_time, i.quantity, i.description, i.image
		"""%(company, model);
	cursor.execute(sql)
	result = cursor.fetchone()
	context['inverter'] = result

	sql = """
		select a.first_name, a.last_name, a.email, i.star, i.title, i.text
		from inverter_review as i, auth_user as a
		where i.company like '%s' and i.model like '%s' and i.user_id = a.id
		"""%(company, model);
	cursor.execute(sql)
	result = cursor.fetchall()
	context['reviews'] = result
	context['user_reviews_list'] = [rev['email'] for rev in result]

	sql = """
		select distinct user_id
		from inverter_order
		where company like '%s' and model like '%s'
		"""%(company, model)
	cursor.execute(sql)
	result = cursor.fetchall()
	context['user_orders_list'] = [res['user_id'] for res in result]

	db.close()

	return render(request, 'shop/inverter_product.html', context)

@login_required
def inverter_order_view(request, company, model):
	context = {}
	add_navbar_context(context)

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """
		select i.model, i.image, i.company, i.price, i.warranty, i.weight, i.battery_system, i.recharge_time
		from inverter as i
		where i.company like '%s' and i.model like '%s'
		"""%(company, model)
	cursor.execute(sql)
	result = cursor.fetchone()
	db.close()
	context['inverter'] = result
	return render(request, 'shop/order_inverter.html', context)

@csrf_protect
@csrf_exempt
@login_required
def inverter_place_order_view(request):
	company = request.POST['company']
	model = request.POST['model']
	address = request.POST['address']
	phone = request.POST['phone']
	quantity = int(request.POST['quantity'])
	user_id = request.user.id
	amount = quantity * float(request.POST['price'])
	
	MERCHANT_KEY = "zkHhZ9b8"
	key="zkHhZ9b8"
	SALT = "DfbyayHWeu"
	PAYU_BASE_URL = "https://secure.payu.in/_payment"
	action = ''
	hash_object = hashlib.sha256(b'randint(0,20)')
	txnid=hash_object.hexdigest()[0:20]
	hashh = ''

	posted={}
	for i in request.POST:
		posted[i]=request.POST[i]
	posted['txnid']=txnid
	posted['amount']=amount
	posted['firstname']=str(request.user.first_name).upper()
	posted['lastname']=str(request.user.last_name).upper()
	posted['email'] = str(request.user.email).upper()
	hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
	posted['key']=key
	posted['surl']="https://127.0.0.1:8000/shop/success"
	posted['furl']="127.0.0.1:8000/shop/failure"
	posted['amount']=amount

	hash_string=''
	hashVarsSeq=hashSequence.split('|')
	for i in hashVarsSeq:
		try:
			hash_string+=str(posted[i])
		except Exception:
			hash_string+=''
		hash_string+='|'
	hash_string+=SALT
	hashh=hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
	action = PAYU_BASE_URL

	if(posted.get("key")!=None and posted.get("txnid")!=None and posted.get("company")!=None and posted.get("model")!=None and posted.get("firstname")!=None and posted.get("email")!=None):
		return render(request, 'shop/current_datetime.html', {"posted":posted,"hashh":hashh,"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,"action":"https://secure.payu.in/_payment" })

	context = {}
	add_navbar_context(context)

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """
		select i.model, i.image, i.company, i.price, i.warranty, i.weight, i.battery_system, i.recharge_time
		from inverter as i
		where i.company like '%s' and i.model like '%s'
		"""%(company, model)
	cursor.execute(sql)
	result = cursor.fetchone()
	db.close()
	context['inverter'] = result
	return render(request, 'shop/order_inverter.html', context)

@login_required
@csrf_protect
@csrf_exempt
def success(request):
	c = {}
	c.update(csrf(request))
	
	try:
		status=request.POST["status"]
	except:
		return redirect(home_url)
	
	firstname=request.POST["firstname"]
	amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="KJfs9LzBqo"
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq).hexdigest().lower()
	if(hashh !=posted_hash):
		print ("Invalid Transaction. Please try again")
	else:
		print ("Thank You. Your order status is ", status)
		print ("Your Transaction ID for this transaction is ",txnid)
		print ("We have received a payment of Rs. ", amount ,". Your order will soon be shipped.")
	db,cur=connect()
	query="INSERT into fee(amount,dateofdeposit,student_id,batch_id) values('%d',curdate(),'%d','%d')"%(int(float(amount)),int(firstname),int(productinfo))
	cur.execute(query)
	db.commit()
	return render(request, 'portal/success.html', {"txnid":txnid,"status":status,"amount":amount})

@login_required
@csrf_protect
@csrf_exempt
def failure(request):
	c = {}
	c.update(csrf(request))
	try:
		status=request.POST["status"]
	except:
		return redirect(login)
	firstname=request.POST["firstname"]
	amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="KJfs9LzBqo"
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq).hexdigest().lower()
	if(hashh !=posted_hash):
		print ("Invalid Transaction. Please try again")
	else:
		print("Thank You. Your order status is ", status)
		print("Your Transaction ID for this transaction is ",txnid)
		print("We have received a fee payment of Rs. ", amount)

	return render_to_response("shop/failure.html",RequestContext(request,c))

@login_required
def inverter_all_orders_view(request):
	context = {}
	add_navbar_context(context)

	if 'company_filter' in request.GET:
		company = request.GET['company_filter']
	else:
		company = '%'

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	if request.user.is_superuser:
		sql = """select i.id, i.time, a.first_name, a.last_name, a.email, i.company, i.model, i.address, i.phone, i.quantity, i.status
			from inverter_order as i, auth_user as a
			where i.company like '%s' and i.user_id = a.id
			"""%(company)
	else:
		sql = """select i.id, i.time, a.first_name, a.last_name, a.email, i.company, i.model, i.address, i.phone, i.quantity, i.status
			from inverter_order as i, auth_user as a
			where i.company like '%s' and a.id = %d and a.id = i.user_id
			"""%(company, request.user.id)

	cursor.execute(sql)
	result = cursor.fetchall()
	context['orders_list'] = result
	db.close()

	context['company'] = company
	return render(request, 'shop/all_orders.html', context)

@login_required
def inverter_add_company_view(request):
	company = request.POST['company']
	img = request.FILES['pic']
	x = img.read()
	imgenc = base64.encodestring(x)

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	# sql = """insert into inverter_company(name, description, image)
	# 	values('%s', '%s', '%s')
	# 	"""%(company, description, imgenc)
	sql = """insert into inverter_company(name, image)
		values(%s, %s)
		"""
	cursor.execute(sql,(company, imgenc))
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:home_url', args=()))

@login_required
def inverter_add_product_view(request):
	company = str(request.POST['company'])
	description = request.POST['description']
	model = str(request.POST['model'])
	price = float(request.POST['price'])
	warranty = float(request.POST['warranty'])
	weight = float(request.POST['weight'])
	batt = request.POST['Battery_System']
	rech = float(request.POST['recharge_time'])
	img = request.FILES['pic_inverter']
	x = img.read()
	imgenc = base64.encodestring(x)

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """insert into inverter(company, description, model, price, warranty, weight, battery_system, recharge_time, quantity, image)
		values(%s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
		"""
	cursor.execute(sql,(company, description, model, price, warranty, weight, batt, rech, imgenc))
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_url', args=()))

@login_required
def inverter_delete_product_view(request, company, model):

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """delete from inverter
		where company like '%s' and model like '%s'
		"""%(company, model)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_url', args=()))


@login_required
def inverter_delete_company_view(request, company):
	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """delete from inverter_company
		where name like '%s'
		"""%(company)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:home_url', args=()))

@login_required
def inverter_change_price_view(request, company, model):
	price = float(request.POST['price'])

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter
		set price = %f
		where company like '%s' and model like '%s'
		"""%(price, company, model)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_product_url', args=(company, model)))

@login_required
def inverter_change_warranty_view(request, company, model):
	warranty = float(request.POST['warranty'])

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter
		set warranty = %f
		where company like '%s' and model like '%s'
		"""%(warranty, company, model)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_product_url', args=(company, model)))

@login_required
def inverter_change_weight_view(request, company, model):
	weight = float(request.POST['weight'])

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter
		set weight = %f
		where company like '%s' and model like '%s'
		"""%(weight, company, model)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_product_url', args=(company, model)))

@login_required
def inverter_change_quantity_view(request, company, model):
	quantity = int(request.POST['quantity'])

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter
		set quantity = %d
		where company like '%s' and model like '%s'
		"""%(quantity, company, model)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_product_url', args=(company, model)))

@login_required
def inverter_change_recharge_time_view(request, company, model):
	recharge_time = float(request.POST['recharge_time'])

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter
		set recharge_time = %f
		where company like '%s' and model like '%s'
		"""%(recharge_time, company, model)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_product_url', args=(company, model)))

@login_required
def inverter_change_description_view(request, company, model):
	description = request.POST['description']

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter
		set description = '%s'
		where company like '%s' and model like '%s'
		"""%(description, company, model)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_product_url', args=(company, model)))

@login_required
def inverter_change_photo_view(request, company, model):
	img = request.FILES['pic']
	x = img.read()
	imgenc = base64.encodestring(x)

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter
		set image = %s
		where company like %s and model like %s
		"""
	cursor.execute(sql, (imgenc, company, model))
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_product_url', args=(company, model)))

@login_required
def inverter_change_company_photo_view(request, company):
	img = request.FILES['pic']
	x = img.read()
	imgenc = base64.encodestring(x)

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter_company
		set image = %s
		where name like %s
		"""
	cursor.execute(sql, (imgenc, company))
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:home_url', args=()))

@login_required
def inverter_change_order_status_view(request, order_id):
	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """update inverter_order
		set status = %s
		where id = %s
		"""%(1, order_id)
	cursor.execute(sql)
	db.commit()
	db.close()
	return HttpResponseRedirect(reverse('shop:inverter_all_orders_url', args=()))

@login_required
def inverter_dealers_view(request):
	context = {}
	add_navbar_context(context)

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """select *
		from inverter_dealer
		"""
	cursor.execute(sql)
	result = cursor.fetchall()
	context['dealers_list'] = result
	db.close()

	return render(request, 'shop/dealers.html', context)

@login_required
def inverter_add_dealer_view(request):
	name = request.POST['name']
	phone = request.POST['phone']
	address = request.POST['address']

	db = pymysql.connect(host='raghavg7796.mysql.pythonanywhere-services.com', user='raghavg7796', passwd='Qwerty@123', db='raghavg7796$dbms_database')
	cursor = db.cursor(pymysql.cursors.DictCursor)
	sql = """insert into inverter_dealer(name, address, phone)
		values('%s', '%s', '%s')
		"""%(name, address, phone)
	cursor.execute(sql)
	db.commit()
	db.close()

	return HttpResponseRedirect(reverse('shop:inverter_dealers_url', args=()))