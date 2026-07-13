from app.repositories.feedback_repository import FeedbackRepository


class FeedbackService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.repo = FeedbackRepository(db)

    async def submit_feedback(
        self,
        message_id: str,
        rating: int,
        comment: str | None = None,
        thumbs: str | None = None,
    ) -> dict:
        return await self.repo.create({
            "workspace_id": self.workspace_id,
            "message_id": message_id,
            "rating": rating,
            "comment": comment,
            "thumbs": thumbs,
        })

    async def get_csat(self) -> dict:
        return await self.repo.get_csat_stats(self.workspace_id)
