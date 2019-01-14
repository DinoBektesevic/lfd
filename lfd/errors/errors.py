import os
import re
import csv

import numpy as np

import createjobs



class QsubErr:
    """
    Class that contains all errors read form a Qsub outputs.

    init parameters
    ----------------
    Keywords:

        path:
            path to catenated file of all output errors.
            It will look only for files of *-*.e* nametype.

      methods
    -----------
    errexists(filename, jobid):
        returns True or False. Noerror state is defined if only
        self.noerrors is found in a *-*.e* qsub file.
    getall():
        returns a list( dict() ) or all the errors. Each dict()
        contains RunID ("startrun-endrun"), JobID and the error (Err)
        in question.
    """

    def __init__(self, path):
        self.path=path
        self._templine=""
        self.noerror = 196 #bytesize of fermi files without an error
        self.errors = self.read()


    def errExists(self, filename):
        path = os.path.join(self.path, filename)
        if (os.path.getsize(path) != self.noerror):
            return True
        return False

    def getError(self, filename, jobid):
        file = open(os.path.join(self.path, filename))
        noerror = ["/var/spool/torque/mom_priv/jobs/JOBID.fermi.SC[49]: .[5]: .[44]: shopt: not found [No such file or directory]",
                   "/var/spool/torque/mom_priv/jobs/JOBID.fermi.SC[49]: .[5]: .[63]: [: argument expected"]
        noerror1 = noerror[0].replace("JOBID", str(jobid))
        noerror2 = noerror[1].replace("JOBID", str(jobid))
        #print (noerror1, noerror2)
        #print(self.noerror)
        for line in file.readlines():
            errline = ""
            if line.strip() not in (noerror1, noerror2):
                errline += line.strip()
        return errline

    def read(self):
        p = re.compile("\d*-\d*.e\d*")
        errors = list( dict() )
        for filename in os.listdir(self.path):
            if(p.match(filename)):
                runid = filename.split(".")[0]
                jobid = filename.split(".")[1][1:]
                if(self.errExists(filename)):
                    errors.append({"RunID":runid,
                                   "Err":self.getError(filename, jobid),
                                   "JobID":jobid})
        return errors








def parse_log_entry(log_entry):
    alllines = log_entry.split("\n")
    run, camcol, field, filter = alllines[0].split(",")
    error = log_entry[len(alllines[0]):]
    err_code = alllines[8] 
    return run, camcol, filter, field, error, err_code


class DetectTrailsLogs(object):

    etype = np.dtype([
        ('run', np.int),
        ('camcol', np.int),
        ("filter", np.str, 1),
        ("field", np.int),
        ("error", np.str, 1000),
        ("err_code", np.str, 200)
    ])

    def __init__(self, path, errors):
        self.path = path
        self.errors = np.array(errors, dtype=DetectTrailsLogs.etype)

    @classmethod
    def fromFile(cls, file_path):
        fpath = file_path
        errors = []

        pattern = re.compile("[0-9]*,[123456],[0-9]*,[ugriz]")
        alltxt = open(file_path).read()

        matches = re.finditer(pattern, alltxt)
        starts = [m.start() for m in matches]

        #si - indice where log starts, ei indice of where a lof ends
        for si, ei in zip(starts, starts[1:]):
            (run, camcol, filter,
             field, error, err_code) = parse_log_entry(alltxt[si:ei])
            errors.append((
                int(run), int(camcol),
                filter,  int(field),
                error, err_code
            ))


        return cls(fpath, errors=errors)

    def summary(self):
        sortedind = np.lexsort((
            #self.errors["run"],
            self.errors["filter"],
            #self.errors["camcol"],
            #self.errors["field"]
        )[::-1])

        for run, camcol, filter, field, error, errc in self.errors[sortedind]:
            print("{0:<5d}{1:<3d}{2:<3}{3:<10d}{4}".format(run, camcol,
                                                           filter, field,
                                                           errc[:80]))
















class Errors:
    """
    Class that contains all errors read (Qsub+detecttrails logs).
    Parse all errors with this class.

    init parameters
    ----------------
    Keywords:

        path:
            path to folder with all qsub errors
        pathlog:
            path to folder with all detectrails errors

      methods
    -----------
    toFile(filename):
        prints out all errors found into a new file given by filename.
        Errors are sorted, each run is printed under the runID and JobID
        in which it executed. ****DOESN'T REALLY WORK WELL!****
    """

    def __init__(self, qsubErrpath, dettrailsErrpath):
        self.qsub = QsubErr(qsubErrpath).errors
        self.dettrails = DetectTrailsLogs(dettrailsErrpath).errors

    def toFile(self, filepath):
        file = open(filepath, "w")
        for qerr in self.qsub:
            bot = int(qerr["RunID"].split("-")[0])
            top = int(qerr["RunID"].split("-")[1])
            #print(bot, top, int(logs[0]["Run"]))
            file.writelines(qerr["RunID"]+" "+qerr["JobID"]+" "+qerr["Err"]+"\n")
            for lerr in self.dettrails:
                if (bot <= int(lerr["Run"]) and top>=int(lerr["Run"])):
                    file.writelines(("    {} {} {} {} {}\n").format(lerr["Run"], lerr["camcol"],
                                                        lerr["filter"], lerr["field"], lerr["Err"]))
        file.close()

    def _removeDuplicates(self, runs, fun=None):
        seen = set()
        return [ x for x in runs if not (x in seen or seen.add(x))]

    def _genRunsQsub(self):
        runs = list()
        for qerr in self.qsub:
            top = int(qerr["RunID"].split("-")[1])
            bot = int(qerr["RunID"].split("-")[0])
            if (top!=bot):  runs.extend([x for x in range(bot, top)])
            else: runs.append(bot)
        return runs

    def _genRunsDT(self):
        allerr = list()
        for lerr in self.dettrails:
            allerr.append(lerr["Run"])
        runs = self._removeDuplicates(allerr)
        return runs

    def genJobsQsub(self, kwargs=None):
        runs = self._genRunsQsub()
        if kwargs:
            self.jobs = createjobs.Jobs(len(runs),runs=runs, **kwargs)
        else:
            self.jobs = createjobs.Jobs(len(runs), runs=runs)

        self.jobs.create()

    def __len__(self):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, context=15)
        for i in range(5):
            print "    caller: ",calframe[i][3]
        len1 = len(self.qsub)
        print "Number of failed QSUB jobs: ", len1
        len2 = len(self.dettrails)
        print "Number of failed frames (DetTrails errors): ", len2
        print "Total errors occured QSUB+DetTrails = "
        return len1+len2
