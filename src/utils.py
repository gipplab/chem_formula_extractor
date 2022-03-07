from fake_useragent import FakeUserAgent
import requests as r


def create_user_agent() -> str:
    """Creates fake user agent string.

    Returns:
        str: User agent string.
    """
    return str(FakeUserAgent().random)


def create_session() -> r.Session:
    """Creates a requests session with random user-agent.

    Returns:
        r.Session: Requests session object.
    """
    user_agent = create_user_agent()
    session = r.Session()
    session.headers.update({"User-Agent": user_agent})
    return session

if __name__ == "__main__":
    user_agent = create_user_agent()
    print(user_agent)
