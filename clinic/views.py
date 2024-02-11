"""
IVF Clinic Management API views.

Provides endpoints for patient authentication, health profile management,
DASS psychological tests (Depression Anxiety Stress Scale), test results,
notifications with Expo push, AWS S3 presigned URLs for image uploads,
and a CRM dashboard for clinic staff.
"""
import json
import hashlib
import uuid
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from .models import Client, Notification, TestResult, Translation, AdminUser, CustomerNote


@api_view(['POST'])
def login(request):
    """Authenticate a client by hashed email+password."""
    data = request.data
    email = data.get("email", "")
    password = data.get("password", "")
    hashed = hashlib.sha256(f"{email}{password}".encode()).hexdigest()

    try:
        client = Client.objects.get(hashed_email_and_password=hashed)
        token = str(uuid.uuid4())[:32]
        client.user_token = token
        client.logged_in = True
        client.save()
        return JsonResponse({
            "success": True,
            "token": token,
            "client_id": client.id,
            "first_name": client.first_name,
            "last_name": client.last_name,
        })
    except Client.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=401)


@api_view(['POST'])
def logout(request):
    """Log out a client by clearing their token."""
    token = request.data.get("token")
    try:
        client = Client.objects.get(user_token=token)
        client.logged_in = False
        client.user_token = None
        client.save()
        return JsonResponse({"success": True})
    except Client.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=401)


@api_view(['GET'])
def get_user_data(request):
    """Return full client profile including test counts and notification summary."""
    token = request.GET.get("token")
    try:
        client = Client.objects.get(user_token=token)
        unread = Notification.objects.filter(client=client, notification_status='unread').count()
        return JsonResponse({
            "client": {
                "id": client.id,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "email": client.email,
                "weight": str(client.weight) if client.weight else None,
                "height": str(client.height) if client.height else None,
                "date_of_birth": str(client.date_of_birth) if client.date_of_birth else None,
                "cycle_type": client.cycle_type,
                "dass_tests_taken": client.dass_tests_taken,
                "profile_image": client.profile_image,
                "language": client.language,
                "period_dates": client.period_dates,
            },
            "unread_notifications": unread,
        })
    except Client.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=401)


@api_view(['PUT'])
def edit_client(request):
    """Update client profile fields."""
    data = request.data
    token = data.get("token")
    try:
        client = Client.objects.get(user_token=token)
        for field in ["first_name", "last_name", "weight", "height", "cycle_type",
                      "period_length", "menstrual_cyclus_length", "language",
                      "address", "city", "country", "postal_code", "telephone"]:
            if field in data:
                setattr(client, field, data[field])
        client.save()
        return JsonResponse({"success": True})
    except Client.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=401)


@api_view(['POST'])
def dass_test_results(request):
    """
    Submit DASS (Depression Anxiety Stress Scale) test results.
    Calculates severity levels and stores both raw and final results.
    """
    data = request.data
    token = data.get("token")
    raw_answers = data.get("answers", [])

    try:
        client = Client.objects.get(user_token=token)
    except Client.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=401)

    # DASS scoring: sum scores for each subscale
    depression = sum(a.get("score", 0) for a in raw_answers if a.get("subscale") == "depression")
    anxiety = sum(a.get("score", 0) for a in raw_answers if a.get("subscale") == "anxiety")
    stress = sum(a.get("score", 0) for a in raw_answers if a.get("subscale") == "stress")

    def severity(score, thresholds):
        labels = ["Normal", "Mild", "Moderate", "Severe", "Extremely Severe"]
        for i, t in enumerate(thresholds):
            if score <= t:
                return labels[i]
        return labels[-1]

    final_result = {
        "depression": {"score": depression, "severity": severity(depression, [9, 13, 20, 27])},
        "anxiety": {"score": anxiety, "severity": severity(anxiety, [7, 9, 14, 19])},
        "stress": {"score": stress, "severity": severity(stress, [14, 18, 25, 33])},
    }

    test = TestResult.objects.create(
        client=client,
        test_type_id=1,
        raw_test_result=raw_answers,
        final_test_result=final_result,
        test_ordinal_number=(client.dass_tests_taken or 0) + 1,
    )
    client.dass_tests_taken = (client.dass_tests_taken or 0) + 1
    client.save()

    return JsonResponse({"success": True, "result": final_result, "test_id": test.id})


