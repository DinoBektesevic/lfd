import os

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
        /home/fermi/$user/run_results/$JOB_ID.

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


    def __init__(self, n, runs=None, queue="standard", wallclock="24:00:00",
                 ppn="3", cputime="48:00:00", pernode=False,
                 template_path=None, save_path=None, res_path="run_results",
                 command = 'python3 -c "import detecttrails as dt;' +\
                                    ' dt.DetectTrails($).process()"\n',
                 **kwargs):

        self.n = n
        self.wallclock = wallclock
        self.cputime = cputime
        self.pernode = pernode
        self.res_path = res_path


        curpath = os.path.abspath(os.path.curdir)
        cjpath = os.path.join(curpath, "createjobs/")
        if save_path is not None:
            tmppath = save_path #expandpath(save_path)
        else:
            tmppath = cjpath

        if save_path is not None:
            os.makedirs(tmppath)
            tmpdir = tmppath
        else:
            tmpdir = os.path.join(tmppath, "jobs")
            os.makedirs(tmpdir)

        self.save_path = tmpdir

        self.queue = queue
        self.ppn = ppn
        self.runs = runs

        if template_path is not None:
            tmppath = expandpath(template_path)
        else:
            tmppath = os.path.split(__file__)[0]
            tmppath = os.path.join(tmppath, "generic")
            tmppath = (True, tmppath)

        if  os.path.isfile(tmppath[1]):
            self.template_path = tmppath[1]
        else:
            self.template_path = os.path.join(cjpath, "generic")

        self.command = command

        self.kwargs = kwargs

    def _runlstAll(self):
        """
        Returns a runlst made for all runs found in runlist.par
        file. Used in createAll function to create a runlst for all
        runs.
        """
        rl = files.runlist()
        indices = np.where(rl["rerun"] == "301")
        rl = rl[indices]
        runs = rl["run"]
        nruns = int(len(runs)/self.n)
        runlst = [runs[i:i+nruns] for i in range(0, len(runs), nruns)]
        return runlst

    def makeRunlst(self, runs):
        """
        Create a runlst from a list of runs or Results instance.
        Recieves a list of runs: [N1,N2,N3,N4,N5...] and returns
        a runlst:
        [   (N1, N2...N( n_runs / n_jobs)) 0
            ...
            (N1, N2...N( n_runs / n_jobs)) n_jobs
        ]
        Runlst is a list of lists. Inner lists contain runs that
        will be executed in a single job. Lenght of outter list
        matches the number of jobs that will be started i.e.
            runls = list(  (2888, 2889, 2890)
                           (3001, 3002, 3003)
                        )
        will start 2 jobs (job0.dqs, job1.dqs), where job0.dqs will
        call DetectTrails.process on 3 runs: 2888, 2889, 2890.
        """
        if len(runs) % self.n == 0:
            nruns = int(len(runs)/self.n)
            runlst = [runs[i:i+nruns] for i in range(0, len(runs), nruns)]
        else:
            nruns = int(len(runs)/self.n)+1
            runlst = [runs[i:i+nruns] for i in range(0, len(runs), nruns)]
        return runlst

    def _createBatch(self, runlst):
        """
        Writes a batch.sh script that contians qsub job#.dqs
        for each job found in runlst.
        Created automatically if you use create or createAll
        methods.
        """
        newbatch = open(self.save_path+"/batch.sh", "w")

        for i in range(0, len(runlst)):
            newbatch.writelines("qsub job"+str(i)+".dqs\n")
        newbatch.close


    def _findKwargs(self):
        """
        Works out what kwargs, if any were sent. If camcol and/or
        filter was sent it adds them as instance attributes.
        It always adds a "pick" instance attribute that describes
        the parameters sent. pick attribute is used by  writeDqs from
        writer module expand command attribute to appropriate string.

        METHOD DOESN'T GET CALLED UNTILL CREATE FUNCTION!
        this avoids potential problems, i.e. if the user sets runs
        attribute after initialization.
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
        """
        Creates job#.dqs files from runlst.
        runlst is a list(list()) in which inner list contains all runs per job.
        Length of outter list is the number of jobs started. See class help.
        """
        self._findKwargs()

        if not self.runs:
            print("There are no runs to create jobs from. Creating jobs"+\
                  " for all runs in runlist.par file.")
            runlst = self._runlstAll()
            writer.writeDqs(self, runlst)

        elif self.runs:
            runlst = self.makeRunlst(self.runs)
            writer.writeDqs(self, runlst)
        else:
            raise ValueError("Unrecognized format for runs.")

        print("Creating: \n "\
              "    {} jobs with {} runs per job \n"\
              "    Queue:     {} \n"\
              "    Wallclock: {} \n"\
              "    Cputime:   {} \n"\
              "    Ppn:       {} \n"\
              "    Path:      {}".format(len(runlst), len(runlst[0]),
                                         self.queue, self.wallclock,
                                         self.cputime, self.ppn,
                                         self.save_path)
             )
        self._createBatch(runlst)



