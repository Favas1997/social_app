from rest_framework import pagination
from rest_framework.response import Response



class CustomPagination(pagination.PageNumberPagination):
    def __init__(self, page_size=None, *args, **kwargs):
        self.page_size = int(page_size) 

    def get_paginated_response(self, data):
        try:
            total_items = int(self.page.paginator.count)
            page_size = int(self.get_page_size(self.request))
            total_pages = (total_items + page_size - 1) // page_size  
            next = self.get_next_link()
            previous = self.get_previous_link()
        except:
            total_items,page_size,total_pages,next,previous = '', '', '', '', ''
        return Response({'data':{
            'links': {
                'next':next,
                'previous': previous
             },
            'count': total_items,
            'total_pages': total_pages,  
            'results': data
        }})