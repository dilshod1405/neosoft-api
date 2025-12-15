# content/filters.py
import django_filters
from django.db import models
from django.db.models import F, Case, When, IntegerField
from django.contrib.postgres.search import SearchVector, SearchQuery

from content.models import Course, Category


class CourseFilter(django_filters.FilterSet):
    # ==================================================
    # BASIC FILTERS
    # ==================================================
    category = django_filters.CharFilter(method="filter_by_category_slug")
    level = django_filters.ChoiceFilter(choices=Course.LEVEL_CHOICES)
    instructor = django_filters.CharFilter(method="filter_instructor")

    # ==================================================
    # FINAL PRICE FILTERS (MUHIM QISM)
    # ==================================================
    min_price = django_filters.NumberFilter(method="filter_min_final_price")
    max_price = django_filters.NumberFilter(method="filter_max_final_price")

    # ==================================================
    # DISCOUNT
    # ==================================================
    has_discount = django_filters.BooleanFilter(method="filter_has_discount")

    # ==================================================
    # RATING
    # ==================================================
    min_rating = django_filters.NumberFilter(method="filter_min_rating")
    max_rating = django_filters.NumberFilter(method="filter_max_rating")

    # ==================================================
    # DURATION
    # ==================================================
    min_duration = django_filters.NumberFilter(
        field_name="duration_hours", lookup_expr="gte"
    )
    max_duration = django_filters.NumberFilter(
        field_name="duration_hours", lookup_expr="lte"
    )

    # ==================================================
    # FLAGS
    # ==================================================
    is_bestseller = django_filters.BooleanFilter(field_name="is_bestseller")
    is_published = django_filters.BooleanFilter(field_name="is_published")

    # ==================================================
    # SEARCH (PostgreSQL FullText)
    # ==================================================
    search = django_filters.CharFilter(method="filter_search")

    # ==================================================
    # ORDERING (FINAL PRICE + RATING)
    # ==================================================
    ordering = django_filters.OrderingFilter(
        fields=(
            ("final_price_calc", "price"),
            ("created_at", "created_at"),
            ("title_uz", "title"),
            ("avg_rating", "rating"),
        )
    )

    class Meta:
        model = Course
        fields = [
            "category",
            "level",
            "instructor",
            "min_price",
            "max_price",
            "has_discount",
            "min_rating",
            "max_rating",
            "min_duration",
            "max_duration",
            "is_bestseller",
            "is_published",
        ]

    # ==================================================
    # INTERNAL: FINAL PRICE ANNOTATION
    # ==================================================
    def _with_final_price(self, queryset):
        return queryset.annotate(
            final_price_calc=Case(
                When(
                    discount_price__isnull=False,
                    discount_price__gt=0,
                    then=F("discount_price"),
                ),
                default=F("price"),
                output_field=IntegerField(),
            )
        )

    # ==================================================
    # FINAL PRICE FILTERS
    # ==================================================
    def filter_min_final_price(self, queryset, name, value):
        queryset = self._with_final_price(queryset)
        return queryset.filter(final_price_calc__gte=value)

    def filter_max_final_price(self, queryset, name, value):
        queryset = self._with_final_price(queryset)
        return queryset.filter(final_price_calc__lte=value)

    # ==================================================
    # CATEGORY FILTER
    # ==================================================
    def filter_by_category_slug(self, queryset, name, value):
        try:
            category = Category.objects.get(slug__iexact=value)
        except Category.DoesNotExist:
            return queryset.none()

        if category.parent is None:
            sub_ids = list(
                category.subcategories.values_list("id", flat=True)
            )
            sub_ids.append(category.id)
            return queryset.filter(category_id__in=sub_ids)

        return queryset.filter(category=category)

    # ==================================================
    # DISCOUNT FILTER
    # ==================================================
    def filter_has_discount(self, queryset, name, value: bool):
        if value:
            return queryset.filter(
                models.Q(discount_price__isnull=False, discount_price__gt=0)
                | models.Q(discounts__isnull=False)
            ).distinct()

        return queryset.filter(
            discount_price__isnull=True, discounts__isnull=True
        )

    # ==================================================
    # RATING FILTERS
    # ==================================================
    def _with_rating(self, queryset):
        return queryset.annotate(avg_rating=models.Avg("ratings__rating"))

    def filter_min_rating(self, queryset, name, value):
        queryset = self._with_rating(queryset)
        return queryset.filter(avg_rating__gte=value)

    def filter_max_rating(self, queryset, name, value):
        queryset = self._with_rating(queryset)
        return queryset.filter(avg_rating__lte=value)

    # ==================================================
    # INSTRUCTOR FILTER
    # ==================================================
    def filter_instructor(self, queryset, name, value):
        return queryset.filter(
            models.Q(
                instructor__mentor__user__first_name__icontains=value
            )
            | models.Q(
                instructor__mentor__user__last_name__icontains=value
            )
        )

    # ==================================================
    # SEARCH FILTER
    # ==================================================
    def filter_search(self, queryset, name, value):
        vector = (
            SearchVector("title_uz")
            + SearchVector("title_ru")
            + SearchVector("description_uz")
            + SearchVector("description_ru")
            + SearchVector("instructor__mentor__user__first_name")
            + SearchVector("instructor__mentor__user__last_name")
        )
        query = SearchQuery(value)
        return queryset.annotate(search=vector).filter(search=query)
