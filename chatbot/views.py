from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from service.models import Appointment, Patient
from user.models import User
from .models import Chat

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Cấu hình thiết bị và model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "Qwen/Qwen1.5-1.8B-Chat"

# Load model và tokenizer
# print("Loading Qwen 1.5 1.8B Chat...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

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

    patient_info = f"""
Use my information to answer the question. You are Clinic Chatbot that only gives short and concise answers. You will only answer question about me or relavant to healh problems. Every questions not related to my information and health problems is forbidden:

My Information:
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
    
        patient_info += f"""
            - Appointment ID: {appointment.appointment_id}
            - Date: {appointment_date}
            - Start Time: {start_time}
            - Status: {status}
            - Doctor: {doctor_name}
            - Service: {service_name}
            - Room: {room_id}
            - Created On: {created}
            """
    
    if request.method == 'POST':
        user_msg = request.POST.get('message')
        full_prompt = f"{patient_info}\nQuestion: {user_msg}\nAssistant:"

        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True).to(device)
        output_ids = model.generate(
            **inputs,
            max_new_tokens=160,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        response_text = decoded.split("Assistant:")[-1].strip()

        chat = Chat(user=request.user, message=user_msg, response=response_text, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': user_msg, 'response': response_text})

    return render(request, 'chatbot/chatbot.html', {'chats': chats})
