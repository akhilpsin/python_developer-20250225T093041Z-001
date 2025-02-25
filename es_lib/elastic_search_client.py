from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from es_lib.exceptions import IDNotFoundError

load_dotenv(override=True)
ES_URL = os.getenv("ES_URL")


class ElasticsearchClient:
    """
    Class containing methods for retrieving jobs or candidates from the
    respective Elasticsearch index by ID as well as sending queries.

    Args:
        index (str): "candidates"
    """

    __client = Elasticsearch(ES_URL)

    def __init__(self, index) -> None:
        self.index = index

    def get_entity(
        self,
        *,
        id: int,
    ) -> dict:
        """
        Returns the document corresponding to the given document ID as dictionary.

        Args:
            id (int): ID of the document to return.

        Returns:
            dict: Entity object corresponding to the given ID.

        Raises:
            IDNotFoundError: If the ID was not found in the index.
        """

        try:
            return self.__client.get_source(index=self.index, id=id, _source=True)
        except NotFoundError as error:
            raise IDNotFoundError(
                "ID '{}' was not found in the index '{}'.".format(id, self.index)
            ) from error

    def search_with_bool_queries(
        self,
        *,
        should_queries: list[dict] = None,
        must_queries: list[dict] = None,
        return_source=False,
    ):
        """
        Builds a boolean query comprising the provided should and must sub queries.

        Args:
            should_queries: the sub-queries that are to be concatenated by the OR operator
            must_queries: the sub-queries that are to be concatenated by the AND operator
            return_source: whether to return the _source field of the document.

        Returns:
            The matching documents.
        """
        if not (should_queries or must_queries):
            raise ValueError("Either should_queries or must_queries must be set.")

        query = {
            "query": {
                "bool": {"must": must_queries or [], "should": should_queries or []}
            }
        }
        return self.search(query=query, return_source=return_source)

    def search(self, query: dict, return_source=False) -> dict:
        """
        Executes a query on the index.
        """
        return self.__client.search(body=query, index=self.index, source=return_source)
