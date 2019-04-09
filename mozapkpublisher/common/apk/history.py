import logging

logger = logging.getLogger(__name__)


_MAJOR_FIREFOX_VERSIONS_PER_ARCHITECTURE_AND_API_LEVEL = {
    'arm64-v8a': {      # Bug 1368484
        21: {
            # XXX AArch64 first shipped in Nightly 66, and then arrived in beta in 67.
            # It's not on release yet. Logic is down below.
            'first_firefox_version': 66,
        },
    },
    'armeabi-v7a': {    # Bug 618789
        9: {
            'first_firefox_version': 32,
            'last_firefox_version': 47,     # Bug 1220184
        },
        11: {
            'first_firefox_version': 37,
            'last_firefox_version': 45,     # Bug 1155801
        },
        15: {
            'first_firefox_version': 46,    # Bug 1220184
            'last_firefox_version': 55,     # Bug 1316462
        },
        16: {
            'first_firefox_version': 56,    # Bug 1316462
        },
    },
    'x86': {    # Bug 757909
        9: {
            'first_firefox_version': 32,
            'last_firefox_version': 36,     # Bug 1220184 - No overlap with API-11 (unlike ARM)
        },
        11: {
            'first_firefox_version': 37,
            'last_firefox_version': 45,     # Bug 1155801
        },
        15: {
            'first_firefox_version': 46,    # Bug 1220184
            'last_firefox_version': 55,     # Bug 1316462
        },
        16: {
            'first_firefox_version': 56,    # Bug 1316462
        },
    },
    'x86_64': {     # Bug 1505538
        21: {
            'first_firefox_version': 67,    # Bug 1368484
        },
    },
}


def get_expected_combos(firefox_version, package_name):
    combos = set()
    for architecture in _MAJOR_FIREFOX_VERSIONS_PER_ARCHITECTURE_AND_API_LEVEL:
        api_levels = get_expected_api_levels(firefox_version, architecture, package_name)

        for api_level in api_levels:
            combos.add((architecture, api_level))

    if not combos:
        raise ValueError('No combos found for Firefox version {}. Current rules: {2}'.format(
            firefox_version, _MAJOR_FIREFOX_VERSIONS_PER_ARCHITECTURE_AND_API_LEVEL
        ))

    logger.debug(
        'Expected to find these combos for Firefox {}: {}'.format(
            firefox_version, craft_combos_pretty_names(combos)
        )
    )
    return combos


def get_expected_api_levels(firefox_version, architecture='armeabi-v7a', package_name='org.mozilla.firefox'):
    return [
        api_level
        for api_level, range_dict in _MAJOR_FIREFOX_VERSIONS_PER_ARCHITECTURE_AND_API_LEVEL[architecture].items()
        if (
            _is_firefox_version_in_range(firefox_version, range_dict) and
            # XXX arm64-v8a (aka AArch64) is not planned to ride trains regularly.
            # It's currently expected on nightly and beta, for now.
            (
                architecture != 'arm64-v8a' or
                (
                    architecture == 'arm64-v8a' and (
                        package_name == 'org.mozilla.fennec_aurora' or
                        package_name == 'org.mozilla.firefox_beta' and get_firefox_major_version_number(firefox_version) >= 67
                    )
                )
            )
        )
    ]


def _is_firefox_version_in_range(firefox_version, range_dict):
    first_firefox_version = range_dict['first_firefox_version']
    current_major_version = get_firefox_major_version_number(firefox_version)
    if current_major_version < first_firefox_version:
        return False

    last_firefox_version = range_dict.get('last_firefox_version', None)
    if last_firefox_version is not None and current_major_version > last_firefox_version:
        return False

    return True


def get_firefox_major_version_number(version):
    return int(version.split('.')[0])


def craft_combos_pretty_names(combos):
    return ', '.join([
        '{} API {}+'.format(*combo)
        for combo in combos
    ])
