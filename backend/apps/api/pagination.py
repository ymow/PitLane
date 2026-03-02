from rest_framework.pagination import CursorPagination


class ArticleCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-published_at'
