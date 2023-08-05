# Copyright 2021 Red Hat, inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import time
from dateutil.parser import isoparse

import prettytable
import json
import yaml


class BaseFormatter:

    def __init__(self, data_type):
        self.data_type = data_type

    def __call__(self, data):
        """Format data according to the type of data being displayed."""
        try:
            return getattr(self, 'format' + self.data_type)(data)
        except Exception:
            raise Exception('Unsupported data type "%s"' % self.data_type)

    def formatBuildNodes(self, data):
        raise NotImplementedError

    def formatAutoholdQueries(self, data):
        raise NotImplementedError

    def formatAutoholdQuery(self, data):
        raise NotImplementedError

    def formatJobResource(self, data):
        raise NotImplementedError

    def formatArtifacts(self, data):
        raise NotImplementedError

    def formatInventory(self, data):
        raise NotImplementedError

    def formatBuild(self, data):
        raise NotImplementedError

    def formatBuildSet(self, data):
        raise NotImplementedError

    def formatBuilds(self, data):
        raise NotImplementedError

    def formatBuildSets(self, data):
        raise NotImplementedError


class JSONFormatter(BaseFormatter):
    def __call__(self, data) -> str:
        # Simply format the raw dictionary returned by the API
        return json.dumps(data, sort_keys=True, indent=2)


