from data_ingestion.normalizers import BaseNormalizer

class SourceBNormalizer(BaseNormalizer):

    def _get_pipeline(self) -> list[dict]:
        pipeline = [
            {"$project": {
                "_id": 0,
                "title": "$title",
                "authors": "$authors",
                "year": "$year",
                "keywords": {"$ifNull": ["$keywords", []]},
                "source": {"$literal": "source_b"}
            }},

            {"$merge": {
                "into": self._target_collection_name,
                "on": "title",
                "whenMatched": "merge",
                "whenNotMatched": "insert"
            }}
        ]

        return pipeline


    def _get_index_field(self) -> list[str]:
        """
        Return a list of field names that should have index in target collection.
        """

        return ["title"]
