from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.cache import cache_manager
from app.enums import RequestStatus, Roles
from app.models.request import Request
from app.models.service import Service
from app.models.user import User
from app.schemas import RequestCreate, RequestResponse, RequestStatusUpdate


def _to_response(request: Request) -> RequestResponse:
    return RequestResponse(
        id=request.id,
        user_id=request.user_id,
        service_id=request.service_id,
        status=request.status,
        created_at=request.created_at,
        updated_at=request.updated_at,
        user={
            "id": request.user.id,
            "name": request.user.name,
            "email": request.user.email,
        }
        if request.user
        else None,
        service={
            "id": request.service.id,
            "name": request.service.name,
            "price": request.service.price,
            "provider": {
                "id": request.service.provider.id,
                "name": request.service.provider.name,
                "email": request.service.provider.email,
            }
            if request.service.provider
            else None,
        }
        if request.service
        else None,
    )


def get_user_role(db: Session, user_id: int) -> int:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.role_id


def create_request(db: Session, user_id: int, payload: RequestCreate) -> RequestResponse:
    service = db.query(Service).filter(Service.id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if not service.status:
        raise HTTPException(status_code=400, detail="Service is not active")

    if service.provider_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot request your own service")

    existing_request = (
        db.query(Request)
        .filter(
            Request.user_id == user_id,
            Request.service_id == payload.service_id,
            Request.status == RequestStatus.pending,
        )
        .first()
    )
    if existing_request:
        raise HTTPException(
            status_code=400, detail="You already have a pending request for this service"
        )

    new_request = Request(
        user_id=user_id,
        service_id=payload.service_id,
        status=RequestStatus.pending,
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    cache_manager.invalidate_tags([
        f"requests:user_{user_id}",
        f"requests:provider_{service.provider_id}",
    ])

    return _to_response(new_request)


def list_provider_requests(db: Session, provider_id: int) -> list[RequestResponse]:
    cache_key = f"requests:provider_{provider_id}"
    cached = cache_manager.get(cache_key)
    if cached is not None:
        return [RequestResponse(**item) for item in cached]

    requests = (
        db.query(Request)
        .join(Service, Request.service_id == Service.id)
        .filter(Service.provider_id == provider_id)
        .order_by(Request.created_at.desc())
        .all()
    )
    result = [_to_response(req) for req in requests]

    cache_manager.set(
        cache_key,
        [r.model_dump() for r in result],
        tags=[f"requests:provider_{provider_id}"],
    )
    return result


def list_user_requests(db: Session, user_id: int) -> list[RequestResponse]:
    cache_key = f"requests:user_{user_id}"
    cached = cache_manager.get(cache_key)
    if cached is not None:
        return [RequestResponse(**item) for item in cached]

    requests = (
        db.query(Request)
        .filter(Request.user_id == user_id)
        .order_by(Request.created_at.desc())
        .all()
    )
    result = [_to_response(req) for req in requests]

    cache_manager.set(
        cache_key,
        [r.model_dump() for r in result],
        tags=[f"requests:user_{user_id}"],
    )
    return result


def get_request(db: Session, user_id: int, request_id: int) -> RequestResponse:
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.user_id != user_id and request.service.provider_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this request")

    return _to_response(request)


def update_request_status(
    db: Session, user_id: int, request_id: int, payload: RequestStatusUpdate
) -> RequestResponse:
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.service.provider_id != user_id:
        raise HTTPException(
            status_code=403, detail="Only the service provider can update request status"
        )

    if request.status != RequestStatus.pending:
        raise HTTPException(
            status_code=400, detail="Can only update requests that are pending"
        )

    request.status = payload.status
    db.commit()
    db.refresh(request)

    cache_manager.invalidate_tags([
        f"requests:user_{request.user_id}",
        f"requests:provider_{user_id}",
    ])

    return _to_response(request)


def delete_request(db: Session, user_id: int, request_id: int) -> None:
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only cancel your own requests")

    if request.status != RequestStatus.pending:
        raise HTTPException(status_code=400, detail="Can only cancel pending requests")

    provider_id = request.service.provider_id
    db.delete(request)
    db.commit()

    cache_manager.invalidate_tags([
        f"requests:user_{user_id}",
        f"requests:provider_{provider_id}",
    ])