class PrettyTableFormatter(BaseFormatter):
    """Format Zuul data in a nice human-readable way for the CLI."""

    def formatAutoholdQuery(self, data) -> str:
        text = ""
        text += "ID: %s\n" % data.get('id', 'N/A')
        text += "Tenant: %s\n" % data.get('tenant', 'N/A')
        text += "Project: %s\n" % data.get('project', 'N/A')
        text += "Job: %s\n" % data.get('job', 'N/A')
        text += "Ref Filter: %s\n" % data.get('ref_filter', 'N/A')
        text += "Max Count: %s\n" % (data.get('max_count', None) or
                                     data.get('count', 'N/A'))
        text += "Current Count: %s\n" % data.get('current_count', 'N/A')
        text += "Node Expiration: %s\n" % (
            data.get('node_expiration', None) or
            data.get('node_hold_expiration', 'N/A')
        )
        text += "Request Expiration: %s\n" % (
            data.get('expired', None) and time.ctime(data['expired']) or
            'N/A'
        )
        text += "Reason: %s\n" % data.get('reason', 'N/A')
        text += "Held Nodes:\n"
        for buildnodes in data.get('nodes', []):
            text += self.formatBuildNodes(buildnodes)
        return text

    def formatBuildNodes(self, data) -> str:
        table = prettytable.PrettyTable(field_names=['Build ID', 'Node ID'])
        for node in data.get('nodes', []):
            table.add_row([data.get('build', 'N/A'), node])
        return str(table)

    def formatAutoholdQueries(self, data) -> str:
        table = prettytable.PrettyTable(
            field_names=[
                'ID', 'Tenant', 'Project', 'Job', 'Ref Filter',
                'Max Count', 'Reason'
            ])

        for request in data:
            table.add_row([
                request.get('id', 'N/A'),
                request.get('tenant', 'N/A'),
                request.get('project', 'N/A'),
                request.get('job', 'N/A'),
                request.get('ref_filter', 'N/A'),
                request.get('max_count', None) or request.get('count', 'N/A'),
                request.get('reason', 'N/A'),
            ])
        return str(table)

    def formatBuild(self, data) -> str:
        output = ''
        # This is based on the web UI
        output += 'UUID: %s\n' % data.get('uuid', 'N/A')
        output += '=' * len('UUID: %s' % data.get('uuid', 'N/A')) + '\n'
        output += 'Result: %s\n' % data.get('result', 'N/A')
        output += 'Pipeline: %s\n' % data.get('pipeline', 'N/A')
        output += 'Project: %s\n' % data.get('project', 'N/A')
        output += 'Job: %s\n' % data.get('job_name', 'N/A')
        if data.get('newrev'):
            output += 'Ref: %s\n' % data.get('ref', 'N/A')
            output += 'New Rev: %s\n' % data['newrev']
        if data.get('change') and data.get('patchset'):
            output += 'Change: %s\n' % (str(data['change']) + ',' +
                                        str(data['patchset']))
        output += 'Branch: %s\n' % data.get('branch', 'N/A')
        output += 'Ref URL: %s\n' % data.get('ref_url', 'N/A')
        output += 'Event ID: %s\n' % data.get('event_id', 'N/A')
        output += 'Buildset ID: %s\n' % data.get('buildset',
                                                 {}).get('uuid', 'N/A')
        output += 'Start time: %s\n' % (
            data.get('start_time') and
            isoparse(data['start_time']) or
            'N/A'
        )
        output += 'End time: %s\n' % (
            data.get('end_time') and
            isoparse(data['end_time']) or
            'N/A'
        )
        output += 'Duration: %s\n' % data.get('duration', 'N/A')
        output += 'Voting: %s\n' % (data.get('voting') and 'Yes' or 'No')
        output += 'Log URL: %s\n' % data.get('log_url', 'N/A')
        output += 'Node: %s\n' % data.get('node_name', 'N/A')

        provides = data.get('provides', [])
        if provides:
            output += 'Provides:\n'
            for resource in provides:
                output += '- %s\n' % self.formatJobResource(resource)
        if data.get('final', None) is not None:
            output += 'Final: %s\n' % (data['final'] and 'Yes' or 'No')
        else:
            output += 'Final: N/A\n'
        if data.get('held', None) is not None:
            output += 'Held: %s' % (data['held'] and 'Yes' or 'No')
        else:
            output += 'Held: N/A'

        return output

    def formatArtifacts(self, data) -> str:
        table = prettytable.PrettyTable(
            field_names=['name', 'url']
        )
        for artifact in data:
            table.add_row([artifact.get('name', 'N/A'),
                           artifact.get('url', 'N/A')])
        return str(table)

    def formatInventory(self, data) -> str:
        return yaml.dump(data, default_flow_style=False)

    def formatBuildSet(self, data) -> str:
        # This is based on the web UI
        output = ''
        output += 'UUID: %s\n' % data.get('uuid', 'N/A')
        output += '=' * len('UUID: %s' % data.get('uuid', 'N/A')) + '\n'
        output += 'Result: %s\n' % data.get('result', 'N/A')
        if data.get('newrev'):
            output += 'Ref: %s\n' % data.get('ref', 'N/A')
            output += 'New Rev: %s\n' % data['newrev']
        if data.get('change') and data.get('patchset'):
            output += 'Change: %s\n' % (str(data['change']) + ',' +
                                        str(data['patchset']))
        output += 'Project: %s\n' % data.get('project', 'N/A')
        output += 'Branch: %s\n' % data.get('branch', 'N/A')
        output += 'Pipeline: %s\n' % data.get('pipeline', 'N/A')
        output += 'Event ID: %s\n' % data.get('event_id', 'N/A')
        output += 'Message: %s' % data.get('message', 'N/A')
        return output

    def formatBuildSets(self, data) -> str:
        table = prettytable.PrettyTable(
            field_names=[
                'ID', 'Project', 'Branch', 'Pipeline', 'Change or Ref',
                'Result', 'Event ID'
            ]
        )
        for buildset in data:
            if buildset.get('change') and buildset.get('patchset'):
                change = (
                    str(buildset['change']) + ',' +
                    str(buildset['patchset'])
                )
            else:
                change = buildset.get('ref', 'N/A')
            table.add_row([
                buildset.get('uuid', 'N/A'),
                buildset.get('project', 'N/A'),
                buildset.get('branch', 'N/A'),
                buildset.get('pipeline', 'N/A'),
                change,
                buildset.get('result', 'N/A'),
                buildset.get('event_id', 'N/A')
            ])
        return str(table)

    def formatBuilds(self, data) -> str:
        table = prettytable.PrettyTable(
            field_names=[
                'ID', 'Job', 'Project', 'Branch', 'Pipeline', 'Change or Ref',
                'Duration (s)', 'Start time', 'Result', 'Event ID'
            ]
        )
        for build in data:
            if build.get('change') and build.get('patchset'):
                change = str(build['change']) + ',' + str(build['patchset'])
            else:
                change = build.get('ref', 'N/A')
            start_time = (
                build.get('start_time') and
                isoparse(build['start_time']) or
                'N/A'
            )
            table.add_row([
                build.get('uuid', 'N/A'),
                build.get('job_name', 'N/A'),
                build.get('project', 'N/A'),
                build.get('branch', 'N/A'),
                build.get('pipeline', 'N/A'),
                change,
                build.get('duration', 'N/A'),
                start_time,
                build.get('result', 'N/A'),
                build.get('event_id', 'N/A')
            ])
        return str(table)

    def formatJobResource(self, data) -> str:
        return data.get('name', 'N/A')
