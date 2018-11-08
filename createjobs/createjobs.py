import os
import warnings

import numpy as np

from lfd.detecttrails.sdss import files
from . import writer
from lfd.results import Event, Frame

__all__ = ["Jobs"]

#from lfd.gui.utils import expandpath

def expandpath(path):
    if path is not None and path != "":
        if path[0] == "~":
            path = os.path.expanduser(path)
        if os.path.exists(path):
            path = os.path.abspath(path)
            return (True, path)
    return (False, None)


class Jobs:
    """
    Class that holds all the important functions for making Qsub jobs.

    init parameters
    -----------------
    Keywords:
        n: number of jobs you want to start.

    Optional:
        save_path:
	        path to directory where you want your jobs to be stored.
            A default path is currently set to ~/Desktop/createjobs
        res_path:
            path to a directory on cluster master where results will
            be copied once the job is finished.
        template_path:
            path to the desired template. Template should contain all
            necessary parameters described bellow. Template parameters
            have to be uppercase single words.
        template:
            a full template text as a string
        queue:
            sets the QSUB queue type: serial, standard or parallel.
            Default: standard.
            Notice that your local QSUB setup will limit wallclock,
            and cputime based on queue you selected.
        wallclock:
            set jobs maximum time allowed to be on the job wall in
            hours.
            default: 24:00:00
        cputime:
            set jobs maximum time allowed to be running on a CPU in
            hours.
            default: 48:00:00
        ppn:
            maximum allowed processors per node.
            Default: 3
        command:
             command that runs detecttrails process function. Default:
                 python -c "import detect_trails as dt;" +\
             "dt.DetectTrails($).process()"
             where "$" gets expanded depending on kwargs.
        **kwargs:
            it's possible create jobs with commands different than
            just processing the whole runs. F.e. it's possible to
            create jobs that will process all runs, all runs but
            just their 1st camcol and/or a filter. The only true way
            of generating jobs per frames is to send in a list of Event
            or Frame instances. See results package help for those
            objects. See this module's help for examples of different
            possible combinations - the usage is the same as with DetectTrails.
        runs:
            if runs are not specified, all sdss runs found in
              runlist.par file will be used.
            if runs is a list of runs only those runs will be sorted
              into jobs
            if runs is a list of Event or Frame instances, only those frames
              will be sorted into jobs.

    In "save_path" a folder "jobs" will be created, if it doesn't exist
    already. In "jobs" folder, files "job#.dqs" will be stored.

    Template is located inside this package in "createjobs"  folder
    under the name "generic".
    Location where final results are saved on Fermi cluster by default
    is
        /home/fermi/$user/$res_path/$JOB_ID.

     methods
    -----------
    _runlstAll():
        don't use this. It just reads in runslit.par and creates jobs
        for every run in there that has a rerun set to 301.
    _createBatch(runlst):
        creates a batch.sh file that starts all the qsub jobs at once.
    create(runlst):
        creates jobs, then batch.
    makeRunlst(list_of_runs):
        creates a runlst from a list of runs. I.e.
            (2881, 2882, 2883, 2884)
        is converted to:
            list(  (2881, 2882)
                   (2883, 2884)
                )
        if chosen number of jobs n=2.
     _findKwargs():
        internal logic to work out what kwargs were sent, if any, to
        expand command to appropriate form.
    """
    def __init__(self, n, runs=None, template_path=None, save_path=None,
                 queue="standard", wallclock="24:00:00", ppn="3",
                 cputime="48:00:00", pernode=False,
                 command = ('python3 -c "import detecttrails as dt; '
                            'dt.DetectTrails($).process()"\n'),
                  res_path="run_results", **kwargs):
        self.n = n
        self.ppn = ppn
        self.runs = runs
        self.pick = None
        self.queue = queue
        self.cputime = cputime
        self.pernode = pernode
        self.command = command
        self.wallclock = wallclock
        self.kwargs = kwargs

        # Paths are harder to set up. There are three paths to track: where to
        # save DQS scripts (save_path), where to find template path
        # (template_path) and into which folder to copy the results on the
        # cluster after processing (res_path)
        self.res_path = res_path
        self.__init__createjobs_folder(save_path)
        self.__init__template(template_path, kwargs.pop("template", None))

        # set the initial value of self.pick if at all possible
        self._findKwargs()

    def __init__createjobs_folder(self, save_path):
        """Creates the createjobs folder at the given location, the current
        directory by default. In createjobs folder a new directory is opened
        for each set of jobs produced to avoid overwriting each other.
        """
        # this will be the location of invocation, not the dir of this file
        curpath = os.path.abspath(os.path.curdir)
        cjpath = os.path.join(curpath, "createjobs/")
        tmppath = cjpath

        if save_path is not None:
            tmppath = os.path.expanduser(save_path)
        if os.path.split(tmppath)[-1] == "createjobs":
            tmppath = os.path.join(tmppath, "jobs")

        if os.path.isdir(tmppath) and len(os.listdir(tmppath)) == 0:
            pass
        else:
            os.makedirs(tmppath)

        self.save_path = tmppath

    def __init__template(self, template_path, template):
        """Verifies if the provided path to template is correct or not and
        loads the template. If the provided template path is incorrect it loads
        the default template provided with this module.
        If a whole template is provided as a string, it will use that string as
        the template.
        """
        # this will be the dir of this file
        default_path = os.path.split(__file__)[0]
        default_path = os.path.join(default_path, "generic")

        if template_path is not None:
            tmppath = expandpath(template_path)
        else:
            tmppath = default_path

        if  os.path.isfile(tmppath):
            self.template_path = tmppath
        else:
            warnings.Warning(("Could not open the given template. Check it "
                              "exists, is not a folder, is not corrupt. Using "
                              "the default template provided with the module."))
            self.template_path = os.path.join(cjpath, "generic")

        if template is None:
            self.template = open(self.template_path).read()
        else:
            self.template = template

    def getAllRuns(self):
        """Returns a list of all runs found in runlist.par file."""
        rl = files.runlist()
        indices = np.where(rl["rerun"] == b"301")
        rl = rl[indices]
        return rl["run"]

    def makeRunlst(self, runs=None):
        """
        Create a runlst from a list of runs or Results instance. Recieves a
        list of runs: [N1,N2,N3,N4,N5...] and returns a runlst:
        [   (N1, N2...N( n_runs / n_jobs)) # idx = 0
            ...
            (N1, N2...N( n_runs / n_jobs)) # idx = n_jobs
        ]

        Runlst is a list of lists. Inner lists contain runs that will be
        executed in a single job. Lenght of outter list matches the number of
        jobs that will be started i.e.
            runls = list(  (2888, 2889, 2890)
                           (3001, 3002, 3003)
                        )
        will start 2 jobs (job0.dqs, job1.dqs), where job0.dqs will call
        DetectTrails.process on 3 runs: 2888, 2889, 2890.

        If (optionally) a list of runs is supplied a run list will be produced
        fom that list, instead of the runs attribute.
        """
        runs = self.runs if runs is None else runs

        whole, remain = divmod(len(runs), self.n)
        nruns = whole if remain == 0 else whole+1
        njobs = int(np.ceil(len(runs)/nruns))

        return [runs[i:i+nruns] for i in range(0, len(runs), nruns)]

    def _createBatch(self, njobs):
        """ Writes a batch.sh script that contians qsub job#.dqs for each job
        found in runlst. Created automatically if you use create or createAll
        methods.
        """
        newbatch = open(self.save_path+"/batch.sh", "w")

        for i in range(0, njobs):
            newbatch.writelines("qsub job"+str(i)+".dqs\n")
        newbatch.close


    def _findKwargs(self):
        """ Works out what kwargs, if any were sent. If camcol and/or filter
        was sent it adds them as instance attributes. It always adds a "pick"
        instance attribute that describes the parameters sent. 'pick0 attribute
        is used by  writeJob from writer module expand command attribute to
        appropriate string.

        METHOD DOESN'T GET CALLED UNTILL CREATE FUNCTION!
        This avoids potential problems, i.e. if the user sets runs
        attribute after initialization but makes it impossible to determine
        the 'pick' attribute value untill execution.
        """
        kwargs = self.kwargs

        if 'camcol' in kwargs:
            if kwargs['camcol'] not in (1, 2, 3, 4, 5, 6):
                raise ValueError("Nonexisting camcol")
            self.camcol = kwargs['camcol']
            self.pick = 'RunCamcol'

        if 'filter' in kwargs:
            if  kwargs['filter'] not in ('u', 'g', 'r', 'i', 'z'):
                raise ValueError("Nonexistting filter")
            self.filter = kwargs['filter']
            if 'camcol' in kwargs:
                self.pick = 'RunCamcolFilter'
            else:
                self.pick = 'RunFilter'

        # this will be true even when runs is a list of results, but in that
        # case pick will be re-picked in the following if. Effectively this
        # means that "run" is the default pick.
        if all(["camcol" not in kwargs, "filter" not in kwargs]):
            self.pick="Run"

        if isinstance(self.runs, list) and (isinstance(self.runs[0], Event) or
                                            isinstance(self.runs[0], Frame)):
            self.pick="Results"

    def create(self):
        """Creates job#.dqs files from runlst. runlst is a list(list()) in
        which inner list contains all runs per job. Length of outter list is
        the number of jobs started. See class help.
        """
        # Continuously updating all the class attributes based on the exact
        # settings chosen in real-time is very ugly. So we force update all
        # attributes that could have changed (i.e. self.pick, self.runs, job
        # partitioning stats etc.)

        self._findKwargs()

        if not self.runs:
            print("There are no runs to create jobs from. Creating jobs"+\
                  " for all runs in runlist.par file.")
            self.runs = self.getAllRuns()

        whole, remain = divmod(len(self.runs), self.n)
        nruns = whole if remain == 0 else whole+1
        njobs = int(np.ceil(len(self.runs)/nruns))
        print("Creating: \n "\
              "    {} jobs with {} runs per job \n"\
              "    Queue:     {} \n"\
              "    Wallclock: {} \n"\
              "    Cputime:   {} \n"\
              "    Ppn:       {} \n"\
              "    Path:      {}".format(njobs, nruns,
                                         self.queue, self.wallclock, self.cputime,
                                         self.ppn, self.save_path)
        )

        writer.writeJob(self)
        self._createBatch(njobs)



