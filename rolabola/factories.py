from django.contrib.auth.models import User
from rolabola.models import Player, Friendship, FriendshipRequest, Group, Membership, Venue
from geoposition import Geoposition
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
    password = factory.PostGenerationMethodCall('set_password', '123456')

class PlayerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Player
    user = factory.SubFactory(UserFactory)

class VenueFactory(factory.DjangoModelFactory):
    class Meta:
        model = Venue
    quadra = factory.LazyAttribute(lambda o: faker.company())
    address = factory.LazyAttribute(lambda o: faker.address())
    location = Geoposition(52.522906,13.41156)
