BANNER = """
neuronquant {version}
Released under DWTFYW
""".strip()

VERSION = ('0', '0', '1', 'dev')


def pretty_version():
    return BANNER.format(version='.'.join(VERSION))
