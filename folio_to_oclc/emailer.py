import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime

from data import HoldingUpdateResult

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class Emailer:
    """ Send holding change results to email recipients. """

    def __init__(self, config):
        self._smtp_host = config.get("Email", "smtp_host")
        self._from_address = config.get("Email", "from_address")
        self._from_name = config.get("Email", "from_name")
        self._to_address = config.get("Email", "to_address")

    def send_results(self, results: list, job_description: str):
        message_body = job_description

        successful_sets = self._filter_results(results, True, HoldingUpdateResult.Operation.SET)
        message_body += self._format_results_message(successful_sets, "Successfully Set")

        failed_sets = self._filter_results(results, False, HoldingUpdateResult.Operation.SET)
        message_body += self._format_results_message(failed_sets, "Failure to Set")

        successful_widthdraws = self._filter_results(results, True, HoldingUpdateResult.Operation.WITHDRAW)
        message_body += self._format_results_message(successful_widthdraws, "Successfully Withdrawn")

        failed_widthdraws = self._filter_results(results, False, HoldingUpdateResult.Operation.WITHDRAW)
        message_body += self._format_results_message(failed_widthdraws, "Failure to Withdraw")

        subject = f"Holdings to OCLC: {len(failed_sets) + len(failed_widthdraws)} failure(s) " \
            f"and {len(successful_sets) + len(successful_widthdraws)} success(es) at {datetime.now()}"

        with smtplib.SMTP("localhost") as server:
            msg = EmailMessage()
            msg.set_content(message_body)
            msg['Subject'] = subject
            msg['From'] = f"{self._from_name} <{self._from_address}>" if self._from_name else self._from_address
            msg['To'] = self._to_address

            server.send_message(msg)
            log.info(f"Emailed results to {self._to_address}")

    def _filter_results(self, results, success, operation):
        return [result for result in results if result.success == success and result.operation == operation]

    def _format_results_message(self, results, heading):
        message = ""
        if len(results):
            message += f"\n\n{heading}:"
            for result in results:
                message += f"\n- {result}"
        return message
