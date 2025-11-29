import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from content.models import Lesson

logger = logging.getLogger(__name__)


# ====================================================================
#       VDOCIPHER WEBHOOK TO MANIPULATE VIDEO INFO ON MY DATABASE
# ====================================================================

@csrf_exempt
def vdocipher_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.info(f"🎬 Received VdoCipher webhook payload: {data}")

        event = data.get("event")
        payload = data.get("payload", {})
        video_id = payload.get("id")

        if not video_id:
            logger.warning("⚠️ No video_id in webhook payload")
            return JsonResponse({"error": "Missing video id"}, status=400)

        try:
            lesson = Lesson.objects.get(video_id=video_id)
        except Lesson.DoesNotExist:
            logger.warning(f"⚠️ No Lesson found for video_id: {video_id}")
            return JsonResponse({"status": "ok", "message": "No matching lesson"}, status=200)

        if event == "video:ready":
            lesson.vdocipher_status = "ready"
            lesson.status = "approved"
        elif event == "video:error":
            lesson.vdocipher_status = "failed"
            lesson.status = "rejected"
            lesson.rejection_reason = payload.get("status", "Unknown error")
        elif event == "video:deleted":
            lesson.vdocipher_status = "pending"
            lesson.status = "pending"
        else:
            logger.info(f"ℹ️ Unknown event: {event}")
            return JsonResponse({"status": "ignored", "event": event})

        lesson.vdocipher_payload = payload
        lesson.save(update_fields=["vdocipher_status", "status", "vdocipher_payload", "rejection_reason"])

        logger.info(f"✅ Lesson {lesson.id} updated successfully for event {event}")
        return JsonResponse({"status": "ok", "event": event, "video_id": video_id})

    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON body in webhook")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.exception("🚨 Error processing VdoCipher webhook")
        return JsonResponse({"error": str(e)}, status=500)
