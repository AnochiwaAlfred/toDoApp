from ninja.pagination import paginate, PaginationBase
from ninja import Schema
from typing import List, Any, Optional


class InternalPagination(PaginationBase):
    # only `limit` param, defaults to 5 per page
    class Input(Schema):
        limit: int

    class Output(Schema):
        items: List[Any] # `items` is a default attribute
        total: int
        per_page: int


    def paginate_queryset(self, queryset, pagination: Input, **params):
        limit = pagination.limit
        limit = limit if limit >  1 else 1
        limit = limit if limit <= queryset.count() else queryset.count()
        return {
            'items': queryset[0 : limit],
            'total': queryset.count(),
            'per_page': limit,
        }



class InternalPaginationOffset(PaginationBase):
    # only `limit` param, defaults to 5 per page
    class Input(Schema):
        start: int
        end:int
        

    class Output(Schema):
        items: List[Any] # `items` is a default attribute
        total: int
        per_page: int
        start:int=1
        end:int=2


    def paginate_queryset(self, queryset, pagination: Input, **params):
        start = pagination.start -1
        start = start if start >  0 else 0
        end = pagination.end - 1 if pagination.end > 1 else pagination.end
        end = end + 1 if end==start else end
        end = end if end <= queryset.count() else queryset.count()
        return {
            'items': queryset[start:end],
            'total': queryset.count(),
            'per_page': end-start,
            'start': pagination.start if pagination.start>0 else 1,
            'end': pagination. end,
        }




