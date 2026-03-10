from fastapi import APIRouter, BackgroundTasks, Depends, status, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.api.controllers import requests_controller
from app.schemas import RequestCreate, RequestResponse, RequestStatusUpdate
from app.core.security import get_current_user
from app.core.rate_limit import (
    limiter,
    REQUEST_CREATE_LIMIT,
    REQUEST_LIST_LIMIT,
    REQUEST_UPDATE_LIMIT,
)

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(REQUEST_CREATE_LIMIT)
def create_request(
    request: Request,
    payload: RequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new service request. Status defaults to pending."""
    return requests_controller.create_request(
        db=db, user_id=current_user.id, payload=payload, background_tasks=background_tasks
    )


@router.get("", response_model=list[RequestResponse])
@limiter.limit(REQUEST_LIST_LIMIT)
def get_requests(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get requests based on user role:
    - Providers: see requests for their services
    - Users: see their own requests
    """
    return requests_controller.list_requests(db=db, user_id=current_user.id)


@router.get("/{request_id}", response_model=RequestResponse)
@limiter.limit(REQUEST_LIST_LIMIT)
def get_request(
    request: Request,
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single request by ID."""
    return requests_controller.get_request(db=db, user_id=current_user.id, request_id=request_id)


@router.put("/{request_id}/status", response_model=RequestResponse)
@limiter.limit(REQUEST_UPDATE_LIMIT)
def update_request_status(
    request: Request,
    request_id: int,
    payload: RequestStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update request status (approve/decline).
    Only the service provider can update the status.
    """
    return requests_controller.update_request_status(
        db=db, user_id=current_user.id, request_id=request_id, payload=payload, background_tasks=background_tasks
    )


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(REQUEST_UPDATE_LIMIT)
def cancel_request(
    request: Request,
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a pending request. Only the requester can cancel their own request."""
    requests_controller.delete_request(db=db, user_id=current_user.id, request_id=request_id)
