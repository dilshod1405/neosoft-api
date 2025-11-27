from rest_framework import serializers
from .models import InstructorProfile, MentorProfile


# ============================================================
#                 INSTRUCTOR PROFILE SERIALIZER
# ============================================================

class InstructorProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = [
            "full_name",
            "bio_uz",
            "bio_ru",
            "expertise",
            "qualifications_uz",
            "qualifications_ru",
            "profile_picture",
            "profile_picture_url",
        ]

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None






# ============================================================
#                 MENTOR SECRET PROFILE SERIALIZER
# ============================================================

class MentorSecretProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorProfile
        fields = [
            "passport_number",
            "passport_issued_by",
            "passport_issue_date",
            "address",
            "card_number",
        ]
        