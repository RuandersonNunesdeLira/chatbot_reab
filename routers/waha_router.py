from fastapi import APIRouter
from services.waha_service import send_message
from workers import tasks

router = APIRouter(prefix="/waha", tags=["WAHA"])

@router.post("/webhook")
async def receive_whatsapp_message(data: dict,) -> dict[str, str]:

    event_dispatcher(data)
    
    return {"status": "sucess"}


def event_dispatcher(data: dict) -> None:
        
        event_type = data.get("event")

        if event_type == "session.status":
              print("session status", data["payload"]["status"])
        elif event_type == "message":
            chat_id = data["payload"]["from"]
            message = data["payload"]["body"]

            tasks.task_answer.delay(chat_id, message)
        else:
              print("EVENTO", event_type)