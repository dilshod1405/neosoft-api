from rest_framework import serializers
from django.db import models
from content.models import Category, Course, Lesson, Quiz, Question, Answer, Resource, Enrollment, UserProgress
from payment.models import Order
from django.utils import timezone


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text_uz", "text_ru", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text_uz", "text_ru", "order", "answers"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ["id", "title_uz", "title_ru", "passing_score", "questions"]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "title", "file", "file_type"]


class LessonSerializer(serializers.ModelSerializer):
    quizzes = QuizSerializer(many=True)
    resources = ResourceSerializer(many=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title_uz",
            "title_ru",
            "content_uz",
            "content_ru",
            "video_id",
            "order",
            "is_preview",
            "quizzes",
            "resources",
        ]


class StudentCourseSerializer(serializers.ModelSerializer):
    is_purchased = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    category = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title_uz",
            "title_ru",
            "slug",
            "description_uz",
            "description_ru",
            "final_price",
            "price",
            "discount_percent",
            "level",
            "level_display",
            "duration_hours",
            "thumbnail",
            "is_bestseller",
            "is_purchased",
            "lessons_count",
            "category",
            "instructor",
        ]

    def get_thumbnail(self, course):
        request = self.context.get("request")
        if course.thumbnail and request:
            return request.build_absolute_uri(course.thumbnail.url)
        return None

    def get_final_price(self, course):
        return course.discount_price or course.price

    def get_discount_percent(self, course):
        if course.discount_price and course.price:
            return int(100 - (course.discount_price / course.price) * 100)
        return 0

    def get_lessons_count(self, course):
        return course.lessons.count()

    def get_is_purchased(self, course):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return (
            Enrollment.objects.filter(student=user, course=course, is_active=True).exists()
            or Order.objects.filter(student=user, course=course, status="PAID").exists()
        )

    def get_category(self, course):
        return {
            "id": course.category.id,
            "name_uz": course.category.name_uz,
            "name_ru": course.category.name_ru,
            "slug": course.category.slug,
        }

    def get_instructor(self, course):
        instructor = course.instructor

        if not instructor or not instructor.mentor or not instructor.mentor.user:
            return None

        user = instructor.mentor.user

        return {
            "id": instructor.id,
            "full_name": user.full_name,  # yoki user.get_full_name
            "photo": user.photo.url if user.photo else None,
        }







class SubmitAnswerSerializer(serializers.Serializer):
    answer_id = serializers.IntegerField()

    def validate(self, data):
        question_id = self.context["view"].kwargs.get("question_id")

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Invalid question.")

        try:
            answer = Answer.objects.get(id=data["answer_id"], question=question)
        except Answer.DoesNotExist:
            raise serializers.ValidationError("This answer does not belong to the question.")

        data["question"] = question
        data["answer"] = answer
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        question = validated_data["question"]
        answer = validated_data["answer"]

        lesson = question.quiz.lesson
        course = lesson.course

        enrollment = user.enrollments.get(course=course)

        progress, _ = UserProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )

        total_questions = question.quiz.questions.count()
        correct_count = 1 if answer.is_correct else 0
        score = int((correct_count / total_questions) * 100)

        progress.quiz_score = score
        progress.completed_at = timezone.now()
        progress.save()

        return {
            "correct": answer.is_correct,
            "score": score,
            "question_id": question.id,
            "answer_id": answer.id
        }



class CategoryChildSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name_uz", "name_ru", "slug", "children"]

    def get_children(self, obj):
        qs = obj.subcategories.all()
        return CategoryChildSerializer(qs, many=True).data