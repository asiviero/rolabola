# Rolabola

[![Build Status](https://travis-ci.org/asiviero/rolabola.svg?branch=develop)](https://travis-ci.org/asiviero/rolabola)

Rolabola is a project to create a social network to make it easy for people to set up groups that regularly play sports together. This is very common in our home country (Brazil) and the whole process of scheduling the matches, calling up people, collecting everyone's money, keeping track of who's going, who actually played, how much everyone played and so on is incredibly laboursome, and usually a burden carried by a single person.

A couple of existing websites provide this kind of functionality, however most of them aren't complete enough, are missing parts, and so on. This project is the result of a lot of experimentation and frustration with all these systems, done by people who will actually use this system to manage their own matches.

A complete and detailed roadmap is not defined yet, but it will be some time soon. Our main goals are:

1. A fully functional website to achieve group making and match scheduling, with some basic secondary functions (such as keeping track of goals scored and other kinds of statistics)
1. A kind of bookkeeping system, through which users would be able to pay for the matches. This would be likely through PayPal since it makes money available in a matter of days. This could be replaced entirely for self-hosting solutions, however our focus is also to provide a full solution in the cloud as well.
1. Android and iOS apps, of course. Most of the functionality could be done in one click, so it could also be ported to a mobile phone.
1. More ambitious and long term: Getting in touch with venus owners to provide a scheduling platform and also to make it possible to match organizers to pay them directly through our application.

## FAQ

1. Where are the detailed specs?

  Not done yet, we had a kind of idea of what it would be but nothing concrete yet. It will be done some time soon.

1. Do you have a design for the interface, branding, etc?

  Not yet. [Resultate](http://www.resultate.com.br), the company the main devs work for, is responsible for that. Branding material and visual identity is likely to be copyrighted since this is also an attempt at a product.

## Developers

Rolabola is built on Django, and there are a few dependencies. They are all listed in the `vagrant_provision.sh`. A `Vagrantfile` is also provided to make it easy to set up a dev environment.

First of all, clone the repo:

    $ git clone git@github.com:asiviero/rolabola.git

After that, you can run it locally or inside a Vagrant box. We're also very early in the development process, so we're using SQLite and Django's built-in server. **Both will be changed once this project get more mature.**

### Running inside a Vagrant box

This is the easiest way of doing it, since Vagrant will provision all the requirements. Just run the provision commands:

    $ cd rolabola
    $ vagrant up # "vagrant up --provision" in case the provision script changes
    $ vagrant ssh

You might run into some unusual effects on Mac OS X when dealing with Selenium inside a Vagrant box. In case you're developing in a Mac environment, replace the last command with `vagrant ssh -- -X`, which will tell Vagrant to use Mac's X as a graphic environment.

After that, inside Vagrant:

    $ cd /vagrant/
    $ python3 manage.py runserver 0.0.0.0:8000 &
    $ celery -A social worker -l info &

If eveything went smoothly, Rolabola will be running in `http://localhost:8001`. Yes, 8001, not 8000.

### Running locally

Running locally requires all the requirements to be installed in the computer used to do so. It's likely that we'll update something like a `requirements.txt` further down the road so it's easier to use `virtualenv`, but it's not available at this time. There are a couple of dependencies to be installed system-wide, and a lot installed by pip. For the system-wide, in deb-based systems, it can be done with:

    # apt-get install -y python3 python3-pip git firefox redis-server

(Instructions on other distributions, such as Amazon Linux and CentOS will soon be made available)

Then install the pip dependencies:

    # pip3 install django==1.8
    # pip3 install --upgrade selenium
    # pip3 install factory_boy fake-factory Pillow django-material python-dateutil django-allauth djangoajax celery redis django-appconf

## Tests

As you all know, automated tests are incredibly important. Currently, there are two main test files, `functional_tests/tests.py` and `rolabola/tests.py`. As the names suggests, they test the system from different perspectives.

  1. `functional_tests/tests.py`: Using Selenium, these tests involve "real users" acting on the website and interacting with its interface. They will usually correspond to a set of internal tests (either unit tests or integration tests), but done from this perspective, although some `setUp` tasks make use of internal methods.
  1. `rolabola/tests.py`: Unit and integration tests, these should test features at the smallest level possible.

Running the tests can be done in several ways:

    $ python3 manage.py test # tests everything
    $ python3 manage.py test functional_tests # functional_tests only
    $ python3 manage.py test rolabola # unit and integration tests only
    $ python3 manage.py rolabola.tests.GroupTest # unit and integrations tests  inside GroupTest
    $ python3 manage.py rolabola.tests.GroupTest.test_user_can_join_public_group # runs a specific test

If you're adding new features, please write tests for it so no one will break it futurely. If you're modifying existing features, make sure tests still pass **or** modify the tests to suit the new functionality.

## License

Code is licensed under the [AGPL](http://www.gnu.org/licenses/agpl-3.0.en.html), also available in this repo as `LICENSE.txt`.

## Contact

If you'd like to be in touch with this project, please do not hesitate in contacting Andre Siviero at `altsiviero at gmail dot com` and I'll be glad to answer you.
