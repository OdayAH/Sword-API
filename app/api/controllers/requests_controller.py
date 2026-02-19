from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.api.crud import requests as requests_crud
from app.schemas import RequestCreate, RequestResponse, RequestStatusUpdate
from app.enums import Roles
from app.core.email import send_email


def list_requests(db: Session, user_id: int) -> list[RequestResponse]:
    role_id = requests_crud.get_user_role(db=db, user_id=user_id)

    if role_id == Roles.PROVIDER:
        return requests_crud.list_provider_requests(db=db, provider_id=user_id)

    return requests_crud.list_user_requests(db=db, user_id=user_id)


def get_request(db: Session, user_id: int, request_id: int) -> RequestResponse:
    return requests_crud.get_request(db=db, user_id=user_id, request_id=request_id)


def create_request(
    db: Session,
    user_id: int,
    payload: RequestCreate,
    background_tasks: BackgroundTasks,
) -> RequestResponse:
    result = requests_crud.create_request(db=db, user_id=user_id, payload=payload)

    if result.user and result.service and result.service.get("provider"):
        provider = result.service["provider"]
        requester = result.user
        service_name = result.service["name"]

        # Notify the provider
        background_tasks.add_task(
            send_email,
            to=provider["email"],
            subject=f"New request for your service: {service_name}",
            body=(
                f"Hi {provider['name']},\n\n"
                f"{requester['name']} ({requester['email']}) has requested your service '{service_name}'.\n\n"
                f"Log in to review and respond to the request."
            ),
        )

        # Confirm to the requester
        background_tasks.add_task(
            send_email,
            to=requester["email"],
            subject=f"Your request for '{service_name}' has been received",
            body=(
                f"Hi {requester['name']},\n\n"
                f"Your request for the service '{service_name}' has been submitted successfully.\n\n"
                f"Status: Pending\n\n"
                f"You will be notified once the provider responds."
            ),
        )

    return result


def update_request_status(
    db: Session,
    user_id: int,
    request_id: int,
    payload: RequestStatusUpdate,
    background_tasks: BackgroundTasks,
) -> RequestResponse:
    result = requests_crud.update_request_status(
        db=db,
        user_id=user_id,
        request_id=request_id,
        payload=payload,
    )

    if result.user and result.service:
        requester = result.user
        service_name = result.service["name"]
        decision = result.status.value  # "approved" or "declined"

        background_tasks.add_task(
            send_email,
            to=requester["email"],
            subject=f"Your request for '{service_name}' has been {decision}",
            body=(
                f"Hi {requester['name']},\n\n"
                f"The provider has {decision} your request for the service '{service_name}'.\n\n"
                f"Status: {decision.capitalize()}\n\n"
                f"Log in to view the full details."
            ),
        )

    return result


def delete_request(db: Session, user_id: int, request_id: int) -> None:
    requests_crud.delete_request(db=db, user_id=user_id, request_id=request_id)
