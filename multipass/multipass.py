#!/usr/bin/env python
#
# multipass ds ChRIS plugin app
#
# (c) 2021 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import      os

from chrisapp.base import ChrisApp
import      pudb
import      subprocess
import      pfmisc
from        pfmisc._colors      import  Colors

Gstr_title = """

       _                        _ _   _
      | |                      | | | (_)
 _ __ | |______ _ __ ___  _   _| | |_ _ _ __   __ _ ___ ___
| '_ \| |______| '_ ` _ \| | | | | __| | '_ \ / _` / __/ __|
| |_) | |      | | | | | | |_| | | |_| | |_) | (_| \__ \__ \\
| .__/|_|      |_| |_| |_|\__,_|_|\__|_| .__/ \__,_|___/___/
| |                                    | |
|_|                                    |_|
"""

Gstr_synopsis = """

    NAME

       multipass

    SYNOPSIS

        multipass                                                       \\
            [--exec <appToRun>]                                         \\
            [--specificArgs <specificArgs>]                             \\
            [--splitExpr <splitOn>]                                     \\
            [--commonArgs <commonArgs>]                                 \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [--noJobLogging]                                            \\
            [--verbose <level>]                                         \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir>

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                                 \\
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing          \\
                fnndsc/pl-multipass multipass                           \\
                /incoming /outgoing

    DESCRIPTION

        `multipass` is a very simple script that runs a specific
        <appToRun> on the underlying system shell multiple times over
        the same <inputDir>. Each run, or phase, differs in the
        set of <pipeSeparatedSpecificArgs> that is passed to the app.

        In each phase, the <commonArgs> remains constant.

        The main purpose of this plugin is to allow for one simple
        mechanism of running slightly different flags over the
        same <inputDir> space in several phases, and capturing
        the multiple outputs in the <outputDir>. In the context of
        a `ChRIS` feed tree, this has the effect of having one feed
        thread contain effectively multiple runs of some <appToRun>
        in one <outputDir>. In some cases this can be a useful
        execution model.

    ARGS

        [--exec <appToRun>]
        A specific `app` to run in _multi-phase_ mode. This app must by
        necessity exist within the  `multiphase` container. See the
        `requirements.txt` for list of installed apps

        [--specificArgs <specificArgs>]
        This is a string list of per-phase specific arguments. Each
        phase is separated by <splitOn> expression.

        [--splitExpr <splitOn>]
        The expression on which to split the <specificArgs> string.
        Default is '++'.

        [--commonArgs <commonArgs>]
        This is a raw string of args, common to each phase call of the
        <appToRun>.

        [-h] [--help]
        If specified, show help message and exit.

        [--json]
        If specified, show json representation of app and exit.

        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.

        [--savejson <DIR>]
        If specified, save json representation file to DIR and exit.

        [--noJobLogging]
        Turns off per-job logging to file system.

        [--verbose <level>]
        Verbosity level for app: 0->silent, 5->talkative.

        [--version]
        If specified, print version number and exit.
"""


