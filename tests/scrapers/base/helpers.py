from infrastructure.http.policies.http import HttpPolicy


def patched_article_init(self, *_args, **kwargs):
    """Replace ArticleScraperBase.__init__ to avoid HTTP setup."""
    pass


def make_policy() -> HttpPolicy:
    return HttpPolicy(retries=0, timeout=10)


