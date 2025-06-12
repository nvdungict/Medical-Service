from django.shortcuts import render
from django.http import JsonResponse
from service.models import Appointment, Patient
from user.models import User

from .models import Chat
from django.contrib.auth.decorators import login_required

from django.utils import timezone
import os
from openai import OpenAI  # sử dụng phiên bản mới từ openai>=1.0.0

# Hàm gọi Together API đúng chuẩn cú pháp mới
def ask_together(message, system_prompt=""):
    client = OpenAI(
        api_key=os.getenv("TOGETHER_API_KEY") or "tgp_v1_hYikuHvLNy5TTejudk0ZiR6CHHQIki3w41qVSg30WEM",
        base_url="https://api.together.xyz/v1"
    )

    try:
        completion = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7
        )

        raw_response = completion.choices[0].message.content

        # 👉 Xử lý định dạng phản hồi
        formatted_response = (
            raw_response
            .replace("1.", "\n\n1.")
            .replace("2.", "\n\n2.")
            .replace("3.", "\n\n3.")
            .replace("4.", "\n\n4.")
            .replace("5.", "\n\n5.")
        )

        return formatted_response

    except Exception as e:
        print("Lỗi gọi Together API:", e)
        return "Xin lỗi, hệ thống đang gặp sự cố khi kết nối AI."




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
        doctor_name = str(appointment.doctor) if appointment.doctor else 'N/A'
        service_name = appointment.service.service_name if appointment.service else 'N/A'
        room_id = str(appointment.room_id) if appointment.room_id else 'N/A'
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
    content += """
You are a Clinical Chatbot designed to provide helpful and accurate information about medical conditions, health advice, and patient information. 
Your main goal is to assist the user by answering questions related to health, wellness, and medical care in a friendly, respectful, and professional manner.

You will only respond to questions related to health or wellness and will not provide information on topics outside of this area. Please ensure you are only providing accurate, medically sound advice when responding.

For any medical concerns, always recommend that the patient consult with a healthcare provider or visit a medical professional for personalized care and advice. 
It is important to maintain patient confidentiality and avoid sharing any sensitive personal information unless absolutely necessary for the conversation.

Your responses should be clear, simple, and understandable for the average patient, avoiding complex medical terminology. If you must use medical terms, explain them in layman’s language.

Remember, you are not a substitute for a healthcare professional and should always encourage patients to seek medical advice from professionals when needed.
"""

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_together(message, system_prompt=content)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})

    return render(request, 'chatbot/chatbot.html', {'chats': chats})
