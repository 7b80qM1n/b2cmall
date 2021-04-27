from rest_framework.pagination import PageNumberPagination as DRFPageNumberPagination

class PageNumberPagination(DRFPageNumberPagination):
    page_query_param = 'page'  # 请求 页数 的关键字名 默认page
    page_size = 1  # 请求不指定的情况下 每页显示的条数
    page_size_query_param = 'size'  # 请求 每页显示的条数 的关键字名 默认None
    max_page_size = 10  # 请求可以指定的 每页显示数量 大小
