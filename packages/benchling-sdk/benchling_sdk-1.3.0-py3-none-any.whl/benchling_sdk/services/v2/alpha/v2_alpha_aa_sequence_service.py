from benchling_api_client.v2.alpha.api.aa_sequences import find_matching_regions_aa_sequences
from benchling_api_client.v2.alpha.models.aa_sequences_find_matching_region import (
    AaSequencesFindMatchingRegion,
)
from benchling_api_client.v2.alpha.models.async_task_link import AsyncTaskLink

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.services.v2.base_service import BaseService


class V2AlphaAaSequenceService(BaseService):
    """
    V2-Alpha AA Sequences.

    AA Sequences are the working units of cells that make everything run (they help make structures, catalyze
    reactions and allow for signaling - a kind of internal cell communication). On Benchling, these are comprised
    of a string of amino acids and collections of other attributes, such as annotations.

    See https://benchling.com/api/v2-alpha/reference#/AA%20Sequences
    """

    @api_method
    def find_matching_regions(self, find_matching_region: AaSequencesFindMatchingRegion) -> AsyncTaskLink:
        """
        Find matching regions for AA sequences.

        See https://benchling.com/api/v2-alpha/reference#/AA%20Sequences/findMatchingRegionsAASequences
        """
        response = find_matching_regions_aa_sequences.sync_detailed(
            client=self.client, json_body=find_matching_region
        )
        return model_from_detailed(response)
