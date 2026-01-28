from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.service import Service
from app.models.user import User
from app.schemas import ServiceCreate, ServiceResponse, ServiceUpdate
from app.api.auth import get_current_user
from app.core.cache import cache_manager
from app.core.jwt import verify_token

router = APIRouter(prefix="/services", tags=["services"])
security = HTTPBearer()


def get_optional_user(credentials: HTTPBearer = Depends(security)) -> int | None:
    try:
        return verify_token(credentials.credentials)
    except:
        return None


@router.get("", response_model=list[ServiceResponse])
def get_all_services(
    db: Session = Depends(get_db),
    credentials: HTTPBearer = Depends(security),
):
    user_id = None
    user_role = None
    try:
        user_id = verify_token(credentials.credentials)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user_role = user.role_id
    except:
        pass
    if user_role == 2:
        cache_key = f"services:provider_{user_id}"
        cached_services = cache_manager.get(cache_key)
        if cached_services is not None:
            return JSONResponse(
                content=[item.model_dump() if isinstance(item, ServiceResponse) else item for item in cached_services],
                headers={"X-Cache": "HIT", "X-Cache-Key": cache_key}
            )
        
        services = db.query(Service).filter(Service.provider_id == user_id).all()
        result = [
            ServiceResponse(
                id=service.id,
                name=service.name,
                description=service.description,
                price=service.price,
                status=service.status,
                provider={"id": service.provider.id, "name": service.provider.name, "email": service.provider.email} if service.provider else None,
            )
            for service in services
        ]
        
        cache_manager.set(cache_key, result, tags=[f"provider_{user_id}"])
        return JSONResponse(
            content=[item.model_dump() for item in result],
            headers={"X-Cache": "MISS", "X-Cache-Key": cache_key}
        )
    
    # For regular users, return active services only
    cached_services = cache_manager.get("services:public")
    if cached_services is not None:
        return JSONResponse(
            content=[item.model_dump() if isinstance(item, ServiceResponse) else item for item in cached_services],
            headers={"X-Cache": "HIT", "X-Cache-Key": "services:public"}
        )
    
    services = db.query(Service).filter(Service.status == True).all()
    result = [
        ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            price=service.price,
            status=service.status,
            provider={"id": service.provider.id, "name": service.provider.name, "email": service.provider.email} if service.provider else None,
        )
        for service in services
    ]
    
    cache_manager.set("services:public", result, tags=["public"])
    return JSONResponse(
        content=[item.model_dump() for item in result],
        headers={"X-Cache": "MISS", "X-Cache-Key": "services:public"}
    )
@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return ServiceResponse(
        id=service.id,
        name=service.name,
        description=service.description,
        price=service.price,
        status=service.status,
        provider={"id": service.provider.id, "name": service.provider.name, "email": service.provider.email} if service.provider else None,
    )


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service: ServiceCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.role_id != 2:
            raise HTTPException(
                status_code=403,
                detail="Only providers can create services"
            )

        new_service = Service(
            name=service.name,
            description=service.description,
            price=service.price,
            status=service.status,
            provider_id=user_id
        )
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
   
        cache_manager.invalidate_tags(["public", f"provider_{user_id}"])

        return ServiceResponse(
            id=new_service.id,
            name=new_service.name,
            description=new_service.description,
            price=new_service.price,
            status=new_service.status,
            provider={"id": new_service.provider.id, "name": new_service.provider.name, "email": new_service.provider.email} if new_service.provider else None,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating service: {str(e)}")


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        if service.provider.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own services"
            )

        data = service_update.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(service, field, value)

        db.commit()
        db.refresh(service)
 
        cache_manager.invalidate_tags(["public", f"provider_{user_id}"])

        return ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            price=service.price,
            status=service.status,
            provider={"id": service.provider.id, "name": service.provider.name, "email": service.provider.email} if service.provider else None,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating service: {str(e)}")


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")


        if service.provider.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only delete your own services"
            )

        db.delete(service)
        db.commit()
       
        cache_manager.invalidate_tags(["public", f"provider_{user_id}"])

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting service: {str(e)}")
