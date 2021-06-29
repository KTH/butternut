__author__ = 'tinglev@kth.se'

import re
import modules.helpers as helpers
import modules.docker as docker


def run():
    response = 'Containers running on management are:```'
    response += helpers.create_header_row([('Image', 80), ('Status', 0)])
    for container in docker.get_local_containers():
        pattern = r"<Image: '(.+)'>"
        image_re = re.search(pattern, str(container.image))
        if image_re:
            response += helpers.create_row([(image_re.group(1), 80), (container.status, 0)])
    return response + '```'
