from rest_framework import serializers
from content.models import Course, Lesson, Quiz, Question, Answer, Resource




class MentorCourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.safe_name", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title_uz", "title_ru", "slug",
            "description_uz", "description_ru",
            "price", "discount_price",
            "duration_hours", "level",
            "category", "category_name",
            "is_published", "thumbnail",
            "created_at", "updated_at"
        ]
        read_only_fields = ("slug", "created_at", "updated_at")



class MentorLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id", "title_uz", "title_ru",
            "content_uz", "content_ru",
            "video_id",
            "order", "weight",
            "is_preview",
            "status", "vdocipher_status",
            "rejection_reason"
        ]
        read_only_fields = ("video_id", "status", "vdocipher_status", "rejection_reason")




class MentorQuizSerializer(serializers.ModelSerializer):
    title_uz = serializers.CharField(read_only=True)
    title_ru = serializers.CharField(read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title_uz", "title_ru", "passing_score"]





class MentorQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text_uz", "text_ru", "order"]




class MentorAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text_uz", "text_ru", "is_correct"]



class MentorResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "title", "file", "file_type", "created_at"]
        read_only_fields = ("file_type", "created_at")



class VideoUploadInitSerializer(serializers.Serializer):
    upload_url = serializers.CharField()
    clientPayload = serializers.DictField()
    video_id = serializers.CharField()
