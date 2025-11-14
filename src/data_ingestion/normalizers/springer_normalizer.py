from data_ingestion.normalizers import BaseNormalizer

class SpringerNormalizer(BaseNormalizer):
    def _get_pipeline(self) -> list[dict]:
        """
        Returns the aggregation pipeline for normalizing Springer documents.

        Pipeline steps:
        1. Transform fields:
            - Parse publicationDate into year, month, and day.
            - Convert publicationType to lowercase.
            - Convert openaccess to Boolean.
            - Extract the first PDF link from url as abstractlink.
            - Split creators array into two separate lists: author and orcid.
            - Extract conference name from conferenceInfo as target_venue.
        2. Project only necessary fields for the target collection.
        3. Upsert using DOI as the key with 'keepExisting':
            - If the DOI exists, retain all existing values in the target collection.
            - If the DOI does not exist, insert the new document.
        """

        pipeline = [
            #Transform fields.
            {
                "$addFields": {
                    "pubDate": {"$dateFromString": {"dateString": "$publicationDate"}},

                    "openaccess": {"$eq": ["$openaccess", "true"]},

                    "publication_type": {"$toLower": "$publicationType"},

                    "abstractlink": {
                        "$arrayElemAt": [
                            {
                                "$map": {
                                    "input": {
                                        "$filter": { "input": "$url", "cond": { "$eq": ["$$this.format", "pdf"] } }
                                    },
                                    "as": "u",
                                    "in": "$$u.value"
                                }
                            },
                            0
                        ]
                    },

                    "author": {"$map": {"input": {"$ifNull": ["$creators", []]}, "as": "c", "in": "$$c.creator"}},

                    "orcid":  {"$map": {"input": {"$ifNull": ["$creators", []]}, "as": "c", "in": "$$c.ORCID"}},

                    "target_venue": {
                        "$arrayElemAt": [
                            {"$map": {"input": {"$ifNull": ["$conferenceInfo", []]}, "as": "c", "in": "$$c.confSeriesName"}},
                            0
                        ]
                    }
                }
            },

            #Project only neccessary fields for the target
            {
                "$project": {
                "_id": 0,
                "doi": 1,
                "title": 1,
                "publication_year": {"$year": "$pubDate"},
                "publication_month": {"$month": "$pubDate"},
                "publication_day": {"$dayOfMonth": "$pubDate"},
                "publication_type": 1,
                "language": 1,
                "openaccess": 1,
                "abstractlink": 1,
                "keyword": 1,
                "abstract": 1,
                "author": 1,
                "orcid": 1,
                "target_venue": 1
                }
            },

            #Upsert into target collection
            {"$merge": {
                "into": self._target_collection_name,
                "on": "doi",
                "whenMatched": "merge",
                "whenMatched": "keepExisting",
                "whenNotMatched": "insert"
            }}
        ]

        return pipeline


    def _get_index_field(self) -> list[str]:
        """
        Return a list of field names that should have index in target collection.
        """

        return ["doi"]

