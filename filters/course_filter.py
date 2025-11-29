# content/filters.py
import django_filters
from django.db import models
from content.models import Course, Category
from django.contrib.postgres.search import SearchVector


class CourseFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method='filter_by_category_slug')
    level = django_filters.ChoiceFilter(choices=Course.LEVEL_CHOICES)
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    instructor = django_filters.CharFilter(field_name='instructor__user__full_name', lookup_expr='icontains')
    min_rating = django_filters.NumberFilter(method='filter_min_rating')
    max_rating = django_filters.NumberFilter(method='filter_max_rating')

    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Course
        fields = [
            'category', 'level', 'min_price', 'max_price',
            'has_discount', 'instructor', 'min_rating', 'max_rating',
            'min_duration', 'max_duration', 'is_bestseller', 'is_published'
        ]


    def filter_by_category_slug(self, queryset, name, value):
        try:
            category = Category.objects.get(slug__iexact=value)
        except Category.DoesNotExist:
            return queryset.none()

        if category.parent is None:
            subcategory_ids = list(category.subcategories.values_list('id', flat=True))
            subcategory_ids.append(category.id)
            return queryset.filter(category_id__in=subcategory_ids)

        return queryset.filter(category=category)



    def filter_has_discount(self, queryset, name, value: bool):
        if value:
            return queryset.filter(
                models.Q(discount_price__isnull=False, discount_price__gt=0) |
                models.Q(discounts__isnull=False)
            ).distinct()
        else:
            return queryset.filter(discount_price__isnull=True, discounts__isnull=True)
        



    def filter_by_rating(self, queryset):
        queryset = queryset.annotate(avg_rating=models.Avg('ratings__rating'))
        return super().filter_queryset(queryset)




    def filter_search(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector('title_uz', 'title_ru', 'description_uz', 'description_ru', 'instructor__user__full_name')
        ).filter(search=value)


    min_duration = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='lte')
    is_bestseller = django_filters.BooleanFilter(field_name='is_bestseller')
    is_published = django_filters.BooleanFilter(field_name='is_published')

