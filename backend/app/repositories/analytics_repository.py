from app.repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository):
    collection_name = "analytics"

    async def get_by_date_range(self, start_date: str, end_date: str) -> list[dict]:
        cursor = self.collection.find(
            self._base_filter({
                "date": {"$gte": start_date, "$lte": end_date},
            })
        ).sort("date", 1)
        docs = await cursor.to_list(365)
        return self._serialize_many(docs)
