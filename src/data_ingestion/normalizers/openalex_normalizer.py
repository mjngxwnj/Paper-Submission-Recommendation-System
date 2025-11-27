from data_ingestion.normalizers import BaseNormalizer

class OpenalexNormalizer(BaseNormalizer):

    def _get_pipeline(self) -> list[dict]:
        """
        Returns the aggregation pipeline for normalizing OpenAlex documents.

        Pipeline steps:
        1. Filter documents:
            - Keep only documents with a valid DOI (exists, not null, not empty string).
            - Keep only documents with a non-null, non-empty abstract.
        2. Transform fields:
            - Normalize DOI by removing the 'https://doi.org/' prefix.
            - Convert crossref_date (ISO string) into a date object for extracting publication_year, publication_month, publication_day.
            - Extract keyword names from the keywords array.
            - Extract author names from authorships array, preserving order.
            - Extract ORCID codes from authorships array, stripping the 'https://orcid.org/' prefix; keep None if missing.
        3. Project only necessary fields for the target collection:
            - Include DOI, title, publication_year/month/day, openaccess, abstractlink, keywords, abstract, author list, ORCID list, target venue, execution_datetime, ingestion_source.
        4. Upsert using DOI as the key with keepExisting:
            - If the DOI exists, retain all existing values in the target collection.
            - If the DOI does not exist, insert the new document.
        """

        pipeline = [
            {
                "$match": {
                    "doi": {
                        "$exists": True,
                        "$type": "string",
                        "$nin": [None, ""]
                    },
                    "abstract": {
                        "$exists": True,
                        "$type": "string",
                        "$nin": [None, "", "None"]
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
                    },

                    "crossref_date_obj": { "$dateFromString": { "dateString": "$crossref_date" } },

                    "keyword": {
                        "$map": {
                            "input": { "$ifNull": ["$keywords", []] },
                            "as": "k",
                            "in": "$$k.display_name"
                        }
                    },

                    "author": {
                        "$map": {
                            "input": {"$ifNull": ["$authorships", []]},
                            "as": "a",
                            "in": "$$a.author.display_name"
                        }
                    },

                    "orcid": {
                        "$map": {
                            "input": {"$ifNull": ["$authorships", []]},
                            "as": "a",
                            "in": {
                                "$cond": [
                                    { "$eq": ["$$a.author.orcid", None] },
                                    None,
                                    {
                                        "$replaceOne": {
                                            "input": "$$a.author.orcid",
                                            "find": "https://orcid.org/",
                                            "replacement": ""
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            },

            {
                "$project": {
                    "_id": 0,
                    "doi": 1,
                    "title": 1,
                    "publication_year": { "$year": "$crossref_date_obj" },
                    "publication_month": { "$month": "$crossref_date_obj" },
                    "publication_day": { "$dayOfMonth": "$crossref_date_obj" },
                    "openaccess": "$primary_location.is_oa",
                    "abstractlink": "$primary_location.pdf_url",
                    "keyword": 1,
                    "abstract": 1,
                    "author": 1,
                    "orcid": 1,
                    "target_venue": "$primary_location.raw_source_name",
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

