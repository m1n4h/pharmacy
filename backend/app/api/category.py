from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService
from app.utils.pagination import Paginator


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/create")
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    category = CategoryService.create(db, payload)
    if not category:
        return JSONResponse(status_code=400, content={"success": False, "message": "Category already exists", "error": "DUPLICATE"})

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="categories",
        details=f"Category: {category.name}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Category created successfully",
        "data": category
    }


@router.get("/")
def list_categories(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Category).order_by(Category.name)
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Categories fetched successfully",
        "data": {
            "items": paginated["items"],
            "pagination": paginated["pagination"]
        }
    }


@router.put("/{category_id}")
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    category = CategoryService.update(db, category_id, payload)

    if not category:
        return {"success": False, "message": "Category not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="categories",
        details=f"Updated category #{category_id} ({category.name})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Category updated successfully",
        "data": category
    }


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    category = CategoryService.delete(db, category_id)

    if not category:
        return {"success": False, "message": "Category not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="categories",
        details=f"Deleted category #{category_id} ({category.name})",
        user=current_user
    )

    return {"success": True, "message": "Category deleted successfully"}
