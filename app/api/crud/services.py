from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.cache import cache_manager
from app.enums import Roles
from app.models.service import Service
from app.models.user import User
from app.schemas import ServiceCreate, ServiceResponse, ServiceUpdate


def _to_response(service: Service) -> ServiceResponse:
    return ServiceResponse(
        id=service.id,
        name=service.name,
        description=service.description,
        price=service.price,
        status=service.status,
        provider={
            "id": service.provider.id,
            "name": service.provider.name,
            "email": service.provider.email,
        }
        if service.provider
        else None,
    )


def get_user_role(db: Session, user_id: int) -> int:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.role_id


def list_provider_services(db: Session, provider_id: int) -> list[ServiceResponse]:
    cache_key = f"services:provider_{provider_id}"
    cached = cache_manager.get(cache_key)
    if cached is not None:
        # cached may be dicts
        return [item if isinstance(item, ServiceResponse) else ServiceResponse(**item) for item in cached]

    services = db.query(Service).filter(Service.provider_id == provider_id).all()
    result = [_to_response(s) for s in services]

    cache_manager.set(
        cache_key,
        [r.model_dump() for r in result],
        tags=[f"provider_{provider_id}"],
    )
    return result


def list_public_services(db: Session) -> list[ServiceResponse]:
    cache_key = "services:public"
    cached = cache_manager.get(cache_key)
    if cached is not None:
        return [item if isinstance(item, ServiceResponse) else ServiceResponse(**item) for item in cached]

    services = db.query(Service).filter(Service.status == True).all()
    result = [_to_response(s) for s in services]

    cache_manager.set(
        cache_key,
        [r.model_dump() for r in result],
        tags=["public"],
    )
    return result


def get_service(db: Session, service_id: int) -> ServiceResponse:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return _to_response(service)


def create_service(db: Session, user_id: int, payload: ServiceCreate) -> ServiceResponse:
    role_id = get_user_role(db=db, user_id=user_id)
    if role_id != Roles.PROVIDER:
        raise HTTPException(status_code=403, detail="Only providers can create services")

    new_service = Service(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        status=payload.status,
        provider_id=user_id,
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    cache_manager.invalidate_tags(["public", f"provider_{user_id}"])
    return _to_response(new_service)


def update_service(db: Session, user_id: int, service_id: int, payload: ServiceUpdate) -> ServiceResponse:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service.provider_id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own services")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)

    cache_manager.invalidate_tags(["public", f"provider_{user_id}"])
    return _to_response(service)


def delete_service(db: Session, user_id: int, service_id: int) -> None:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service.provider_id != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own services")

    db.delete(service)
    db.commit()

    cache_manager.invalidate_tags(["public", f"provider_{user_id}"])
