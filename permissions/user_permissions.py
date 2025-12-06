from rest_framework.permissions import BasePermission
from content.models import Course, Lesson, Quiz, Question, Enrollment, Resource, Answer


# ==================================================================
#                CHECK USER THAT IS STUDENT OR MENTOR
# ==================================================================

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_mentor



class IsMentor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "is_mentor", False)





# ===============================================================================
#         CHECK IF USER IS ENROLLED IN THE COURSE BEFORE ACCESSING VIEW
# ===============================================================================

class IsEnrolledStudent(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        lesson_id = view.kwargs.get("lesson_id")
        if not lesson_id:
            return False

        try:
            lesson = Lesson.objects.get(id=lesson_id)
            return Enrollment.objects.filter(
                student=user,
                course=lesson.course,
                is_active=True
            ).exists()
        except Lesson.DoesNotExist:
            return False
        




class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        owner_fields = ["user", "owner", "mentor", "student", "created_by"]

        for field in owner_fields:
            if hasattr(obj, field):
                return getattr(obj, field) == request.user
        
        return False




class IsCourseAccessible(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        course_id = view.kwargs.get("course_id")
        if course_id:
            return self._is_enrolled(user, course_id)

        lesson_id = view.kwargs.get("lesson_id")
        if lesson_id:
            try:
                course_id = Lesson.objects.values_list("course_id", flat=True).get(id=lesson_id)
                return self._is_enrolled(user, course_id)
            except Lesson.DoesNotExist:
                return False

        quiz_id = view.kwargs.get("quiz_id")
        if quiz_id:
            try:
                lesson = Quiz.objects.select_related("lesson__course").get(id=quiz_id).lesson
                return self._is_enrolled(user, lesson.course_id)
            except Quiz.DoesNotExist:
                return False

        question_id = view.kwargs.get("question_id")
        if question_id:
            try:
                lesson = Question.objects.select_related(
                    "quiz__lesson__course"
                ).get(id=question_id).quiz.lesson
                return self._is_enrolled(user, lesson.course_id)
            except Question.DoesNotExist:
                return False

        return False

    def _is_enrolled(self, user, course_id):
        return Enrollment.objects.filter(
            student=user,
            course_id=course_id,
            is_active=True
        ).exists()





class MentorOwnsObject(BasePermission):

    def has_object_permission(self, request, view, obj):
        user_mentor = getattr(request.user, "mentor_profile", None)
        if user_mentor is None:
            return False

        if isinstance(obj, Course):
            return obj.instructor.mentor == user_mentor

        if isinstance(obj, Lesson):
            return obj.course.instructor.mentor == user_mentor

        if isinstance(obj, Quiz):
            return obj.lesson.course.instructor.mentor == user_mentor

        if isinstance(obj, Question):
            return obj.quiz.lesson.course.instructor.mentor == user_mentor

        if isinstance(obj, Answer):
            return obj.question.quiz.lesson.course.instructor.mentor == user_mentor

        if isinstance(obj, Resource):
            return obj.lesson.course.instructor.mentor == user_mentor

        return False
