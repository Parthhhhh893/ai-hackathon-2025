from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

backend_routers = APIRouter()

@backend_routers.post("/upload-doc/")
async def upload_doc_for_evaluation(request: Request, db: Session = Depends(get_db)):
    return await handle_api_request(
        request=request,
        helper_function=send_notification_helper,
        schema=SendNotificationSchema,
        db=db,
        partner_name="USER_SERVICE"
        # partner_name=request.state.partner_name
    )