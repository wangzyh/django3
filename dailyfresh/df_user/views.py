# coding:utf-8
from django.shortcuts import render, redirect
from models import *
from hashlib import sha1
from django.http import JsonResponse, HttpResponseRedirect
from . import user_decorator
from df_goods.models import *
from df_order.models import *


def register(request):
    return render(request, 'df_user/register.html')


def register_handle(request):
    # 接收用户输入
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')
    # 判断两次密码
    if upwd != upwd2:
        return redirect('/user/register/')
    # 密码加密
    s1 = sha1()
    s1.update(upwd)
    upwd3 = s1.hexdigest()

    # 创建对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()
    # 注册成功,转到登陆页面
    return redirect('/user/login/')


def register_exist(request):
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count': count})


def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {'title': '用户登陆', 'error_name': 0, 'error_pwd': 0, 'uname': uname}
    return render(request, 'df_user/login.html', context)


def login_handle(request):
    # 接收请求信息
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu = post.get('jizhu', 0)
    # 根据用户名查询对象
    users = UserInfo.objects.filter(uname=uname)  # 查不到返回[]
    print(uname)
    # 判断:如果未查到则用户名错，如果查到则判断密码是否正确，正确则转到用户中心
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd)
        if s1.hexdigest() == users[0].upwd:
            url = request.COOKIES.get('url', '/')
            red = HttpResponseRedirect(url)
            # 记住用户名
            if jizhu != 0:
                red.set_cookie('uname', uname)
            else:
                red.set_cookie('uname', '', max_age=-1)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:
            context = {'title': '用户登陆', 'error_name': 0, 'error_pwd': 1, 'uname': uname, 'upwd':upwd}
            return render(request, 'df_user/login.html', context)
    else:
        context = {'title': '用户登陆', 'error_name': 1, 'error_pwd': 0, 'uname': uname, 'upwd': upwd}
        return render(request, 'df_user/login.html', context)


def info_handle(request):
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    user = UserInfo()

    return redirect('/user/info/')


@user_decorator.login
def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    # user_phone = UserInfo.objects.get(id=request.session['user_id']).uphone
    # GoodInfo.objects.filter(id__in=goods_ids1)
    # 最近浏览
    goods_ids = request.COOKIES.get('goods_ids', '')
    goods_ids1 = goods_ids.split(',')
    goods_list = []
    if goods_ids:
        for goods_id in goods_ids1:
            goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))

    context = {'title': '用户中心',
               'page_name': 1,
               'user_email': user_email,
               'user_name': request.session['user_name'],
               'goods_list': goods_list}
    return render(request, 'df_user/user_center_info.html', context)


@user_decorator.login
def order(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    order = OrderInfo(user=user)
    context = {'title': '用户中心', 'page_name': 1,
               'order': order}
    return render(request, 'df_user/user_center_order.html', context)


@user_decorator.login
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uzipcode = post.get('uzipcode')
        user.uphone = post.get('uphone')
        user.save()
    context = {'title': '用户中心', 'user': user, 'page_name': 1}
    return render(request, 'df_user/user_center_site.html', context)


def logout(request):
    request.session.flush()
    return redirect('/')

