from rest_framework import serializers
from content.models import Lesson
from authentication.models import CustomUser

class ChatLessonSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    teacher_id = serializers.IntegerField(source="course.instructor.mentor.user.id", read_only=True)

    class Meta:
        model = Lesson
        fields = ["id", "course_id", "teacher_id"]



class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "is_mentor", "first_name", "last_name"]
