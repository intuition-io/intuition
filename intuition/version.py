BANNER = """
intuition {version}
Released under APACHE 2.0 Licence.
""".strip()

VERSION = ('0', '4', '1', 'dev')


def pretty_version():
    return BANNER.format(version='.'.join(VERSION))
