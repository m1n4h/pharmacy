from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchUpdate
from app.services.branch_service import BranchService
from app.utils.pagination import Paginator


router = APIRouter(prefix="/branches", tags=["Branches"])


@router.post("/create")
def create_branch(
    payload: BranchCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    branch = BranchService.create(db, payload)
    if not branch:
        return {"success": False, "message": "Branch with this code already exists", "error": "DUPLICATE"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="branches",
        details=f"Branch: {branch.name}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Branch created successfully",
        "data": branch
    }


@router.get("/")
def list_branches(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Branch)

    if search:
        s = f"%{search}%"
        query = query.filter(Branch.name.ilike(s) | Branch.code.ilike(s))

    query = query.order_by(Branch.name)
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Branches fetched successfully",
        "data": {
            "items": paginated["items"],
            "pagination": paginated["pagination"]
        }
    }


@router.get("/{branch_id}")
def get_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    branch = BranchService.get_by_id(db, branch_id)

    if not branch:
        return {"success": False, "message": "Branch not found", "error": "NOT_FOUND"}

    return {
        "success": True,
        "message": "Branch fetched successfully",
        "data": branch
    }


@router.put("/{branch_id}")
def update_branch(
    branch_id: int,
    payload: BranchUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    branch = BranchService.update(db, branch_id, payload)

    if not branch:
        return {"success": False, "message": "Branch not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="branches",
        details=f"Updated branch #{branch_id} ({branch.name})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Branch updated successfully",
        "data": branch
    }


@router.delete("/{branch_id}")
def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    branch = BranchService.delete(db, branch_id)

    if not branch:
        return {"success": False, "message": "Branch not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="branches",
        details=f"Deleted branch #{branch_id} ({branch.name})",
        user=current_user
    )

    return {"success": True, "message": "Branch deleted successfully"}
