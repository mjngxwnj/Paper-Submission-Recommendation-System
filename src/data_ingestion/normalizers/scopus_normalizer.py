from data_ingestion.normalizers import BaseNormalizer

class ScopusNormalizer(BaseNormalizer):

    def _get_pipeline(self) -> list[dict]:
        """
        Returns the aggregation pipeline for normalizing Scopus documents.

        Pipeline steps:
        1. Transform fields:
            - Parse prism:coverDate into publication_year, publication_month, publication_day.
            - Convert openaccess to Boolean.
            - Extract the first link with @ref=self from link array as abstractlink.
            - Convert dc:creator string into an array author.
            - Set orcid as an array containing null (no ORCID in current dataset).
            - Extract keywords from subjects.$ array.
            - Set target_venue from prism:publicationName (conference or journal name).
        2. Project only necessary fields for the target collection.
        3. Upsert using DOI as the key with keepExisting:
            - If the DOI exists, retain all existing values in the target collection.
            - If the DOI does not exist, insert the new document.
        """
        pipeline = [
            {
                "$match": {
                    "prism:doi": {
                        "$exists": True,
                        "$type": "string",
                        "$nin": [None, "", "None"]
                    }
                }
            },

            {
                "$addFields": {
                    "pubDate": { "$dateFromString": { "dateString": "$prism:coverDate" } },

                    "openaccess": { "$cond": [{ "$eq": ["$openaccess", "1"] }, True, False] },

                    "abstractlink": {
                        "$first": {
                            "$map": {
                                "input": {
                                    "$filter": {
                                        "input": { "$ifNull": ["$link", []] },
                                        "cond": { "$eq": ["$$this.@ref", "self"] }
                                    }
                                },
                                "as": "l",
                                "in": "$$l.@href"
                            }
                        }
                    },

                    "author": {
                        "$cond": [
                            { "$ne": [{ "$ifNull": ["$dc:creator", ""] }, ""] },
                            ["$dc:creator"],
                            None
                        ]
                    },

                    "keyword": {
                        "$map": {
                            "input": { "$ifNull": ["$subjects", []] },
                            "in": {
                                "$getField": {
                                    "field": { "$literal": "$" },
                                    "input": "$$this"
                                }
                            }
                        }
                    },

                    "target_venue": { "$ifNull": ["$prism:publicationName", None] }
                }
            },

            {
                "$project": {
                    "_id": 0,
                    "doi": "$prism:doi",
                    "title": "$dc:title",
                    "publication_year": { "$year": "$pubDate" },
                    "publication_month": { "$month": "$pubDate" },
                    "publication_day": { "$dayOfMonth": "$pubDate" },
                    "openaccess": 1,
                    "abstractlink": 1,
                    "keyword": 1,
                    "abstract": 1,
                    "author": 1,
                    "orcid": [None],
                    "target_venue": 1,
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

