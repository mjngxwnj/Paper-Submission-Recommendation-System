from data_ingestion.normalizers import BaseNormalizer

class OpenalexNormalizer(BaseNormalizer):

    def _get_pipeline(self) -> list[dict]:


        pipeline = [
            {
                "$match": {
                    "doi": {
                        "$exists": True,
                        "$ne": None,
                        "$ne": "",
                        "$type": "string"
                    }
                }
            },

            {
                "$addFields": {
                    "doi": {
                        "$replaceOne": {
                            "input": "$doi",
                            "find": "https://doi.org/",
                            "replacement": ""
                        }
                    }
                }
            },

            {
                "$project": {
                    "_id": 0,
                    "doi": 1,
                    "title": 1,
                    "publication_year": 1,
                    "openaccess": "$primary_locatoin",
                    "execution_datetime": 1,
                    "ingestion_source": 1
                }
            },

            {
                "$merge": {
                    "into": self._target_collection_name,
                    "on": "doi",
                    "whenMatched": "keepExisting",
                    "whenNotMatched": "insert"
                }
            }

        ]

        return pipeline


    def _get_index_field(self) -> list[str]:
        """
        Return a list of field names that should have index in target collection.
        """

        return ["doi", "execution_datetime"]

