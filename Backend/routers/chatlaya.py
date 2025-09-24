from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from schemas.chat_schema import ChatRequest, ChatResponse, FeedbackPayload
from services import router_ai, rag_service, logger_service
from deps.auth import get_bearer_token

router = APIRouter(tags=["Chat-LAYA"])

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, token: str | None = Depends(get_bearer_token)):
    user_msg = req.get_last_user_message()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Aucun message utilisateur trouvé")

    # 1) Log user
    logger_service.log_message("user", user_msg)

    # 2) RAG
    passages, sources = rag_service.search_context(req.query_text(), req.top_k)

    # 3) Appel IA
    answer = router_ai.chat_completion(req.messages, context="\n".join(passages))

    # 4) Log assistant
    logger_service.log_message("assistant", answer)

    return ChatResponse(answer=answer, citations=sources)


@router.post("/ingest")
def ingest(file: UploadFile = File(...), token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication requise")
    ok, detail = rag_service.ingest_file(file)
    if not ok:
        raise HTTPException(status_code=400, detail=detail)
    return {"status": "ok", "detail": detail}


@router.post("/feedback")
def feedback(payload: FeedbackPayload):
    logger_service.log_feedback(
        message_id=payload.message_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    return {"status": "ok"}
