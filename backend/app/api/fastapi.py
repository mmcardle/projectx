from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from users.models import User


class APIUser(BaseModel):
    email: str
    first_name: Optional[str]  # pylint: disable=unsubscriptable-object
    last_name: Optional[str]  # pylint: disable=unsubscriptable-object

    def create_new(self):
        """
        Create a new Django User model instance.
        """
        return User.objects.create_user(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )

    def update(self, instance: User):
        """
        Update a Django User model instance and return an APIUser instance.
        """
        instance.email = self.email or instance.email
        instance.first_name = self.first_name or instance.first_name
        instance.last_name = self.last_name or instance.last_name
        instance.save()
        return SingleAPIUser.from_model(instance)


class SingleAPIUser(APIUser):
    public_uuid: UUID

    @classmethod
    def from_model(cls, instance: User):
        """
        Convert a Django User model instance to an SingleAPIUser instance.
        """
        return cls(
            public_uuid=instance.public_uuid,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
        )


class MultipleAPIUsers(BaseModel):  # pylint: disable=too-few-public-methods
    items: List[SingleAPIUser]

    @classmethod
    def from_qs(cls, qs):
        """
        Convert a Django User queryset to a MultipleAPIUsers instance.
        """
        return cls(items=[SingleAPIUser.from_model(i) for i in qs])
