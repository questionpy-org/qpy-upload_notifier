import base64
import json

from time import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from questionpy import get_qpy_environment, Attempt, Question, ResponseNotScorableError, NeedsManualScoringError, BaseScoringState

from .form import UploadNotifierModel


class UploadNotifierScoringState(BaseScoringState):
    webhook_response_code: int | None = None
    error_message: str | None = None


class UploadNotifierAttempt(Attempt):
    scoring_state: UploadNotifierScoringState

    def _send_to_webhook(self, data: dict) -> None:
        token = self.question.options.username + ":" + self.question.options.password
        token = base64.b64encode(token.encode()).decode()

        request = Request(
            self.question.options.webhook_url,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {token}"
            },
            data=json.dumps(data).encode(),
        )

        try:
            with urlopen(request) as response:
                pass
            self.scoring_state = UploadNotifierScoringState(
                webhook_response_code=response.getcode(),
            )
        except HTTPError as error:
            self.scoring_state = UploadNotifierScoringState(
                webhook_response_code=error.getcode(),
                error_message=str(error),
            )
            raise ResponseNotScorableError from error
        except URLError as error:
            self.scoring_state = UploadNotifierScoringState(
                error_message=str(error),
            )
            raise ResponseNotScorableError from error

    def _compute_score(self) -> float:
        attributes = get_qpy_environment().request_info.lms_provided_attributes.model_dump()
        if submission_id := attributes["lms"].pop("lms_moodle_assignment_submission_id", None):
            attributes["lms"]["submission_id"] = submission_id

        if module_instance := attributes["lms"].pop("lms_moodle_module_instance", None):
            attributes["lms"]["module_instance"] = module_instance

        self._send_to_webhook(attributes)

        raise NeedsManualScoringError

    def _error_occurred(self) -> bool:
        return self.scoring_state and self.scoring_state.error_message is not None

    @property
    def specific_feedback(self) -> str | None:
        if self._error_occurred():
            return self.jinja2.get_template("retry_message.xhtml.j2").render()
        return None

    @property
    def formulation(self) -> str:
        data = {"timestamp": time()} if self._error_occurred() else {}
        return self.jinja2.get_template("formulation.xhtml.j2").render(data)


class UploadNotifierQuestion(Question):
    attempt_class = UploadNotifierAttempt

    options: UploadNotifierModel
