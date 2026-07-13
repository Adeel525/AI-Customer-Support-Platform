from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document(self, document_id: str, workspace_id: str):
    from api.services.knowledge import process_document as sync_process

    try:
        sync_process(document_id, workspace_id)
    except Exception as exc:
        logger.error("Document processing failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=2)
def crawl_website(self, job_id: str, workspace_id: str):
    try:
        from api.views.crawler import _execute_crawl

        _execute_crawl(job_id, workspace_id)
    except Exception as exc:
        logger.error("Crawl failed: %s", exc)
        raise self.retry(exc=exc, countdown=120)


@shared_task
def aggregate_daily_analytics():
    from datetime import datetime, timedelta, timezone
    from api.models import Workspace, Analytics, Conversation, Ticket, Feedback

    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    for ws in Workspace.objects:
        ws_id = str(ws.id)
        convs = list(Conversation.objects(workspace_id=ws_id))
        tickets = list(Ticket.objects(workspace_id=ws_id))
        feedbacks = list(Feedback.objects(workspace_id=ws_id))
        metrics = {
            "total_conversations": len(convs),
            "resolved_conversations": sum(1 for c in convs if c.status == "resolved"),
            "escalated_conversations": sum(1 for c in convs if c.status == "escalated"),
            "ticket_volume": len(tickets),
            "csat_score": (
                round(sum(1 for f in feedbacks if (f.rating or 0) >= 4) / max(len(feedbacks), 1) * 100, 1)
                if feedbacks
                else 0
            ),
        }
        Analytics.objects(workspace_id=ws_id, date=yesterday).update_one(
            upsert=True,
            set__metrics=metrics,
            set_on_insert__workspace_id=ws_id,
            set_on_insert__date=yesterday,
        )


@shared_task
def sync_scheduled_crawlers():
    from api.models import CrawlerJob

    for job in CrawlerJob.objects(status__ne="running"):
        crawl_website.delay(str(job.id), job.workspace_id)


@shared_task
def summarize_conversation(conversation_id: str, workspace_id: str):
    from datetime import datetime, timezone
    from api.models import Conversation, Message
    from core.ai.llm_client import LLMClient

    messages = list(Message.objects(conversation_id=conversation_id).order_by("created_at"))
    if not messages:
        return
    conv_text = "\n".join(f"{m.role}: {m.content}" for m in messages)
    summary = LLMClient().generate(
        [{"role": "user", "content": f"Summarize this support conversation in 2-3 sentences:\n{conv_text[:3000]}"}],
        temperature=0.3,
        max_tokens=200,
    )
    Conversation.objects(id=conversation_id).update_one(
        set__summary=summary,
        set__summarized_at=datetime.now(timezone.utc),
    )
