#!/usr/local/bin/python3
#
# sonar-tools
# Copyright (C) 2019-2022 Olivier Korach
# mailto:olivier.korach AT gmail DOT com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""

    Exports all projects of a SonarQube platform

"""
import sys
import os
from sonar import env, projects, options
import sonar.utilities as util


def main():
    parser = util.set_common_args("Exports all projects of a SonarQube platform")
    parser.add_argument(
        "--exportTimeout",
        required=False,
        type=int,
        default=180,
        help="Maximum wait time for export",
    )
    args = util.parse_and_check_token(parser)
    util.check_environment(vars(args))
    sq = env.Environment(some_url=args.url, some_token=args.token)

    if sq.edition() in ("community", "developer") and sq.version(digits=2) < (9, 2):
        util.exit_fatal(
            "Can't export projects on Community and Developer Edition before 9.2, aborting...",
            options.ERR_UNSUPPORTED_OPERATION,
        )

    project_list = projects.search(sq)
    nb_projects = len(project_list)
    util.logger.info("%d projects to export", nb_projects)
    statuses = {}
    exports = []

    for key, p in project_list.items():
        try:
            dump = p.export_zip(timeout=args.exportTimeout)
        except options.UnsupportedOperation as e:
            util.exit_fatal(e.message, options.ERR_UNSUPPORTED_OPERATION)

        status = dump["status"]
        if status in statuses:
            statuses[status] += 1
        else:
            statuses[status] = 1

        data = {"key": key, "status": status}
        if status == "SUCCESS":
            data["file"] = os.path.basename(dump["file"])
            data["path"] = dump["file"]

        exports.append(data)
        util.logger.info(
            "%d/%d exports (%d%%) - Latest: %s - %s",
            len(exports),
            nb_projects,
            int(len(exports) * 100 / nb_projects),
            key,
            status,
        )

        summary = ""
        for k, v in statuses.items():
            summary += f"{k}:{v}, "
        util.logger.info("%s", summary[:-2])

    print(
        util.json_dump(
            {
                "sonarqube_environment": {
                    "version": sq.version(digits=2, as_string=True),
                    "plugins": sq.plugins(),
                },
                "project_exports": exports,
            }
        )
    )
    util.logger.info("%s", summary)
    sys.exit(0)


if __name__ == "__main__":
    main()
