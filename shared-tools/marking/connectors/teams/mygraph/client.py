import os
import sys
from pathlib import Path

from msgraph import GraphServiceClient
from msgraph.generated.models.user import User
from msgraph.generated.models.team import Team
from msgraph.generated.teams.item.members.add.add_post_request_body import AddPostRequestBody
from msgraph.generated.models.aad_user_conversation_member import AadUserConversationMember
from msgraph.generated.models.group import Group
from msgraph.generated.education.classes.item.assignments.item.submissions.submissions_request_builder import SubmissionsRequestBuilder
from msgraph.generated.models.password_profile import PasswordProfile
from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
from msgraph.generated.teams.item.archive.archive_post_request_body import ArchivePostRequestBody
from msgraph.generated.education.users.users_request_builder import UsersRequestBuilder
from msgraph.generated.models.education_class import EducationClass
from msgraph.generated.models.education_points_outcome import EducationPointsOutcome
from msgraph.generated.models.education_assignment_points_grade import EducationAssignmentPointsGrade
from msgraph.generated.models.education_feedback import EducationFeedback
from msgraph.generated.models.education_feedback_outcome import EducationFeedbackOutcome
from msgraph.generated.models.education_item_body import EducationItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.education_assignment import EducationAssignment
from msgraph.generated.models.education_assignment_points_grade_type import EducationAssignmentPointsGradeType
from msgraph.generated.education.classes.item.assignments.item.submissions.item.outcomes.outcomes_request_builder import OutcomesRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from azure.identity import DeviceCodeCredential
from azure.identity.aio import ClientSecretCredential
import kiota_http

# Load credentials from the repo-root .env file.
# parents[4] = shared-tools/, repo_env.py lives there
_repo_env = Path(__file__).resolve().parents[4] / "repo_env.py"
if _repo_env.exists():
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("repo_env", _repo_env)
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    _mod.load_repo_env()

MS_CLIENT_ID = os.environ["MS_CLIENT_ID"]
MS_TENANT_ID = os.environ["MS_TENANT_ID"]
MS_SECRET_VALUE = os.environ["MS_SECRET_VALUE"]


