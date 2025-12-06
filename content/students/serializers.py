from rest_framework import serializers
from django.db import models
from content.models import Course, Lesson, Quiz, Question, Answer, Resource, Enrollment, UserProgress
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
    lessons = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title_uz",
            "title_ru",
            "slug",
            "description_uz",
            "description_ru",
            "price",
            "discount_price",
            "final_price",
            "level",
            "duration_hours",
            "thumbnail",
            "is_bestseller",
            "is_published",
            "is_purchased",
            "progress",
            "lessons",
        ]

    # -----------------------------------
    # PURCHASE CHECK
    # -----------------------------------
    def get_is_purchased(self, course):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False

        if Enrollment.objects.filter(student=user, course=course, is_active=True).exists():
            return True

        if Order.objects.filter(student=user, course=course, status="PAID").exists():
            return True

        return False

    # -----------------------------------
    # FINAL PRICE
    # -----------------------------------
    def get_final_price(self, course):
        return course.discount_price or course.price

    # -----------------------------------
    # LESSONS (dynamic)
    # -----------------------------------
    def get_lessons(self, course):
        user = self.context["request"].user
        is_purchased = self.get_is_purchased(course)

        if is_purchased:
            lessons = course.lessons.prefetch_related(
                "quizzes__questions__answers",
                "resources"
            )
            return LessonSerializer(lessons, many=True).data
        else:
            previews = course.lessons.filter(is_preview=True)
            return LessonSerializer(previews, many=True).data

    # -----------------------------------
    # PROGRESS (full statistics)
    # -----------------------------------
    def get_progress(self, course):
        user = self.context["request"].user
        if not user.is_authenticated:
            return None

        enrollment = Enrollment.objects.filter(student=user, course=course, is_active=True).first()
        if not enrollment:
            return None

        total_lessons = course.lessons.count()

        completed_lessons = enrollment.progress.filter(completed_at__isnull=False).count()

        total_weight = sum(l.weight for l in course.lessons.all())

        completed_weight = sum(
            up.lesson.weight
            for up in enrollment.progress.filter(completed_at__isnull=False)
        )

        video_progress = (completed_weight / total_weight) * 100 if total_weight else 0

        quiz_scores = enrollment.progress.exclude(quiz_score__isnull=True)
        quiz_avg = quiz_scores.aggregate(avg=models.Avg("quiz_score"))["avg"] or 0
        quiz_progress = (quiz_avg / 100) * 30

        total_questions = Question.objects.filter(quiz__lesson__course=course).count()
        correct_answers = Answer.objects.filter(
            is_correct=True,
            question__quiz__lesson__course=course
        ).count()

        return {
            "completion_percentage": enrollment.completion_percentage,
            "video_progress": int(video_progress),
            "quiz_progress": int(quiz_progress),
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "total_quizzes": Quiz.objects.filter(lesson__course=course).count(),
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "quiz_avg_score": int(quiz_avg),
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