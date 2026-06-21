from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme

from app.models import Query, Result, Summary
from app.utils import get_search_results, generate_summary, count_keywords


def signup(request):
    if request.user.is_authenticated:
        return redirect('search')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        email = request.POST.get('email', '').strip()

        if not username or not password:
            messages.error(request, 'Логин и пароль обязательны')
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'signup.html')

        if password != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('search')

    return render(request, 'signup.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('search')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or ''
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('search')
        messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def search(request):
    if request.method == 'POST':
        query_text = request.POST.get('text', '').strip()

        if not query_text:
            messages.warning(request, 'Введите поисковой запрос')
            return render(request, 'search.html')

        query = Query.objects.create(user=request.user, text=query_text)
        results = get_search_results(query_text)

        keywords = query_text.split()
        results.sort(key=lambda x: count_keywords(x['snippet'], keywords), reverse=True)
        top_results = results[:10]

        if top_results:
            Result.objects.bulk_create([
                Result(query=query, title=r['title'], url=r['url'], description=r['snippet'])
                for r in top_results
            ])

        summary_text = generate_summary(top_results)
        Summary.objects.create(query=query, text=summary_text)

        return render(request, 'results.html', {
            'results': top_results,
            'summary': summary_text,
            'query': query_text,
        })

    return render(request, 'search.html')


@login_required
def history(request):
    queries = Query.objects.filter(user=request.user).prefetch_related('results', 'summaries')
    paginator = Paginator(queries, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'history.html', {'page_obj': page_obj})


@login_required
def delete_history(request, query_id):
    if request.method == 'POST':
        Query.objects.filter(id=query_id, user=request.user).delete()
    return redirect('history')


@login_required
def clear_history(request):
    if request.method == 'POST':
        Query.objects.filter(user=request.user).delete()
    return redirect('history')