@api_view(['POST'])
def generate_signed_url(request):
    """Generate an AWS S3 presigned URL for profile image upload."""
    import boto3
    token = request.data.get("token")
    file_name = request.data.get("file_name", "profile.jpg")

    try:
        client = Client.objects.get(user_token=token)
    except Client.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=401)

    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
        )
        key = f"profiles/{client.id}/{file_name}"
        url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': settings.AWS_S3_BUCKET, 'Key': key, 'ContentType': 'image/jpeg'},
            ExpiresIn=3600,
        )
        return JsonResponse({"upload_url": url, "key": key})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
def mark_notifications_read(request):
    """Mark specific notifications as read."""
    data = request.data
    notification_ids = data.get("notification_ids", [])
    Notification.objects.filter(id__in=notification_ids).update(notification_status='read')
    return JsonResponse({"success": True})


@api_view(['POST'])
def mark_all_notifications_hidden(request):
    """Hide all notifications for a client."""
    token = request.data.get("token")
    try:
        client = Client.objects.get(user_token=token)
        Notification.objects.filter(client=client).update(notification_status='hidden')
        return JsonResponse({"success": True})
    except Client.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=401)


@api_view(['GET'])
def translations(request):
    """Return translations grouped by language (EN, SR, RU, ZH)."""
    keywords = list(Translation.objects.values_list('keyword', flat=True))
    eng = list(Translation.objects.values_list('english', flat=True))
    sr = list(Translation.objects.values_list('serbian', flat=True))
    ru = list(Translation.objects.values_list('russian', flat=True))
    zh = list(Translation.objects.values_list('chinese', flat=True))
    return JsonResponse({
        "eng": dict(zip(keywords, eng)),
        "sr": dict(zip(keywords, sr)),
        "ru": dict(zip(keywords, ru)),
        "zh": dict(zip(keywords, zh)),
    })


# ---- CRM Views (for clinic staff) ----

@api_view(['POST'])
def crm_login(request):
    """Authenticate a clinic admin user."""
    data = request.data
    try:
        user = AdminUser.objects.get(email=data["email"], password=data["password"])
        return JsonResponse({"success": True, "user_id": user.id, "first_name": user.first_name})
    except AdminUser.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=401)


@api_view(['GET'])
def crm_dashboard(request):
    """Return dashboard with all clients and summary statistics."""
    clients = Client.objects.filter(existing=True)
    return JsonResponse({
        "total_clients": clients.count(),
        "paid_clients": clients.filter(paid=True).count(),
        "clients": [{
            "id": c.id, "name": f"{c.first_name} {c.last_name}",
            "email": c.email, "paid": c.paid,
            "tests_taken": c.dass_tests_taken,
        } for c in clients[:50]],
    })


@api_view(['GET'])
def crm_client_data(request, customer_id):
    """Load detailed client data for CRM view."""
    try:
        c = Client.objects.get(id=customer_id)
        notes = CustomerNote.objects.filter(customer=c).order_by('-datetime')
        tests = TestResult.objects.filter(client=c).order_by('-test_taken_at')
        return JsonResponse({
            "client": {
                "id": c.id, "first_name": c.first_name, "last_name": c.last_name,
                "email": c.email, "telephone": c.telephone, "city": c.city,
                "paid": c.paid, "dass_tests_taken": c.dass_tests_taken,
            },
            "notes": [{"id": n.id, "title": n.note_title, "text": n.note_text}
                      for n in notes],
            "tests": [{"id": t.id, "type": t.test_type_id, "result": t.final_test_result,
                       "date": t.test_taken_at.isoformat()}
                      for t in tests],
        })
    except Client.DoesNotExist:
        return JsonResponse({"error": "Client not found"}, status=404)
