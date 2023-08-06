import os
import pytest
import yaml

from playbooks.hostea.roles.hostea.files import hosteasetup


@pytest.fixture
def domain(pytestconfig):
    inventory = pytestconfig.getoption("--ansible-inventory")
    vars_dir = f'{inventory}/group_vars/all'
    return yaml.safe_load(open(vars_dir + '/domain.yml'))['domain']


@pytest.fixture
def gitea_hostname(domain):
    return f'gitea.{domain}'


@pytest.fixture
def woodpecker_hostname(domain):
    return f'woodpecker.{domain}'


@pytest.fixture
def certs(request):
    return request.session.infrastructure.certs()


@pytest.fixture
def password():
    # must match playbooks/hostea/inventory/host_vars/gitea-host/gitea.yml
    return "etquofEtseudett"


@pytest.fixture
def make_user(password):

    contexts = []

    def _make_user(forge, username):
        forge.authenticate(username="root", password=password)
        user = forge.users.get(username)
        if user:
            for project in user.projects:
                forge.projects.delete(username, project.project)

            forge.users.delete(username)
        email = f"{username}@example.com"
        user = forge.users.create(username, password, email)
        contexts.append((forge, username))
        return user

    yield _make_user

    for (forge, username) in contexts:
        if not forge.is_authenticated or not forge.is_admin:
            forge.authenticate(username="root", password=password)
        user = forge.users.get(username)
        if user:
            for project in user.projects:
                forge.projects.delete(username, project.project)
        forge.users.delete(username)


@pytest.fixture
def make_project(password):

    contexts = []

    def _make_project(forge, username, project, **data):
        forge.projects.delete(username, project)
        p = forge.projects.create(username, project, **data)
        contexts.append((forge, username, project))
        return p

    yield _make_project

    for (forge, username, project) in contexts:
        forge.authenticate(username="root", password=password)
        forge.projects.delete(username, project)


def test_gitea_project_create(gitea_hostname, make_user, password, certs):
    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    username = "testuser2"
    make_user(forge, username)
    forge.authenticate(username=username, password=password)

    forge.projects.delete(username, "testproject")
    assert forge.projects.get(username, "testproject") is None
    p = forge.projects.create(username, "testproject")
    assert p.project == "testproject"
    assert p.id == forge.projects.create(username, "testproject").id
    forges = list(forge.projects.list())
    forges_count = len(forges)
    assert forges and forges_count >= 1
    assert forge.projects.delete(username, "testproject") is True
    assert forge.projects.delete(username, "testproject") is False
    forges = list(forge.projects.list())
    assert len(forges) == forges_count - 1


def test_gitea_project_keys(gitea_hostname, make_user, password, make_project, certs, tmpdir):
    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    username = "testuser2"
    make_user(forge, username)
    forge.authenticate(username=username, password=password)
    p = make_project(forge, username, "testproject")

    keys = list(p.keys.list())
    assert not keys and len(keys) == 0

    title = "THE TITLE"
    read_only = False
    os.system(f"ssh-keygen -q -f {tmpdir}/key -N ''")
    key = open(f"{tmpdir}/key.pub").read().strip()

    k = p.keys.create(title, key, read_only)
    assert k == p.keys.create(title, key, read_only)
    assert k.title == title
    assert k.id == p.keys.get(k.id).id
    assert k == p.keys.get(k.id)
    keys = list(p.keys.list())
    assert keys and len(keys) == 1 and keys[0].id == k.id
    assert keys[0] == k
    assert p.keys.delete(k.id) is True
    assert not list(p.keys.list())
    assert p.keys.get(k.id) is None
    assert p.keys.delete(k.id) is False


def test_gitea_user_create_regular(gitea_hostname, password, certs):
    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    forge.authenticate(username="root", password=password)
    username = "testuser3"
    email = "testuser3@example.com"
    forge.users.delete(username)

    u = forge.users.create(username, password, email)
    assert u.url == forge.users.create(username, password, email).url
    assert any([x.username == username for x in forge.users.list()])
    forge.authenticate(username=username, password=password)
    assert forge.username == username
    assert forge.is_admin is False

    forge.authenticate(username="root", password=password)
    assert forge.users.delete(username) is True
    assert forge.users.get(username) is None
    assert forge.users.delete(username) is False


def test_gitea_user_get(gitea_hostname, password, certs):
    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    forge.authenticate(username="root", password=password)

    username1 = "testuser4"
    email1 = "testuser4@example.com"
    forge.users.delete(username1)
    u1 = forge.users.create(username1, password, email1)

    username2 = "testuser5"
    email2 = "testuser5@example.com"
    forge.users.delete(username2)
    u2 = forge.users.create(username2, password, email2)

    assert u1 != u2

    u1_view_admin = forge.users.get(username1)
    forge.authenticate(username=username1, password=password)
    u1_view_self = forge.users.get(username1)
    forge.authenticate(username=username2, password=password)
    u1_view_unpriv = forge.users.get(username1)
    assert u1_view_admin == u1_view_self == u1_view_unpriv

    forge.authenticate(username="root", password=password)
    assert forge.users.delete(username1) is True
    assert forge.users.delete(username2) is True


def test_gitea_user_projects(gitea_hostname, make_user, password, certs):
    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    username = "testuser6"
    user1 = make_user(forge, username)
    forge.authenticate(username=username, password=password)

    projects = list(user1.projects)
    assert not projects and len(projects) == 0

    p = forge.projects.create(username, "testproject")
    projects = list(user1.projects)
    assert projects and len(projects) == 1 and projects[0] == p

    assert forge.projects.delete(username, "testproject") is True
    projects = list(user1.projects)
    assert not projects and len(projects) == 0


def test_gitea_user_key(gitea_hostname, make_user, password, certs, tmpdir):
    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    username = "testuser7"
    user = make_user(forge, username)
    forge.authenticate(username=username, password=password)

    os.system(f"ssh-keygen -q -f {tmpdir}/key -N ''")
    key = open(f"{tmpdir}/key.pub").read().strip()

    user.delete_key("mykey")
    user.create_key("mykey", key)
    assert user.get_key("mykey")["key"] == key
    user.delete_key("mykey")


def test_gitea_user_application(gitea_hostname, password, certs):
    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    forge.authenticate(username="root", password=password)
    user = forge.users.get("root")

    appname = "testapp"
    appuri = "uri"
    user.delete_application(appname)
    app = user.create_application(appname, appuri)
    assert app["name"] == appname
    assert app["redirect_uris"] == [appuri]
    assert "client_id" in app
    assert "client_secret" in app
    app = user.get_application(appname)
    assert app is not None
    assert app == user.delete_application(appname)
    assert user.delete_application(appname) is None


def test_hostea_setup(gitea_hostname, woodpecker_hostname, password, certs, tmpdir):
    # Must be in woodpecker_admins at hostea/inventory/group_vars/gitea-service-group.yml
    username = "testuser8"
    userpassword = "thepassword123"
    project = "testproject"
    deploy = f"{tmpdir}/key"
    os.system(f"ssh-keygen -q -f {deploy} -N ''")

    hostea = hosteasetup.Hostea(
        certs=certs,
        gitea_hostname=gitea_hostname,
        admin_user="root",
        admin_password=password,
        user=username,
        password=userpassword,
        email=f"contact+{username}@hostea.org",
        project=project,
        woodpecker_hostname=woodpecker_hostname,
        deploy=deploy)

    hostea.destroy()

    for _ in range(2):
        hostea.setup()
        assert hostea.gitea.users.get(hostea.user) is not None
        assert hostea.gitea.projects.get(hostea.user, hostea.project) is not None
        assert hostea.woodpecker.enable_project(hostea.project) is False

    hostea.destroy()


def test_hostea_woodpecker(gitea_hostname, woodpecker_hostname, password, certs, tmpdir):
    #
    # Errors are not returned, they are in the logs
    # tests/run-tests.sh tests/ssh hostea gitea-host
    # sudo bash
    # cd /srv/woodpecker
    # docker-compose down
    # docker-compose up
    #
    # Must be in woodpecker_admins at hostea/inventory/group_vars/gitea-service-group.yml
    username = "testuser9"
    userpassword = "thepassword123"
    project = "testproject"
    deploy = f"{tmpdir}/key"
    os.system(f"ssh-keygen -q -f {deploy} -N ''")

    hostea = hosteasetup.Hostea(
        certs=certs,
        gitea_hostname=gitea_hostname,
        admin_user="root",
        admin_password=password,
        user=username,
        password=userpassword,
        email=f"contact+{username}@hostea.org",
        project=project,
        woodpecker_hostname=woodpecker_hostname,
        deploy=deploy)

    hostea.destroy()
    hostea.setup()

    assert hostea.woodpecker_add_deploy() is True

    assert hostea.woodpecker_enable_project() is False
    assert hostea.woodpecker_disable_project() is True
    assert hostea.woodpecker_disable_project() is False
    assert hostea.woodpecker_enable_project() is True

    assert hostea.woodpecker_disable_project() is True
    assert len(hostea.gitea_browser.revoke_application("woodpecker")) >= 1
    hostea.destroy()


def test_hostea_run(gitea_hostname, woodpecker_hostname, password, certs, tmpdir):
    username = "testuserc"
    userpassword = "thepassword123"
    project = "testproject"
    deploy = f"{tmpdir}/key"
    os.system(f"ssh-keygen -q -f {deploy} -N ''")

    hostea = hosteasetup.Hostea(
        certs=certs,
        gitea_hostname=gitea_hostname,
        admin_user="root",
        admin_password=password,
        user=username,
        password=userpassword,
        email=f"contact+{username}@hostea.org",
        project=project,
        woodpecker_hostname=woodpecker_hostname,
        deploy=deploy)

    hostea.destroy()
    hostea.setup()
    sha = hostea.update_project("playbooks/hostea/tests/hostea")
    logs = hostea.woodpecker.build_logs(project, sha, "deploy")
    assert 'Server Version:' in logs
    assert 'CONTAINER ID' in logs

    hostea.destroy()


def test_gitea_main(gitea_hostname, woodpecker_hostname, password, certs, tmpdir):
    # Must be in woodpecker_admins at hostea/inventory/group_vars/gitea-service-group.yml
    username = "testusera"
    userpassword = "thepassword123"
    project = "testproject"
    deploy = f"{tmpdir}/key"
    os.system(f"ssh-keygen -q -f {deploy} -N ''")

    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    forge.authenticate(username="root", password=password)
    forge.projects.delete(username, project)
    forge.users.delete(username)

    (gitea, woodpecker) = hosteasetup.main([
        '--certs', certs,
        '--deploy', deploy,
        gitea_hostname, "root", password,
        username, userpassword, "contact@hostea.org", project,
        woodpecker_hostname])
    assert gitea.users.get(username) is not None
    assert gitea.projects.get(username, project) is not None
    assert woodpecker.enable_project(project) is False

    assert woodpecker.disable_project(project) is True
    forge.projects.delete(username, project)
    forge.users.delete(username)
