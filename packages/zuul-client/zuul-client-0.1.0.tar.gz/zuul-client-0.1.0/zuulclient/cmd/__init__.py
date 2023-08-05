# Copyright 2020 Red Hat, inc
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

import argparse
import configparser
import logging
import os
from pathlib import Path
import shutil
import sys
import tempfile
import textwrap

from zuulclient.api import ZuulRESTClient
from zuulclient.utils import get_default
from zuulclient.utils import encrypt_with_openssl
from zuulclient.utils import formatters


_HOME = Path(os.path.expandvars('$HOME'))
_XDG_CONFIG_HOME = Path(os.environ.get(
    'XDG_CONFIG_HOME',
    _HOME / '.config'))


class ArgumentException(Exception):
    pass


class ZuulClient():
    app_name = 'zuul-client'
    app_description = 'Zuul User CLI'
    log = logging.getLogger("zuul-client")
    default_config_locations = [
        _XDG_CONFIG_HOME / 'zuul' / 'client.conf',
        _HOME / '.zuul.conf'
    ]

    def __init__(self):
        self.args = None
        self.config = None

    def _get_version(self):
        from zuulclient.version import version_info
        return "Zuul-client version: %s" % version_info.release_string()

    def createParser(self):
        parser = argparse.ArgumentParser(
            description=self.app_description,
            formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-c', dest='config',
                            help='specify the config file')
        parser.add_argument('--version', dest='version', action='version',
                            version=self._get_version(),
                            help='show zuul version')
        parser.add_argument('-v', dest='verbose', action='store_true',
                            help='verbose output')
        parser.add_argument('--auth-token', dest='auth_token',
                            required=False,
                            default=None,
                            help='Authentication Token, required by '
                                 'admin commands')
        parser.add_argument('--zuul-url', dest='zuul_url',
                            required=False,
                            default=None,
                            help='Zuul base URL, needed if using the '
                                 'client without a configuration file')
        parser.add_argument('--use-config', dest='zuul_config',
                            required=False,
                            default=None,
                            help='A predefined configuration in the '
                                 'zuul-client configuration file')
        parser.add_argument('--insecure', dest='verify_ssl',
                            required=False,
                            action='store_false',
                            help='Do not verify SSL connection to Zuul '
                                 '(Defaults to False)')
        parser.add_argument('--format', choices=['JSON', 'text'],
                            default='text', required=False,
                            help='The output format, when applicable')
        self.createCommandParsers(parser)
        return parser

    def createCommandParsers(self, parser):
        subparsers = parser.add_subparsers(title='commands',
                                           description='valid commands',
                                           help='additional help')
        self.add_autohold_subparser(subparsers)
        self.add_autohold_delete_subparser(subparsers)
        self.add_autohold_info_subparser(subparsers)
        self.add_autohold_list_subparser(subparsers)
        self.add_enqueue_subparser(subparsers)
        self.add_enqueue_ref_subparser(subparsers)
        self.add_dequeue_subparser(subparsers)
        self.add_promote_subparser(subparsers)
        self.add_encrypt_subparser(subparsers)
        self.add_builds_list_subparser(subparsers)
        self.add_build_info_subparser(subparsers)

        return subparsers

    def parseArguments(self, args=None):
        self.parser = self.createParser()
        self.args = self.parser.parse_args(args)
        if (
            (self.args.zuul_url and self.args.zuul_config) or
            (not self.args.zuul_url and not self.args.zuul_config)
        ):
            raise ArgumentException(
                'Either specify --zuul-url or use a config file')
        if not getattr(self.args, 'func', None):
            self.parser.print_help()
            sys.exit(1)
        if self.args.func == self.enqueue_ref:
            # if oldrev or newrev is set, ensure they're not the same
            if (self.args.oldrev is not None) or \
               (self.args.newrev is not None):
                if self.args.oldrev == self.args.newrev:
                    raise ArgumentException(
                        "The old and new revisions must not be the same.")
            # if they're not set, we pad them out to zero
            if self.args.oldrev is None:
                self.args.oldrev = '0000000000000000000000000000000000000000'
            if self.args.newrev is None:
                self.args.newrev = '0000000000000000000000000000000000000000'
        if self.args.func == self.dequeue:
            if self.args.change is None and self.args.ref is None:
                raise ArgumentException("Change or ref needed.")
            if self.args.change is not None and self.args.ref is not None:
                raise ArgumentException(
                    "The 'change' and 'ref' arguments are mutually exclusive.")

    @property
    def formatter(self):
        if self.args.format == 'JSON':
            return formatters.JSONFormatter
        elif self.args.format == 'text':
            return formatters.PrettyTableFormatter
        else:
            raise Exception('Unsupported formatter: %s' % self.args.format)

    def readConfig(self):
        safe_env = {
            k: v for k, v in os.environ.items()
            if k.startswith('ZUUL_')
        }
        self.config = configparser.ConfigParser(safe_env)
        if self.args.config:
            locations = [self.args.config]
        else:
            locations = self.default_config_locations
        for fp in locations:
            if os.path.exists(os.path.expanduser(fp)):
                self.config.read(os.path.expanduser(fp))
                return
        raise ArgumentException(
            "Unable to locate config "
            "file in %s" % ', '.join([x.as_posix() for x in locations]))

    def setup_logging(self):
        config_args = dict(
            format='%(levelname)-8s - %(message)s'
        )
        if self.args.verbose:
            config_args['level'] = logging.DEBUG
        else:
            config_args['level'] = logging.ERROR
        # set logging across all components (urllib etc)
        logging.basicConfig(**config_args)
        if self.args.zuul_config and\
           self.args.zuul_config in self.config.sections():
            zuul_conf = self.args.zuul_config
            log_file = get_default(self.config,
                                   zuul_conf, 'log_file', None)
            if log_file is not None:
                fh = logging.FileHandler(log_file)
                f_loglevel = get_default(self.config,
                                         zuul_conf, 'log_level', 'INFO')
                fh.setLevel(getattr(logging, f_loglevel, 'INFO'))
                f_formatter = logging.Formatter(
                    fmt='%(asctime)s %(name)s %(levelname)-8s - %(message)s',
                    datefmt='%x %X'
                )
                fh.setFormatter(f_formatter)
                self.log.addHandler(fh)

    def _main(self, args=None):
        # TODO make func return specific return codes
        try:
            self.parseArguments(args)
            if not self.args.zuul_url:
                self.readConfig()
            self.setup_logging()
            ret = self.args.func()
        except ArgumentException:
            if self.args.func:
                name = self.args.func.__name__
                parser = getattr(self, 'cmd_' + name, self.parser)
            else:
                parser = self.parser
            parser.print_help()
            print()
            raise
        if ret:
            self.log.info('Command %s completed '
                          'successfully' % self.args.func.__name__)
            return 0
        else:
            self.log.error('Command %s completed '
                           'with error(s)' % self.args.func.__name__)
            return 1

    def main(self):
        try:
            sys.exit(self._main())
        except Exception as e:
            self.log.exception(
                'Failed with the following exception: %s ' % e
            )
            sys.exit(1)

    def _check_tenant_scope(self, client):
        tenant_scope = client.info.get("tenant", None)
        tenant = self.tenant()
        if tenant != "":
            if tenant_scope is not None and tenant_scope != tenant:
                raise ArgumentException(
                    "Error: Zuul API URL %s is "
                    'scoped to tenant "%s"' % (client.base_url, tenant_scope)
                )
        else:
            if tenant_scope is None:
                raise ArgumentException(
                    "Error: the --tenant argument or the 'tenant' "
                    "field in the configuration file is required"
                )

    def add_autohold_subparser(self, subparsers):
        cmd_autohold = subparsers.add_parser(
            'autohold', help='hold nodes for failed job')
        cmd_autohold.add_argument('--tenant', help='tenant name',
                                  required=False, default='')
        cmd_autohold.add_argument('--project', help='project name',
                                  required=True)
        cmd_autohold.add_argument('--job', help='job name',
                                  required=True)
        cmd_autohold.add_argument('--change',
                                  help='specific change to hold nodes for',
                                  required=False, default='')
        cmd_autohold.add_argument('--ref', help='git ref to hold nodes for',
                                  required=False, default='')
        cmd_autohold.add_argument('--reason', help='reason for the hold',
                                  required=True)
        cmd_autohold.add_argument('--count',
                                  help='number of job runs (default: 1)',
                                  required=False, type=int, default=1)
        cmd_autohold.add_argument(
            '--node-hold-expiration',
            help=('how long in seconds should the node set be in HOLD status '
                  '(default: scheduler\'s default_hold_expiration value)'),
            required=False, type=int)
        cmd_autohold.set_defaults(func=self.autohold)
        self.cmd_autohold = cmd_autohold

    def autohold(self):
        if self.args.change and self.args.ref:
            raise Exception(
                "Change and ref can't be both used for the same request")
        if "," in self.args.change:
            raise Exception("Error: change argument can not contain any ','")

        node_hold_expiration = self.args.node_hold_expiration
        client = self.get_client()
        self._check_tenant_scope(client)
        kwargs = dict(
            tenant=self.tenant(),
            project=self.args.project,
            job=self.args.job,
            change=self.args.change,
            ref=self.args.ref,
            reason=self.args.reason,
            count=self.args.count,
            node_hold_expiration=node_hold_expiration)
        self.log.info('Invoking autohold with arguments: %s' % kwargs)
        r = client.autohold(**kwargs)
        return r

    def add_autohold_delete_subparser(self, subparsers):
        cmd_autohold_delete = subparsers.add_parser(
            'autohold-delete', help='delete autohold request')
        cmd_autohold_delete.set_defaults(func=self.autohold_delete)
        cmd_autohold_delete.add_argument('--tenant', help='tenant name',
                                         required=False, default='')
        cmd_autohold_delete.add_argument('id', metavar='REQUEST_ID',
                                         help='the hold request ID')
        self.cmd_autohold_delete = cmd_autohold_delete

    def autohold_delete(self):
        client = self.get_client()
        self._check_tenant_scope(client)
        kwargs = dict(
            id=self.args.id,
            tenant=self.tenant()
        )
        self.log.info('Invoking autohold-delete with arguments: %s' % kwargs)
        return client.autohold_delete(**kwargs)

    def add_autohold_info_subparser(self, subparsers):
        cmd_autohold_info = subparsers.add_parser(
            'autohold-info', help='retrieve autohold request detailed info')
        cmd_autohold_info.set_defaults(func=self.autohold_info)
        cmd_autohold_info.add_argument('--tenant', help='tenant name',
                                       required=False, default='')
        cmd_autohold_info.add_argument('id', metavar='REQUEST_ID',
                                       help='the hold request ID')
        self.cmd_autohold_info = cmd_autohold_info

    def autohold_info(self):
        client = self.get_client()
        self._check_tenant_scope(client)
        request = client.autohold_info(self.args.id, self.tenant())

        if not request:
            print("Autohold request not found")
            return False

        formatted_result = self.formatter('AutoholdQuery')(request)
        print(formatted_result)

        return True

    def add_autohold_list_subparser(self, subparsers):
        cmd_autohold_list = subparsers.add_parser(
            'autohold-list', help='list autohold requests')
        cmd_autohold_list.add_argument('--tenant', help='tenant name',
                                       required=False, default='')
        cmd_autohold_list.set_defaults(func=self.autohold_list)
        self.cmd_autohold_list = cmd_autohold_list

    def autohold_list(self):
        client = self.get_client()
        self._check_tenant_scope(client)
        requests = client.autohold_list(tenant=self.tenant())

        if not requests:
            print("No autohold requests found")
            return True

        formatted_result = self.formatter('AutoholdQueries')(requests)
        print(formatted_result)

        return True

    def add_enqueue_subparser(self, subparsers):
        cmd_enqueue = subparsers.add_parser('enqueue', help='enqueue a change')
        cmd_enqueue.add_argument('--tenant', help='tenant name',
                                 required=False, default='')
        cmd_enqueue.add_argument('--pipeline', help='pipeline name',
                                 required=True)
        cmd_enqueue.add_argument('--project', help='project name',
                                 required=True)
        cmd_enqueue.add_argument('--change', help='change id',
                                 required=True)
        cmd_enqueue.set_defaults(func=self.enqueue)
        self.cmd_enqueue = cmd_enqueue

    def enqueue(self):
        client = self.get_client()
        self._check_tenant_scope(client)
        kwargs = dict(
            tenant=self.tenant(),
            pipeline=self.args.pipeline,
            project=self.args.project,
            change=self.args.change
        )
        self.log.info('Invoking enqueue with arguments: %s' % kwargs)
        r = client.enqueue(**kwargs)
        return r

    def add_enqueue_ref_subparser(self, subparsers):
        cmd_enqueue_ref = subparsers.add_parser(
            'enqueue-ref', help='enqueue a ref',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''\
            Submit a trigger event

            Directly enqueue a trigger event.  This is usually used
            to manually "replay" a trigger received from an external
            source such as gerrit.'''))
        cmd_enqueue_ref.add_argument('--tenant', help='tenant name',
                                     required=False, default='')
        cmd_enqueue_ref.add_argument('--pipeline', help='pipeline name',
                                     required=True)
        cmd_enqueue_ref.add_argument('--project', help='project name',
                                     required=True)
        cmd_enqueue_ref.add_argument('--ref', help='ref name',
                                     required=True)
        cmd_enqueue_ref.add_argument(
            '--oldrev', help='old revision', default=None)
        cmd_enqueue_ref.add_argument(
            '--newrev', help='new revision', default=None)
        cmd_enqueue_ref.set_defaults(func=self.enqueue_ref)
        self.cmd_enqueue_ref = cmd_enqueue_ref

    def enqueue_ref(self):
        client = self.get_client()
        self._check_tenant_scope(client)
        kwargs = dict(
            tenant=self.tenant(),
            pipeline=self.args.pipeline,
            project=self.args.project,
            ref=self.args.ref,
            oldrev=self.args.oldrev,
            newrev=self.args.newrev
        )
        self.log.info('Invoking enqueue-ref with arguments: %s' % kwargs)
        r = client.enqueue_ref(**kwargs)
        return r

    def add_dequeue_subparser(self, subparsers):
        cmd_dequeue = subparsers.add_parser('dequeue',
                                            help='dequeue a buildset by its '
                                                 'change or ref')
        cmd_dequeue.add_argument('--tenant', help='tenant name',
                                 required=False, default='')
        cmd_dequeue.add_argument('--pipeline', help='pipeline name',
                                 required=True)
        cmd_dequeue.add_argument('--project', help='project name',
                                 required=True)
        cmd_dequeue.add_argument('--change', help='change id',
                                 default=None)
        cmd_dequeue.add_argument('--ref', help='ref name',
                                 default=None)
        cmd_dequeue.set_defaults(func=self.dequeue)
        self.cmd_dequeue = cmd_dequeue

    def dequeue(self):
        client = self.get_client()
        self._check_tenant_scope(client)
        kwargs = dict(
            tenant=self.tenant(),
            pipeline=self.args.pipeline,
            project=self.args.project,
            change=self.args.change,
            ref=self.args.ref
        )
        self.log.info('Invoking dequeue with arguments: %s' % kwargs)
        r = client.dequeue(**kwargs)
        return r

    def add_promote_subparser(self, subparsers):
        cmd_promote = subparsers.add_parser('promote',
                                            help='promote one or more changes')
        cmd_promote.add_argument('--tenant', help='tenant name',
                                 required=False, default='')
        cmd_promote.add_argument('--pipeline', help='pipeline name',
                                 required=True)
        cmd_promote.add_argument('--changes', help='change ids',
                                 required=True, nargs='+')
        cmd_promote.set_defaults(func=self.promote)
        self.cmd_promote = cmd_promote

    def promote(self):
        client = self.get_client()
        self._check_tenant_scope(client)
        kwargs = dict(
            tenant=self.tenant(),
            pipeline=self.args.pipeline,
            change_ids=self.args.changes
        )
        self.log.info('Invoking promote with arguments: %s' % kwargs)
        r = client.promote(**kwargs)
        return r

    def get_client(self):
        if self.args.zuul_url:
            self.log.debug(
                'Using Zuul URL provided as argument to instantiate client')
            client = ZuulRESTClient(self.args.zuul_url,
                                    self.args.verify_ssl,
                                    self.args.auth_token)
            return client
        conf_sections = self.config.sections()
        if len(conf_sections) == 1 and self.args.zuul_config is None:
            zuul_conf = conf_sections[0]
            self.log.debug(
                'Using section "%s" found in '
                'config to instantiate client' % zuul_conf)
        elif self.args.zuul_config and self.args.zuul_config in conf_sections:
            zuul_conf = self.args.zuul_config
        else:
            raise Exception('Unable to find a way to connect to Zuul, '
                            'provide the "--zuul-url" argument or set up a '
                            'zuul-client configuration file.')
        server = get_default(self.config,
                             zuul_conf, 'url', None)
        verify = get_default(self.config, zuul_conf,
                             'verify_ssl',
                             self.args.verify_ssl)
        # Allow token override by CLI argument
        auth_token = self.args.auth_token or get_default(self.config,
                                                         zuul_conf,
                                                         'auth_token',
                                                         None)
        if server is None:
            raise Exception('Missing "url" configuration value')
        client = ZuulRESTClient(server, verify, auth_token)
        return client

    def tenant(self):
        if self.args.tenant == "":
            if self.config is not None:
                config_tenant = ""
                conf_sections = self.config.sections()
                if (
                    self.args.zuul_config
                    and self.args.zuul_config in conf_sections
                ):
                    zuul_conf = self.args.zuul_config
                    config_tenant = get_default(
                        self.config, zuul_conf, "tenant", ""
                    )
                return config_tenant
        return self.args.tenant

    def add_encrypt_subparser(self, subparsers):
        cmd_encrypt = subparsers.add_parser(
            'encrypt', help='Encrypt a secret to be used in a project\'s jobs')
        cmd_encrypt.add_argument('--public-key',
                                 help='path to project public key '
                                      '(bypass API call)',
                                 metavar='/path/to/pubkey',
                                 required=False, default=None)
        cmd_encrypt.add_argument('--tenant', help='tenant name',
                                 required=False, default='')
        cmd_encrypt.add_argument('--project', help='project name',
                                 required=False, default=None)
        cmd_encrypt.add_argument('--no-strip', action='store_true',
                                 help='Do not strip whitespace from beginning '
                                      'or end of input.  Ignored when '
                                      '--infile is used.',
                                 default=False)
        cmd_encrypt.add_argument('--secret-name',
                                 default=None,
                                 help='How the secret should be named. If not '
                                      'supplied, a placeholder will be used.')
        cmd_encrypt.add_argument('--field-name',
                                 default=None,
                                 help='How the name of the secret variable. '
                                      'If not supplied, a placeholder will be '
                                      'used.')
        cmd_encrypt.add_argument('--infile',
                                 default=None,
                                 help='A filename whose contents will be '
                                      'encrypted. If not supplied, the value '
                                      'will be read from standard input.\n'
                                      'If entering the secret manually, press '
                                      'Ctrl+d when finished to process the '
                                      'secret.')
        cmd_encrypt.add_argument('--outfile',
                                 default=None,
                                 help='A filename to which the encrypted '
                                      'value will be written.  If not '
                                      'supplied, the value will be written '
                                      'to standard output.')
        cmd_encrypt.set_defaults(func=self.encrypt)
        self.cmd_encrypt = cmd_encrypt

    def encrypt(self):
        if self.args.project is None and self.args.public_key is None:
            raise ArgumentException(
                'Either provide a public key or a project to continue'
            )
        strip = not self.args.no_strip
        if self.args.infile:
            strip = False
            try:
                with open(self.args.infile) as f:
                    plaintext = f.read()
            except FileNotFoundError:
                raise Exception('File "%s" not found' % self.args.infile)
            except PermissionError:
                raise Exception(
                    'Insufficient rights to open %s' % self.args.infile)
        else:
            plaintext = sys.stdin.read()
        if strip:
            plaintext = plaintext.strip()
        pubkey_file = tempfile.NamedTemporaryFile(delete=False)
        self.log.debug('Creating temporary key file %s' % pubkey_file.name)

        try:
            if self.args.public_key is not None:
                self.log.debug('Using local public key')
                shutil.copy(self.args.public_key, pubkey_file.name)
            else:
                client = self.get_client()
                self._check_tenant_scope(client)
                key = client.get_key(self.tenant(), self.args.project)
                pubkey_file.write(str.encode(key))
                pubkey_file.close()
            self.log.debug('Invoking openssl')
            ciphertext_chunks = encrypt_with_openssl(pubkey_file.name,
                                                     plaintext,
                                                     self.log)
            output = textwrap.dedent(
                '''
                - secret:
                    name: {}
                    data:
                      {}: !encrypted/pkcs1-oaep
                '''.format(self.args.secret_name or '<name>',
                           self.args.field_name or '<fieldname>'))

            twrap = textwrap.TextWrapper(width=79,
                                         initial_indent=' ' * 8,
                                         subsequent_indent=' ' * 10)
            for chunk in ciphertext_chunks:
                chunk = twrap.fill('- ' + chunk)
                output += chunk + '\n'

            if self.args.outfile:
                with open(self.args.outfile, "w") as f:
                    f.write(output)
            else:
                print(output)
            return_code = True
        except ArgumentException as e:
            # do not log and re-raise, caught later
            raise e
        except Exception as e:
            self.log.exception(e)
            return_code = False
        finally:
            self.log.debug('Deleting temporary key file %s' % pubkey_file.name)
            os.unlink(pubkey_file.name)
        return return_code

    def add_build_info_subparser(self, subparsers):
        cmd_build_info = subparsers.add_parser(
            'build-info', help='Get info on a specific build')
        cmd_build_info.add_argument(
            '--tenant', help='tenant name', required=False, default='')
        cmd_build_info.add_argument(
            '--uuid', help='build UUID', required=True)
        cmd_build_info.add_argument(
            '--show-job-output', default=False, action='store_true',
            help='Only download the job\'s output to the console')
        cmd_build_info.add_argument(
            '--show-artifacts', default=False, action='store_true',
            help='Display only artifacts information for the build')
        cmd_build_info.add_argument(
            '--show-inventory', default=False, action='store_true',
            help='Display only ansible inventory information for the build')
        cmd_build_info.set_defaults(func=self.build_info)
        self.cmd_build_info = cmd_build_info

    def build_info(self):
        if sum(map(lambda x: x and 1 or 0,
                   [self.args.show_artifacts,
                    self.args.show_job_output,
                    self.args.show_inventory])
               ) > 1:
            raise Exception(
                '--show-artifacts, --show-job-output and '
                '--show-inventory are mutually exclusive'
            )
        client = self.get_client()
        self._check_tenant_scope(client)
        build = client.build(self.tenant(), self.args.uuid)
        if not build:
            print('Build not found')
            return False
        if self.args.show_job_output:
            output = client.session.get(build['job_output_url'])
            client._check_request_status(output)
            formatted_result = output.text
        elif self.args.show_artifacts:
            formatted_result = self.formatter('Artifacts')(
                build.get('artifacts', [])
            )
        elif self.args.show_inventory:
            formatted_result = self.formatter('Inventory')(
                build.get('inventory', {})
            )
        else:
            formatted_result = self.formatter('Build')(build)
        print(formatted_result)
        return True

    def add_builds_list_subparser(self, subparsers):
        cmd_builds = subparsers.add_parser(
            'builds', help='List builds matching search criteria')
        cmd_builds.add_argument(
            '--tenant', help='tenant name', required=False, default='')
        cmd_builds.add_argument(
            '--project', help='project name')
        cmd_builds.add_argument(
            '--pipeline', help='pipeline name')
        cmd_builds.add_argument(
            '--change', help='change reference')
        cmd_builds.add_argument(
            '--branch', help='branch name')
        cmd_builds.add_argument(
            '--patchset', help='patchset number')
        cmd_builds.add_argument(
            '--ref', help='ref name')
        cmd_builds.add_argument(
            '--newrev', help='the applied revision')
        cmd_builds.add_argument(
            '--job', help='job name')
        cmd_builds.add_argument(
            '--voting', help='show voting builds only',
            action='store_true', default=False)
        cmd_builds.add_argument(
            '--non-voting', help='show non-voting builds only',
            action='store_true', default=False)
        cmd_builds.add_argument(
            '--node', help='node name')
        cmd_builds.add_argument(
            '--result', help='build result')
        cmd_builds.add_argument(
            '--final', help='show final builds only',
            action='store_true', default=False)
        cmd_builds.add_argument(
            '--held', help='show held builds only',
            action='store_true', default=False)
        cmd_builds.add_argument(
            '--limit', help='maximum amount of results to return',
            default=50, type=int)
        cmd_builds.add_argument(
            '--skip', help='how many results to skip',
            default=0, type=int)
        cmd_builds.set_defaults(func=self.builds)
        self.cmd_builds = cmd_builds

    def builds(self):
        if self.args.voting and self.args.non_voting:
            raise Exception('--voting and --non-voting are mutually exclusive')
        filters = {'limit': self.args.limit,
                   'skip': self.args.skip}
        if self.args.project:
            filters['project'] = self.args.project
        if self.args.pipeline:
            filters['pipeline'] = self.args.pipeline
        if self.args.change:
            filters['change'] = self.args.change
        if self.args.branch:
            filters['branch'] = self.args.branch
        if self.args.patchset:
            filters['patchset'] = self.args.patchset
        if self.args.ref:
            filters['ref'] = self.args.ref
        if self.args.newrev:
            filters['newrev'] = self.args.newrev
        if self.args.job:
            filters['job_name'] = self.args.job
        if self.args.voting:
            filters['voting'] = True
        if self.args.non_voting:
            filters['voting'] = False
        if self.args.node:
            filters['node'] = self.args.node
        if self.args.result:
            filters['result'] = self.args.result
        if self.args.final:
            filters['final'] = True
        if self.args.held:
            filters['held'] = True
        client = self.get_client()
        self._check_tenant_scope(client)
        request = client.builds(tenant=self.tenant(), **filters)

        formatted_result = self.formatter('Builds')(request)
        print(formatted_result)

        return True


def main():
    ZuulClient().main()
