# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api.dtm_pb2 import Activity, Finding as FindingDtm
from contrast.utils.string_utils import protobuf_safe

from contrast.agent.policy.constants import (
    CURRENT_FINDING_VERSION,
    MINIMUM_FINDING_VERSION,
)


from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class Finding(object):
    """
    Wrapper around api.dtm_pb2.Finding
    """

    def __new__(cls, rule, properties, **kwargs):
        finding = FindingDtm()

        rule.add_events_to_finding(finding, **kwargs)

        finding.rule_id = protobuf_safe(rule.name)

        for key, value in properties.items():
            finding.properties[key] = value

        hash_code = rule.generate_preflight_hash(**kwargs)

        finding.hash_code = hash_code
        finding.preflight = ",".join([rule.name, hash_code])

        logger.debug("Created finding for %s", rule.name)
        logger.debug("initial preflight value: %s", finding.preflight)

        return finding

    @staticmethod
    def pick_version(finding):
        """
        Given a finding dtm message, determine the finding version.

        Note:  This is a staticmethod and not applied when the create method is called
        because sometimes the finding version cannot be determined until later in the
        request lifecycle.

        :param finding: instance of dtm_pb2.Finding
        :return: finding version
        """
        # dataflow or non-dataflow finding with route(s)
        if finding.routes:
            return CURRENT_FINDING_VERSION

        # non-dataflow rules without routes
        if not finding.events:
            return CURRENT_FINDING_VERSION

        # dataflow finding without routes
        return MINIMUM_FINDING_VERSION


def send_finding(finding, context=None):
    """
    Send a finding by either appending it to request context
    OR sending it immediately.

    If `context` exists, agent should not sent message immediately because
    current route needs to be appended in `append_route_to_findings`

    :param finding:  api.dtm_pb2.Finding instance
    :param context: Request context instance
    :return: None
    """
    if context:
        context.activity.findings.extend([finding])
        return

    activity = Activity()
    activity.findings.extend([finding])

    from contrast.agent.settings import Settings
    settings = Settings()

    if settings.config.is_service_bypassed:
        from contrast.reporting import ReportingClient
        from contrast.reporting import teamserver_messages

        client = ReportingClient()
        client.add_message(teamserver_messages.Preflight(activity))

    else:
        # Import here to prevent circular import.
        from contrast.agent.service_client import send_messages
        send_messages([activity])
