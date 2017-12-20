""" This module manage the users permissions with any repository. """
from tornado.web import HTTPError
from app.handlers.base import BothubBaseHandler
from app.models.base_models import DATABASE
from app.models.models import Repository, RepositoryAuthorization
from app.utils import INVALID_TOKEN, INVALID_REPOSITORY, validate_uuid


class RepositoryManagerHandler(BothubBaseHandler):
    allowed_permissions = []

    def _check_repo_user_authorization(self, repository_uuid):
        if not validate_uuid(repository_uuid):
            raise HTTPError(reason=INVALID_REPOSITORY, status_code=404)

        with DATABASE.execution_context():
            repository = Repository.select().where(Repository.uuid == repository_uuid)
            if repository.exists():
                repository = repository.get()
            else:
                raise HTTPError(reason=INVALID_REPOSITORY, status_code=404)
            user_repo_authorization = RepositoryAuthorization.select(RepositoryAuthorization.permission) \
                                                             .where(RepositoryAuthorization.profile == self.get_cleaned_token()) \
                                                             .where(RepositoryAuthorization.repository == repository_uuid)
            if user_repo_authorization.exists():
                user_repo_authorization = user_repo_authorization.get()
            else:
                raise HTTPError(reason=INVALID_TOKEN, status_code=401)

        if user_repo_authorization not in self.allowed_permissions and repository.private:
            raise HTTPError(reason=INVALID_TOKEN, status_code=401)