class MSGraphClient:
    def __init__(self, is_application=True):
        self.client = None
        self._is_application = is_application
        self.renew_client(is_application)

    def renew_client(self, is_application=True):
        print("Renewing client...")
        try:
            sys.stdout.flush()
        except Exception:
            pass
        self.client = None
        scopes = ["https://graph.microsoft.com/.default"]
        if is_application:
            credential = ClientSecretCredential(
                client_id=MS_CLIENT_ID, tenant_id=MS_TENANT_ID, client_secret=MS_SECRET_VALUE
            )
            self.client = GraphServiceClient(credential, scopes=scopes)
        else:
            credential = DeviceCodeCredential(client_id=MS_CLIENT_ID, tenant_id=MS_TENANT_ID)
            self.client = GraphServiceClient(credential, scopes=scopes)

    async def get_team_by_id(self, team_id):
        return await self.client.teams.by_team_id(team_id).get()

    async def get_user_by_id(self, user_id):
        return await self.client.users.by_user_id(user_id).get()

    async def search_teams(self, keywords):
        query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
            search='"displayName:' + keywords + '"',
        )
        request_configuration = RequestConfiguration(query_parameters=query_params)
        request_configuration.headers.add("ConsistencyLevel", "eventual")
        response = await self.client.groups.get(request_configuration=request_configuration)
        groups = response.value
        while response.odata_next_link is not None:
            response = await self.client.groups.with_url(response.odata_next_link).get(
                request_configuration=request_configuration
            )
            groups.extend(response.value)
        return groups

    async def get_group_members(self, group_id):
        response = await self.client.groups.by_group_id(group_id).members.get()
        members = response.value
        while response.odata_next_link is not None:
            response = await self.client.groups.by_group_id(group_id).members.with_url(
                response.odata_next_link
            ).get()
            members.extend(response.value)
        return members

    async def get_assignments(self, course_id):
        response = await self.client.education.classes.by_education_class_id(course_id).assignments.get()
        assignments = response.value
        while response.odata_next_link is not None:
            response = await self.client.education.classes.by_education_class_id(
                course_id
            ).assignments.with_url(response.odata_next_link).get()
            assignments.extend(response.value)
        return assignments

    async def get_submissions(self, course_id, assignment_id):
        query_params = SubmissionsRequestBuilder.SubmissionsRequestBuilderGetQueryParameters(
            expand="submittedResources,outcomes,resources",
        )
        config = RequestConfiguration(query_parameters=query_params)
        response = await (
            self.client.education.classes.by_education_class_id(course_id)
            .assignments.by_education_assignment_id(assignment_id)
            .submissions.get(request_configuration=config)
        )
        submissions = response.value
        while response.odata_next_link is not None:
            response = await (
                self.client.education.classes.by_education_class_id(course_id)
                .assignments.by_education_assignment_id(assignment_id)
                .submissions.with_url(response.odata_next_link)
                .get(request_configuration=config)
            )
            submissions.extend(response.value)
        return submissions

    async def get_submitted_resources(self, course_id, assignment_id, submission_id):
        response = await (
            self.client.education.classes.by_education_class_id(course_id)
            .assignments.by_education_assignment_id(assignment_id)
            .submissions.by_education_submission_id(submission_id)
            .resources.get()
        )
        resources = response.value
        while response.odata_next_link is not None:
            response = await (
                self.client.education.classes.by_education_class_id(course_id)
                .assignments.by_education_assignment_id(assignment_id)
                .submissions.by_education_submission_id(submission_id)
                .resources.with_url(response.odata_next_link)
                .get()
            )
            resources.extend(response.value)
        return resources

    async def download_file(self, file_url, file_path):
        drive_id = file_url.split("drives/")[1].split("/")[0]
        item_id = file_url.split("items/")[1].split("/")[0]
        while True:
            try:
                item = await (
                    self.client.drives.by_drive_id(drive_id)
                    .items.by_drive_item_id(item_id)
                    .content.get()
                )
            except kiota_http._exceptions.RedirectError as e:
                print("Error downloading file:", e.message)
                continue
            except Exception as e:
                print("Error downloading file:", e)
                continue
            break
        if item is None:
            item = b""
        with open(file_path, "wb") as f:
            f.write(item)
        return item

    async def submit_comments(self, course_id, assignment_id, submission_id, comments):
        query_params = OutcomesRequestBuilder.OutcomesRequestBuilderGetQueryParameters(
            filter="isof('microsoft.graph.educationFeedbackOutcome')",
        )
        request_configuration = RequestConfiguration(query_parameters=query_params)
        result = await (
            self.client.education.classes.by_education_class_id(course_id)
            .assignments.by_education_assignment_id(assignment_id)
            .submissions.by_education_submission_id(submission_id)
            .outcomes.get(request_configuration=request_configuration)
        )
        feedback_outcome = result.value[0]
        request_body = EducationFeedbackOutcome(
            feedback=EducationFeedback(
                text=EducationItemBody(
                    content=comments.replace("\n", "<br>"),
                    content_type=BodyType.Html,
                ),
            ),
        )
        return await (
            self.client.education.classes.by_education_class_id(course_id)
            .assignments.by_education_assignment_id(assignment_id)
            .submissions.by_education_submission_id(submission_id)
            .outcomes.by_education_outcome_id(feedback_outcome.id)
            .patch(request_body)
        )

    async def submit_marks(self, course_id, assignment_id, submission_id, marks):
        query_params = OutcomesRequestBuilder.OutcomesRequestBuilderGetQueryParameters(
            filter="isof('microsoft.graph.educationPointsOutcome')",
        )
        request_configuration = RequestConfiguration(query_parameters=query_params)
        result = await (
            self.client.education.classes.by_education_class_id(course_id)
            .assignments.by_education_assignment_id(assignment_id)
            .submissions.by_education_submission_id(submission_id)
            .outcomes.get(request_configuration=request_configuration)
        )
        points_outcome = result.value[0]
        request_body = EducationPointsOutcome(
            odata_type="#microsoft.graph.educationPointsOutcome",
            points=EducationAssignmentPointsGrade(
                odata_type="#microsoft.graph.educationAssignmentPointsGrade",
                points=float(marks),
            ),
        )
        return await (
            self.client.education.classes.by_education_class_id(course_id)
            .assignments.by_education_assignment_id(assignment_id)
            .submissions.by_education_submission_id(submission_id)
            .outcomes.by_education_outcome_id(points_outcome.id)
            .patch(request_body)
        )

    async def return_submission(self, course_id, assignment_id, submission_id):
        return await (
            self.client.education.classes.by_education_class_id(course_id)
            .assignments.by_education_assignment_id(assignment_id)
            .submissions.by_education_submission_id(submission_id)
            .return_.post()
        )

    async def update_assignment_max_score(self, course_id, assignment_id, max_score):
        grading = EducationAssignmentPointsGradeType(
            odata_type="#microsoft.graph.educationAssignmentPointsGradeType",
            max_points=float(max_score),
        )
        request_body = EducationAssignment(
            odata_type="#microsoft.graph.educationAssignment",
            grading=grading,
        )
        return await (
            self.client.education.classes.by_education_class_id(course_id)
            .assignments.by_education_assignment_id(assignment_id)
            .patch(request_body)
        )
