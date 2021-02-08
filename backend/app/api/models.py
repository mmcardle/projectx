from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from users.models import User


##########
# Would be useful to just have one model here
# https://github.com/tiangolo/fastapi/issues/1357
##########
class FastAPIUser(BaseModel):
    email: str
    first_name: Optional[str]  # pylint: disable=unsubscriptable-object
    last_name: Optional[str]  # pylint: disable=unsubscriptable-object

    def new_user(self):
        """
        Convert a Django User model instance to an FastAPIUser instance.
        """
        return User.objects.create_user(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )

    def update_user(self, instance: User):
        """
        Convert a Django User model instance to an FastAPIUser instance.
        """
        instance.email = self.email or instance.email
        instance.first_name = self.first_name or instance.first_name
        instance.last_name = self.last_name or instance.last_name
        instance.save()
        return SingleFastAPIUser.from_model(instance)


class SingleFastAPIUser(FastAPIUser):
    public_uuid: UUID

    @classmethod
    def from_model(cls, instance: User):
        """
        Convert a Django User model instance to an FastAPIUser instance.
        """
        return cls(
            public_uuid=instance.public_uuid,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
        )


class MultipleFastAPIUsers(BaseModel):  # pylint: disable=too-few-public-methods
    items: List[SingleFastAPIUser]

    @classmethod
    def from_qs(cls, qs):
        """
        Convert a Django USer queryset to SingleFastAPIUser instances.
        """
        return cls(items=[SingleFastAPIUser.from_model(i) for i in qs])
