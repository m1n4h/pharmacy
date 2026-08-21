from math import ceil

MAX_PAGE_LIMIT = 100

class Paginator:

    @staticmethod
    def paginate(query, page: int = 1, limit: int = 10):
        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
        if limit > MAX_PAGE_LIMIT:
            limit = MAX_PAGE_LIMIT

        total = query.count()
        pages = ceil(total / limit) if total > 0 else 1

        items = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": pages
            }
        }
