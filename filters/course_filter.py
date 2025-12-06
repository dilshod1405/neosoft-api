# content/filters.py
import django_filters
from django.db import models
from django.contrib.postgres.search import SearchVector, SearchQuery
from content.models import Course, Category


class CourseFilter(django_filters.FilterSet):
    # BASIC FILTERS
    category = django_filters.CharFilter(method='filter_by_category_slug')
    level = django_filters.ChoiceFilter(choices=Course.LEVEL_CHOICES)
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    instructor = django_filters.CharFilter(method='filter_instructor')

    # RATING FILTERS
    min_rating = django_filters.NumberFilter(method='filter_min_rating')
    max_rating = django_filters.NumberFilter(method='filter_max_rating')

    # SEARCH
    search = django_filters.CharFilter(method='filter_search')

    # DURATION
    min_duration = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='lte')

    # FLAGS
    is_bestseller = django_filters.BooleanFilter(field_name='is_bestseller')
    is_published = django_filters.BooleanFilter(field_name='is_published')

    # ORDERING
    ordering = django_filters.OrderingFilter(
        fields=(
            ('price', 'price'),
            ('created_at', 'created_at'),
            ('title_uz', 'title'),
            ('avg_rating', 'rating'),
        )
    )

    class Meta:
        model = Course
        fields = [
            'category',
            'level',
            'min_price', 'max_price',
            'has_discount',
            'instructor',
            'min_rating', 'max_rating',
            'min_duration', 'max_duration',
            'is_bestseller',
            'is_published',
        ]

    # ================================================
    # CATEGORY FILTER
    # ================================================
    def filter_by_category_slug(self, queryset, name, value):
        try:
            category = Category.objects.get(slug__iexact=value)
        except Category.DoesNotExist:
            return queryset.none()

        if category.parent is None:
            sub_ids = list(category.subcategories.values_list('id', flat=True))
            sub_ids.append(category.id)
            return queryset.filter(category_id__in=sub_ids)

        return queryset.filter(category=category)

    # ================================================
    # DISCOUNT FILTER
    # ================================================
    def filter_has_discount(self, queryset, name, value: bool):
        if value:
            return queryset.filter(
                models.Q(discount_price__isnull=False, discount_price__gt=0) |
                models.Q(discounts__isnull=False)
            ).distinct()

        return queryset.filter(discount_price__isnull=True, discounts__isnull=True)

    # ================================================
    # RATING FILTERS
    # ================================================
    def _apply_rating_annotate(self, queryset):
        return queryset.annotate(avg_rating=models.Avg('ratings__rating'))

    def filter_min_rating(self, queryset, name, value):
        queryset = self._apply_rating_annotate(queryset)
        return queryset.filter(avg_rating__gte=value)

    def filter_max_rating(self, queryset, name, value):
        queryset = self._apply_rating_annotate(queryset)
        return queryset.filter(avg_rating__lte=value)
    

    # ================================================
    # FILTER BY MENTOR
    # ================================================

    def filter_instructor(self, queryset, name, value):
        return queryset.filter(
            models.Q(instructor__mentor__user__first_name__icontains=value) |
            models.Q(instructor__mentor__user__last_name__icontains=value)
        )


    # ================================================
    # SEARCH FILTER (PostgreSQL FULLTEXT)
    # ================================================
    def filter_search(self, queryset, name, value):
        vector = (
            SearchVector('title_uz') +
            SearchVector('title_ru') +
            SearchVector('description_uz') +
            SearchVector('description_ru') +
            SearchVector('instructor__mentor__user__first_name') +
            SearchVector('instructor__mentor__user__last_name')
        )
        query = SearchQuery(value)
        return queryset.annotate(search=vector).filter(search=query)

