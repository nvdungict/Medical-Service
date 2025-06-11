from django.shortcuts import render
from django.http import JsonResponse
from  openai import OpenAI

from service.models import Appointment, Patient
from user.models import User

from .models import Chat
from django.contrib.auth.decorators import login_required

from django.utils import timezone
import os

# messages = [{"role": "system", "content": "Trả lời hết tất cả câu hỏi bằng tiếng anh dù câu hỏi có thể là ngôn ngữ khác tiếng anh"}]
messages = [{"role": "system", "content": ""}]  
def ask_openai(message):
    api_key = ""
    os.environ["OPENAI_API_KEY"] = api_key
    OpenAI.api_key = api_key

    client = OpenAI(api_key=api_key)
    
    messages.append({"role": "user", "content": message})
        
    completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
    )
    
    latest_response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": latest_response})
    return latest_response

@login_required(login_url='login')  
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    user = request.user
    patient = Patient.objects.get(user_id=request.user.id)
    appointments = Appointment.objects.filter(patient=patient).all() or ''
    lastname = patient.lastname or ''
    contact_number = patient.contact_number or ''
    cccd = patient.cccd
    firstname = patient.firstname or ''
    address = patient.address or ''
    dob = patient.dob or ''
    bmi = patient.bmi or ''
    weight = patient.weight or ''
    height = patient.height or ''
    bloodpressure = patient.blood_pressure or ''
    gender = patient.gender or 1
    email = request.user.email 
    content = f"""
        Patient Information:
        - First Name: {firstname}
        - Last Name: {lastname}
        - Contact Number: {contact_number}
        - CCCD: {cccd}
        - Address: {address}
        - Date of Birth: {dob}
        - BMI: {bmi}
        - Weight: {weight}
        - Height: {height}
        - Blood Pressure: {bloodpressure}
        - Gender: {gender}
        - Email: {email}

        Appointments:
        """

    for appointment in appointments:
        appointment_date = appointment.appointment_date or 'N/A'
        start_time = appointment.start_time or 'N/A'
        status = appointment.status or 'N/A'
        doctor_name = appointment.doctor.__str__() if appointment.doctor else 'N/A'
        service_name = appointment.service.service_name if appointment.service else 'N/A'
        room_id = appointment.room_id.__str__() if appointment.room_id else 'N/A'
        created = appointment.created or 'N/A'
    
        content += f"""
            - Appointment ID: {appointment.appointment_id}
            - Date: {appointment_date}
            - Start Time: {start_time}
            - Status: {status}
            - Doctor: {doctor_name}
            - Service: {service_name}
            - Room: {room_id}
            - Created On: {created}
            """
        
    print(content)
    content += "This is my information. You are Clinic Chatbot. You will only answer question about me or relavant to healh problems. Every questions not related to my information and health problems is forbidden"
    messages[0]["content"] = content
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot/chatbot.html', {'chats': chats})
