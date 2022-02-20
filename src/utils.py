from fake_useragent import FakeUserAgent
import requests as r


def create_user_agent() -> str:
    return str(FakeUserAgent().random)


def create_session() -> r.Session:
    user_agent = create_user_agent()
    session = r.Session()
    session.headers.update({"User-Agent": user_agent})
    return session
