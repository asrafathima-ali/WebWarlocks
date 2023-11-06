from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import *
from django.contrib import messages
from django.core.mail import send_mail

def index(request):
    return render(request, "index.html",{})

def booking(request):
    #Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    
    weekdays = validWeekday(22)

    #Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)
    

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        brand = request.POST.get('brand')
        if service == None:
            messages.success(request, "Please Select A Service!")
            return redirect('booking')

        #Store day and service and brand in django session:
        request.session['day'] = day
        request.session['service'] = service
        request.session['brand'] = brand

        return redirect('bookingSubmit')


    return render(request, 'booking.html', {
            'weekdays':weekdays,
            'validateWeekdays':validateWeekdays,
        })



# ... (your existing code)

def bookingSubmit(request):
    user = request.user
    times = [
        "8 AM", "11 AM", "3 PM", "6 PM", "9 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    day = request.session.get('day')
    service = request.session.get('service')
    brand = request.session.get('brand')
    
    #Only show the time of the day that has not been selected before:
    hour = checkTime(times, day)

    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service is not None:
            if day <= maxDate and day >= minDate:
                if date in ['Monday', 'Saturday', 'Wednesday']:
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            # Creating the appointment
                            Appointment.objects.create(
                                user=user,
                                service=service,
                                brand=brand,
                                day=day,
                                time=time,
                            )

                            # Sending email confirmation
                            subject = 'Appointment Confirmation'
                            message = f'Your appointment for {service} on {day} at {time} has been confirmed.'
                            from_email = 'your_email@example.com'  # Update this with your email
                            to_email = user.email  # Assuming user.email exists
                            send_mail(subject, message, from_email, [to_email])
                            
                            messages.success(request, "Your confirmation regarding your appointment sent to registered email!")
                            return redirect('index')
                        else:
                            messages.success(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.success(request, "The Selected Day Is Full!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                messages.success(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service!")

    return render(request, 'bookingSubmit.html', {
        'times': hour,
    })


def userPanel(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('day', 'time')
    return render(request, 'userPanel.html', {
        'user':user,
        'appointments':appointments,
    })

def userUpdate(request, id):
    appointment = Appointment.objects.get(pk=id)
    userdatepicked = appointment.day
    #Copy  booking:
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')

    #24h if statement in template:
    delta24 = (userdatepicked).strftime('%Y-%m-%d') >= (today + timedelta(days=1)).strftime('%Y-%m-%d')
    #Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(22)

    #Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)
    

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        brand = request.POST.get('brand')

        #Store day and service in django session:
        request.session['day'] = day
        request.session['service'] = service
        request.session['brand'] = brand

        return redirect('userUpdateSubmit', id=id)


    return render(request, 'userUpdate.html', {
            'weekdays':weekdays,
            'validateWeekdays':validateWeekdays,
            'delta24': delta24,
            'id': id,
        })

def userUpdateSubmit(request, id):
    user = request.user
    times = [
        "8 AM", "11 AM", "3 PM", "6 PM", "9 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    day = request.session.get('day')
    service = request.session.get('service')
    brand = request.session.get('brand')
    
    #Only show the time of the day that has not been selected before and the time he is editing:
    hour = checkEditTime(times, day, id)
    appointment = Appointment.objects.get(pk=id)
    userSelectedTime = appointment.time
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Saturday' or date == 'Wednesday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1 or userSelectedTime == time:
                            AppointmentForm = Appointment.objects.filter(pk=id).update(
                                user = user,
                                service = service,
                                day = day,
                                time = time,
                                brand = brand,
                            ) 
                            messages.success(request, "Appointment Edited!")
                            return redirect('index')
                        else:
                            messages.success(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.success(request, "The Selected Day Is Full!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                    messages.success(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service!")
        return redirect('userPanel')


    return render(request, 'userUpdateSubmit.html', {
        'times':hour,
        'id': id,
    })


def delete(request, id):
  member = Appointment.objects.get(id=id)
  member.delete()
  messages.success(request, "Appointment Deleted")
  return redirect('staffPanel')



from django.shortcuts import render, HttpResponseRedirect
from datetime import datetime, timedelta
from .models import Appointment

def staffPanel(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        predefined_username = 'admin'
        predefined_password = 'secretpassword'

        if username == predefined_username and password == predefined_password:
            today = datetime.today()
            minDate = today.strftime('%Y-%m-%d')
            deltatime = today + timedelta(days=21)
            strdeltatime = deltatime.strftime('%Y-%m-%d')
            maxDate = strdeltatime
            items = Appointment.objects.filter(day__range=[minDate, maxDate]).order_by('day', 'time')
            return render(request, 'staffPanel.html', {'items': items})
        else:
            # Display the login form again with an error message
            return render(request, 'admin.html', {'error_message': 'Invalid credentials'})

    # Render the login form initially or if the credentials are invalid
    return render(request, 'admin.html')


    
from django.shortcuts import render

def admin(request):
    # Your view logic here
    return render(request, 'admin.html', {
        'admin':'admin login',
    })



    

def dayToWeekday(x):
    z = datetime.strptime(x, "%Y-%m-%d")
    y = z.strftime('%A')
    return y

def validWeekday(days):
    #Loop days you want in the next 21 days:
    today = datetime.now()
    weekdays = []
    for i in range (0, days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y == 'Monday' or y == 'Saturday' or y == 'Wednesday':
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays
    
def isWeekdayValid(x):
    validateWeekdays = []
    for j in x:
        if Appointment.objects.filter(day=j).count() < 10:
            validateWeekdays.append(j)
    return validateWeekdays

def checkTime(times, day):
    #Only show the time of the day that has not been selected before:
    x = []
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1:
            x.append(k)
    return x

def checkEditTime(times, day, id):
    #Only show the time of the day that has not been selected before:
    x = []
    appointment = Appointment.objects.get(pk=id)
    time = appointment.time
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1 or time == k:
            x.append(k)
    return x


