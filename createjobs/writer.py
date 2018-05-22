import os

def get_node_with_files(job, run):
    """
                     ***DEPRECATED***
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

def writeDqs(job, runlst):
    """
    Writes the job#.dqs files. Takes in a Jobs instance and processes the
    "generic" template replacing any/all keywords using values from Jobs instance.

    For each entry in runlst it creates a new job#.dqs file, which contains
    commands to execute detecttrails processing for each entry of entry in runlst.
    """
    for i in range(0, len(runlst)):
        jobpath = os.path.abspath(job.save_path)
        newjobpath = os.path.join(jobpath, "job"+str(i)+".dqs")
        newjob = open(newjobpath, "w")
        temp = open(job.template_path).read()

        if job.pick.lower() in ["results", "fromresults"]:
            temp = temp.replace("JOBNAME", str(runlst[i][0].run)
                                +"-"+str(runlst[i][-1].run))
        else:
            temp = temp.replace("JOBNAME", str(runlst[i][0])
                                +"-"+str(runlst[i][-1]))
        temp = temp.replace("QUEUE", job.queue)
        temp = temp.replace("WALLCLOCK", job.wallclock)
        temp = temp.replace("PPN", job.ppn)
        temp = temp.replace("CPUTIME", job.cputime)
        temp = temp.replace("RESULTSPATH", job.res_path)

        header = temp.split("COMMAND")[0]
        footer = temp.split("COMMAND")[1]

        for x in runlst[i]:

            if job.pick.lower() in ["run", "runs", "fromruns"]:
                header+=job.command.replace("$", "run="+str(x))

            if job.pick.lower() in ["runfilter", "filterrun", "fromrunfilter"]:
                header+=job.command.replace("$", "run="+str(x) +
                                               ", filter='"+str(job.filter)+"'")

            if job.pick.lower() in ["results", "fromresults"]:
                header+=job.command.replace("$", "run="+str(x.run) +
                                                ",camcol="+str(x.camcol) +
                                                ",filter='"+str(x.filter) +
                                                "',field="+str(x.field)
                                            )

            if job.pick.lower() in ["runcamcol", "runcamcol", "fromruncamcol"]:
                header+=job.command.replace("$", "run="+str(x) +
                                                ",camcol=" +str(job.camcol))

            if job.pick.lower() in ["runfiltercamcol", "runcamcolfilter",
                                "fromruncamcolfilter", "fromrunfiltercamcol"]:
                header+=job.command.replace("$", "run="+str(x) +
                                                ",camcol=" +str(job.camcol) +
                                                ",filter='"+str(job.filter)+"'")

            if job.pernode:
                node=get_node_with_files(job, run)
                header = header.replace("NODEFLAG", "fermi-node"+node)
                header = header.replace("FERMINODE", "fermi-node"+node)
            else:
                 header = header.replace("NODEFLAG", "1")
                 header = header.replace("FERMINODE", "fermi-node01")

        newjob.writelines(header+footer)

    newjob.close()

