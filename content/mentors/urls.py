from django.urls import path
from .views import (
    MentorCourseListCreateView,
    MentorCourseDetailView,

    MentorLessonCreateView,
    MentorLessonDetailView,
    MentorInitiateUploadView,

    MentorQuizCreateView,
    MentorQuizDetailView,

    MentorQuestionCreateView,
    MentorQuestionDetailView,

    MentorAnswerCreateView,
    MentorAnswerDetailView,

    MentorResourceCreateView,
    MentorResourceDetailView,
)

urlpatterns = [

    # ===============================
    #          COURSE CRUD
    # ===============================
    path(
        "courses/",
        MentorCourseListCreateView.as_view(),
        name="mentor-course-list-create"
    ),

    path(
        "courses/<int:pk>/",
        MentorCourseDetailView.as_view(),
        name="mentor-course-detail"
    ),

    # ===============================
    #        LESSON CRUD
    # ===============================
    path(
        "courses/<int:course_id>/lessons/create/",
        MentorLessonCreateView.as_view(),
        name="mentor-lesson-create"
    ),

    path(
        "lessons/<int:pk>/",
        MentorLessonDetailView.as_view(),
        name="mentor-lesson-detail"
    ),

    # ===============================
    #     VIDEO UPLOAD → VdoCipher
    # ===============================
    path(
        "lessons/<int:lesson_id>/init-upload/",
        MentorInitiateUploadView.as_view(),
        name="mentor-lesson-init-upload"
    ),

    # ===============================
    #            QUIZ CREATE
    # ===============================
    path(
        "lessons/<int:lesson_id>/quizzes/create/",
        MentorQuizCreateView.as_view(),
        name="mentor-quiz-create"
    ),


    # ===============================
    #       QUIZ PUT/DELETE/GET
    # ===============================
    path(
    "quizzes/<int:pk>/",
    MentorQuizDetailView.as_view(),
    name="mentor-quiz-detail"
    ),


    # ===============================
    #         QUESTION CREATE
    # ===============================
    path(
        "quizzes/<int:quiz_id>/questions/create/",
        MentorQuestionCreateView.as_view(),
        name="mentor-question-create"
    ),


    # ===============================
    #     QUESTION PUT/DELETE/GET
    # ===============================
    path(
    "questions/<int:pk>/",
    MentorQuestionDetailView.as_view(),
    name="mentor-question-detail"
    )
    ,

    # ===============================
    #          ANSWER CREATE
    # ===============================
    path(
        "questions/<int:question_id>/answers/create/",
        MentorAnswerCreateView.as_view(),
        name="mentor-answer-create"
    ),


    # ===============================
    #      ANSWER PUT/DELETE/GET
    # ===============================
    path(
    "answers/<int:pk>/",
    MentorAnswerDetailView.as_view(),
    name="mentor-answer-detail"
    ),


    # ===============================
    #      RESOURCE CRUD (file)
    # ===============================
    path(
        "lessons/<int:lesson_id>/resources/create/",
        MentorResourceCreateView.as_view(),
        name="mentor-resource-create"
    ),

    path(
        "resources/<int:pk>/",
        MentorResourceDetailView.as_view(),
        name="mentor-resource-detail"
    ),
]
