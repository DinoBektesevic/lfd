import os

def get_node_with_files(job, run):
    """
    .. deprecated:: 1.0

    Reads lst-lnk file to retrieve nodes on which fits files
    of run are stored. Returns the node number. In cases where
    error occured while reading node number returns the first,
    "01", node.

    """
    os.path.join(job.dir, "lst-lnk")
    f = open(os.path.join(job.dir, "lst_lnk"))
    read = f.read()
    index = read.find(str(run))
    if read[index-1] == "/":
        return read[index-32:index-30]
    return "01"

def writeJob(job, verbose=True):
    """Writes the job#.dqs files. Takes in a Jobs instance and processes the
    "generic" template replacing any/all keywords using values from Jobs
    instance.
    For each entry in runlst it creates a new job#.dqs file, which contains
    commands to execute detecttrails processing for each entry of entry in
    runlst.

    Parameters
    ----------
    job : lfd.createjobs.Job
       Job object from which job scripts are to be created.
    verbose : bool
       deprecated to alleviate clutter

    """
    runlst = job.makeRunlst()
    for i in range(0, len(runlst)):
        jobpath = os.path.abspath(job.save_path)
        newjobpath = os.path.join(jobpath, "job"+str(i)+".dqs")
        newjob = open(newjobpath, "w")
        temp = job.template

        if job.pick.lower() == "Results":
            jobname = "{0}-{1}".format(runlst[i][0].run, runlst[i][-1].run)
        else:
            jobname = "{0}-{1}".format(runlst[i][0], runlst[i][-1])

        temp = temp.replace("JOBNAME", jobname)
        temp = temp.replace("QUEUE", job.queue)
        temp = temp.replace("WALLCLOCK", job.wallclock)
        temp = temp.replace("PPN", job.ppn)
        temp = temp.replace("CPUTIME", job.cputime)
        temp = temp.replace("RESULTSPATH", job.res_path)

        header = temp.split("COMMAND")[0]
        footer = temp.split("COMMAND")[1]

        for x in runlst[i]:
            if job.pick.lower() == "run":
                command = "run={}".format(x)
            elif job.pick.lower() == "runfilter":
                command = "run={0}, filter='{1}'".format(x, job.filter)
            elif job.pick.lower() == "runcamcol":
                command = "run={0}, camcol={2}".format(x,  job.camcol)
            elif job.pick.lower() == "runfiltercamcol":
                command = "run={0}, filter='{1}', camcol={2}"
                command = command.format(x, job.filter, job.camcol)
            elif job.pick.lower() == "results":
                command = "run={0}, filter='{1}', camcol={2}, field={3}"
                command = command.format(x.run, x.filter, x.camcol, x.field)
            else:
                raise ValueError(
                    ("Type of command format is not known, expected pick=run|"
                     "runcamcol|runfilter|runcamcolfilter|results, "
                     "but got {}".format(job.pick.lower()))
                )
            header += job.command.replace("$", command)

            if job.pernode:
                node = get_node_with_files(job, run)
                header = header.replace("NODEFLAG", "fermi-node"+node)
                header = header.replace("FERMINODE", "fermi-node"+node)
            else:
                 header = header.replace("NODEFLAG", "1")
                 header = header.replace("FERMINODE", "fermi-node01")
        newjob.writelines(header+footer)
    newjob.close()