class Multipass(ChrisApp):
    """
    An app to make multiple passes or runs of a certain Python Utility with different args
    """
    PACKAGE                 = __package__
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = '' # url of an icon image
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = '2Gi' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT           = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT           = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        self.add_argument("--commonArgs",
                            help        = "Arguments common to each pass",
                            type        = str,
                            dest        = 'commonArgs',
                            optional    = True,
                            default     = "")

        self.add_argument("--specificArgs",
                            help        = "Compound string of pass specific args",
                            type        = str,
                            dest        = 'specificArgs',
                            optional    = True,
                            default     = "")

        self.add_argument("--splitExpr",
                            help        = "Expression on which to split the <specificArgs>",
                            type        = str,
                            dest        = 'splitExpr',
                            optional    = True,
                            default     = "++")

        self.add_argument("-e", "--exec",
                            help        = "DS app to run",
                            type        = str,
                            dest        = 'exec',
                            optional    = True,
                            default     = "pfdo_mgz2image")

        self.add_argument("--noJobLogging",
                            help        = "Turn off per-job logging to file system",
                            type        = bool,
                            dest        = 'noJobLogging',
                            action      = 'store_true',
                            optional    = True,
                            default     = False)

        self.add_argument("--verbose",
                            type        = str,
                            optional    = True,
                            help        = "verbosity level for app",
                            dest        = 'verbose',
                            default     = "1")


    def job_run(self, str_cmd):
        """
        Running some CLI process via python is cumbersome. The typical/easy
        path of

                            os.system(str_cmd)

        is deprecated and prone to hidden complexity. The preferred
        method is via subprocess, which has a cumbersome processing
        syntax. Still, this method runs the `str_cmd` and returns the
        stderr and stdout strings as well as a returncode.
        Providing readtime output of both stdout and stderr seems
        problematic. The approach here is to provide realtime
        output on stdout and only provide stderr on process completion.
        """
        d_ret       : dict = {
            'stdout':       "",
            'stderr':       "",
            'cmd':          "",
            'cwd':          "",
            'returncode':   0
        }
        str_stdoutLine  : str   = ""
        str_stdout      : str   = ""

        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
        )

        # Realtime output on stdout
        str_stdoutLine  = ""
        str_stdout      = ""
        while True:
            stdout      = p.stdout.readline()
            if p.poll() is not None:
                break
            if stdout:
                str_stdoutLine = stdout.decode()
                if int(self.args['verbosity']):
                    print(str_stdoutLine, end = '')
                str_stdout      += str_stdoutLine
        d_ret['cmd']        = str_cmd
        d_ret['cwd']        = os.getcwd()
        d_ret['stdout']     = str_stdout
        d_ret['stderr']     = p.stderr.read().decode()
        d_ret['returncode'] = p.returncode
        if int(self.args['verbosity']) and len(d_ret['stderr']):
            print('\nstderr: \n%s' % d_ret['stderr'])
        return d_ret

    def job_stdwrite(self, d_job, str_outputDir, str_prefix = ""):
        """
        Capture the d_job entries to respective files.
        """
        if not self.args['noJobLogging']:
            for key in d_job.keys():
                with open(
                    '%s/%s%s' % (str_outputDir, str_prefix, key), "w"
                ) as f:
                    f.write(str(d_job[key]))
                    f.close()
        return {
            'status': True
        }

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """

        l_specificArg :     list    = []
        str_cmd       :     str     = ""
        pass_count    :     int     = 0

        options.verbosity   = options.verbose
        self.args           = vars(options)
        self.__name__       = "multipass"
        self.dp             = pfmisc.debug(
                                 verbosity   = int(self.args['verbosity']),
                                 within      = self.__name__
                             )

        self.dp.qprint( Colors.CYAN + Gstr_title,
                            level   = 1,
                            syslog  = False)

        self.dp.qprint( Colors.YELLOW + 'Version: %s' % self.get_version(),
                            level   = 1,
                            syslog  = False)

        for k,v in self.args.items():
            self.dp.qprint("%25s: %-40s" % (k, v),
                            comms   = 'status',
                            syslog  = False)
        self.dp.qprint(" ", level   = 1, syslog = False)

        l_specificArg   = options.specificArgs.split(options.splitExpr)
        str_cmd         = ""

        for str_specificArg in l_specificArg:
            if options.exec == 'pfdo_mgz2image':
                str_cmd = '%s --inputDir %s --outputDir %s %s %s' % \
                          (
                            options.exec,
                            options.inputdir,
                            options.outputdir,
                            options.commonArgs,
                            str_specificArg
                        )
            self.dp.qprint("Running %s..." % str_cmd)
            # Run the job and provide realtime stdout
            # and post-run stderr
            self.job_stdwrite(
                self.job_run(str_cmd), options.outputdir,
                '%s-%d-' % (options.exec, pass_count)
            )
            pass_count += 1


    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
