from django import template

register = template.Library()


def paginator(context, adjacent_pages=2):
    page_obj = context['page_obj']
    current_page = page_obj.number
    number_of_pages = context['paginator'].num_pages

    startPage = max(current_page - adjacent_pages, 1)
    endPage = current_page + adjacent_pages + 1

    if endPage > number_of_pages:
        endPage = number_of_pages + 1

    page_numbers = [n for n in range(startPage, endPage) if 0 < n <= number_of_pages]

    return {
        'page': current_page,
        'pages': number_of_pages,
        'page_numbers': page_numbers,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous': page_obj.previous_page_number,
        'next': page_obj.next_page_number,
        'show_first': 1 not in page_numbers,
        'show_last': number_of_pages not in page_numbers,
    }


register.inclusion_tag('app/pagination.html', takes_context=True)(paginator)