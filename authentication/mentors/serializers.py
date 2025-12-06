from rest_framework import serializers
from .models import MentorProfile
from content.mentors.models import InstructorProfile


# ============================================================
#                 INSTRUCTOR PROFILE SERIALIZER
# ============================================================

class InstructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = [
            "bio_uz",
            "bio_ru",
            "expertise",
            "qualifications_uz",
            "qualifications_ru",
            "profile_picture",
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
            "passport_expiry_date",
            "address",
            "card_number",
            "pinfl",
            "dob",
        ]


# ============================================================
#               MENTOR UPDATE PROFILE SERIALIZER
# ============================================================

class InstructorInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = [
            "bio_uz",
            "bio_ru",
            "expertise",
            "qualifications_uz",
            "qualifications_ru",
            "profile_picture",
        ]


class MentorFullProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    middle_name = serializers.CharField(source="user.middle_name", read_only=True)

    phone = serializers.CharField(source="user.phone")

    bio_uz = serializers.CharField(source="user.instructor_profile.bio_uz", required=False)
    bio_ru = serializers.CharField(source="user.instructor_profile.bio_ru", required=False)
    expertise = serializers.CharField(source="user.instructor_profile.expertise", required=False)
    qualifications_uz = serializers.CharField(source="user.instructor_profile.qualifications_uz", required=False)
    qualifications_ru = serializers.CharField(source="user.instructor_profile.qualifications_ru", required=False)

    class Meta:
        model = MentorProfile
        fields = [
            # READ-ONLY NAME FIELDS
            "first_name",
            "last_name",
            "middle_name",

            # USER FIELD
            "phone",

            # Instructor fields
            "bio_uz",
            "bio_ru",
            "expertise",
            "qualifications_uz",
            "qualifications_ru",

            # Mentor secret fields
            "passport_number",
            "passport_issued_by",
            "passport_issue_date",
            "passport_expiry_date",
            "address",
            "card_number",
            "pinfl",
            "dob",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        instructor_data = user_data.pop("instructor_profile", {})

        # USER
        user = instance.user

        if "phone" in user_data:
            user.phone = user_data["phone"]
            user.save()

        instructor, _ = InstructorProfile.objects.get_or_create(mentor=instance)

        for field, value in instructor_data.items():
            setattr(instructor, field, value)

        instructor.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance


