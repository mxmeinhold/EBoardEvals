import subprocess
from functools import wraps

from flask import session

from eboardevals import _ldap
from eboardevals.ldap import ldap_is_eboard


def before_request(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        git_revision = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').rstrip()
        uuid = str(session["userinfo"].get("sub", ""))
        uid = str(session["userinfo"].get("preferred_username", ""))
        user_obj = _ldap.get_member(uid, uid=True)
        info = {
            "git_revision": git_revision,
            "uuid": uuid,
            "uid": uid,
            "user_obj": user_obj,
            "is_eboard": ldap_is_eboard(user_obj)
        }
        kwargs["info"] = info
        return func(*args, **kwargs)

    return wrapped_function
