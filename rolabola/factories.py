from django.contrib.auth.models import User
from rolabola.models import Player, Friendship, FriendshipRequest, Group, Membership
import factory
import faker
from django.conf import settings

faker = faker.Factory.create()

class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group
    name = "A new group"

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.LazyAttribute(lambda o: faker.first_name())
    last_name = factory.LazyAttribute(lambda o: faker.last_name())
    email = factory.LazyAttribute(lambda a: '{0}.{1}@example.com'.format(a.first_name, a.last_name).lower())
    username = email

class PlayerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Player
    user = factory.SubFactory(UserFactory)
