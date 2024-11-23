#!/usr/bin/python
# coding: utf-8 -*-

# Copyright (c) 2021, Sagi Shnaidman <sshnaidm@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
module: ocp_resolve
short_description: Get a specific OCP image from given data
author: Sagi Shnaidman (@sshnaidm)
description:
  - Find an OCP image from given data and return it
options:
  full_tag:
    description:
      - Full OCP tag (4.12.0-0.nightly-2023-03-09-142909, etc)
    type: str
  release:
    description:
      - OCP release type. Choose from "ci", "nightly", "stable", "candidate", "dev-preview"
    type: str
    choices:
      - ci
      - nightly
      - stable
      - candidate
      - dev-preview
    default: stable
  tag:
    description:
      - OCP tag (4.12, 4.11, etc)
    type: str
  debug:
    description:
      - Enable debug mode
    type: bool
    default: false
requirements:
  - requests
'''

RETURN = '''
image:
    description: Image of OCP in quay.io
    returned: always
    type: str
    sample: quay.io/openshift-release-dev/ocp-release@sha256:d9729e....
'''

EXAMPLES = '''
# Resolve various OCP versions
- name: Get OCP image
  ocp_resolve:
    tag: 4.15
    debug: true

- name: Get OCP image
  ocp_resolve:
    tag: 4.17
    release: ci
    debug: true

- name: Get OCP image
  ocp_resolve:
    tag: 4.16
    release: dev-preview

- name: Get OCP image
  ocp_resolve:
    tag: 4.15
    release: candidate

- name: Get OCP
  ocp_resolve:
    full_tag: 4.16.0-0.nightly-2024-06-23-120416
'''

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible.module_utils.basic import missing_required_lib  # noqa: E402

import traceback  # noqa: E402

try:
    import requests  # noqa: E402
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_REQUESTS = True
    REQUESTS_IMPORT_ERROR = None


API_URL = "https://amd64.ocp.releases.ci.openshift.org/api/v1/releasestream/%s.0-0.%s/latest"
STABLE_URL = "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable-%s/"
CANDIDATE_URL = "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/candidate-%s/"
DEV_PREVIEW_URL = "https://mirror.openshift.com/pub/openshift-v4/clients/ocp-dev-preview/candidate-%s/"


def get_url(url, module):
    response = requests.get(url, verify=False, timeout=120)
    if not response.ok:
        module.fail_json(msg=f"Failed to get {url}: {response.text}, HTTP status: {response.status_code}")
    return response


def resolve_tag(module, tag, release, full_tag, debug=False):
    if full_tag:
        if debug:
            module.log(f"OCP-RESOLVE-LOG: Using full tag {full_tag}")
        if "ci" in full_tag or "nightly" in full_tag:
            if debug:
                module.log(
                    f"Using version registry.ci.openshift.org/ocp/release:{full_tag}")
            return f"registry.ci.openshift.org/ocp/release:{full_tag}"
        if not full_tag.endswith("-x86_64"):
            if debug:
                module.log(f"OCP-RESOLVE-LOG: Adding -x86_64 to {full_tag}")
            full_tag += "-x86_64"
        if debug:
            module.log(
                f"Using version quay.io/openshift-release-dev/ocp-release:{full_tag}")
        return f"quay.io/openshift-release-dev/ocp-release:{full_tag}"

    if release in ("ci", "nightly"):
        if debug:
            module.log(f"OCP-RESOLVE-LOG: Finding {release} release for tag {tag}")
        url = API_URL % (tag, release)
        if debug:
            module.log(f"OCP-RESOLVE-LOG: Getting URL {url}")
        response = requests.get(url)
        try:
            data = response.json()
        except Exception:
            module.fail_json(
                msg=f"Failed to parse {url} as JSON: {response.text}")
        if debug:
            module.log(f"OCP-RESOLVE-LOG: Using {release} version {data['pullSpec']}")
        return data["pullSpec"]

    if release in ("stable", "candidate", "dev-preview"):
        if debug:
            module.log(f"OCP-RESOLVE-LOG: Finding {release} release for tag {tag}")
        if release == "stable":
            release_url = requests.compat.urljoin(
                STABLE_URL % tag, "release.txt")
        elif release == "candidate":
            release_url = requests.compat.urljoin(
                CANDIDATE_URL % tag, "release.txt")
        elif release == "dev-preview":
            release_url = requests.compat.urljoin(
                DEV_PREVIEW_URL % tag, "release.txt")
        if debug:
            module.log(f"OCP-RESOLVE-LOG: Getting URL {release_url}")
        url_data = get_url(release_url, module)
        if "Pull From: " in url_data.text:
            for line in url_data.text.splitlines():
                if "Pull From: " in line:
                    if debug:
                        module.log(f"OCP-RESOLVE-LOG: Found {release} in line {line.strip()}")
                    result = line.split("Pull From: ")[1].strip()
                    if debug:
                        module.log(f"OCP-RESOLVE-LOG: Using {release} version {result}")
                    return result
        module.fail_json(
            msg=f"Failed to parse {release} release.txt: {release_url}")
    if not tag and not release and not full_tag:
        module.fail_json(msg="No tag or release or full_tag specified")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            tag=dict(type='str'),
            release=dict(type='str', choices=["ci", "nightly", "stable", "candidate", "dev-preview"], default="stable"),
            full_tag=dict(type='str'),
            debug=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )

    if not HAS_REQUESTS:
        module.fail_json(
            msg=missing_required_lib('requests'),
            exception=REQUESTS_IMPORT_ERROR)

    tag = module.params['tag']
    release = module.params['release']
    full_tag = module.params['full_tag']
    result = resolve_tag(module, tag, release, full_tag,
                         module.params['debug'])

    results = {
        "changed": False,
        "image": result,
    }
    module.exit_json(**results)


if __name__ == '__main__':
    main()
