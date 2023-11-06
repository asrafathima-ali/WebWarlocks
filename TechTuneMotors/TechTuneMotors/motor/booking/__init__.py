from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('staffPanel')  # Redirect to the staff panel upon successful login
        else:
            return render(request, 'anagha.html', {'error_message': 'Invalid username or password'})
    return render(request, 'anagha.html')
