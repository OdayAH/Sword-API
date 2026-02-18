from sqlalchemy.orm import Session

from app.api.crud import services as services_crud
from app.schemas import ServiceCreate, ServiceUpdate, ServiceResponse
from app.enums import Roles


def list_services(db: Session, user_id: int) -> list[ServiceResponse]:
    role_id = services_crud.get_user_role(db=db, user_id=user_id)

    if role_id == Roles.PROVIDER:
        return services_crud.list_provider_services(db=db, provider_id=user_id)

    return services_crud.list_public_services(db=db)


def get_service(db: Session, service_id: int) -> ServiceResponse:
    return services_crud.get_service(db=db, service_id=service_id)


def create_service(db: Session, user_id: int, payload: ServiceCreate) -> ServiceResponse:
    return services_crud.create_service(db=db, user_id=user_id, payload=payload)


def update_service(
    db: Session,
    user_id: int,
    service_id: int,
    payload: ServiceUpdate,
) -> ServiceResponse:
    return services_crud.update_service(
        db=db,
        user_id=user_id,
        service_id=service_id,
        payload=payload,
    )


def delete_service(db: Session, user_id: int, service_id: int) -> None:
    services_crud.delete_service(db=db, user_id=user_id, service_id=service_id)
