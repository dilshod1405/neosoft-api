from rest_framework.permissions import BasePermission
from content.models import Lesson, Enrollment


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