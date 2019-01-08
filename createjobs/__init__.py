"""
createjobs module is used to create .dqs files necessary to run a job
on QSUB system. Importing this module will only import Jobs class.
Main idea was to create a class that can take care of writing a
large job requests on users behalf without the need to always edit
the template to change parameters. This package was written for the
Fermi cluster at the Astronomical Observatory Belgrade but is easily
adaptable for any QSUB system.

Main pillar for the creating is Jobs class. In the background it uses
writer module to write the user-specified parameters to a template.


    Template
----------------------

By default the opened template is called "generic" and can be found
in the same folder this module resides in. Since it's neccesary to
change a lot of parameters, especially paths, template can be edited,
or a new one can be sent in its place. Specifying template_path at
class instantiation time will instruct writer to change that template.
When writing your own template, to avoid error reports, you have to
specify all parameters in the new template that this class can change.
Parameters are uppercase single words, i.e: JOBNAME, QUEUE, NODEFLAG

    #!/usr/bin/ksh
    #PBS -N JOBNAME
    #PBS -S /usr/bin/ksh
    #PBS -q QUEUE
    #PBS -l nodes=NODEFLAG:ppn=PPN
    #PBS -l walltime=WALLCLOCK,cput=CPUTIME

All enviroment paths in the template are NOT changable throught this class.
Edit those directly, i.e. the save path for results is given by:
    cp *.txt /home/fermi/$user/run_results/$JOB_ID/
and save the result as a new template.

    Usage cases
----------------------

1) The simplest one is just specifying the number of jobs you want.
   Jobs will then take all the runs found in runlist.par file with
   rerun 301. runlist.par file should be located in $BOSS/photo/redux.

	  >>> jobs = cj.Jobs(500)
	  >>> jobs.create()
	  There are no runs to create jobs from.
          Creating jobs for all runs in runlist.par file.

          Creating:
	       765 jobs with 1 runs per job
	      Queue:     standard
	      Wallclock: 24:00:00
	      Cputime:   48:00:00
	      Ppn:       3
	      Path:      /home/user/Desktop/.../jobs

    User will be notified about all important parameters that were set.
    Notice that the default save path, queue, wallclock, ppn and
    cputime are set by default. All parameters can be sent as keyword
    arguments at instantiation.

    Notice that we specified 500 jobs to be created but 765 jobs were.
    This is intentional. Jobs looks for the next larger whole number
    divisor divisor to split the jobs between. It's better to send in
    more jobs than to risk jobs failing.

2)  Specifying certain runs by hand is possible by sending a list of
    runs of interes:

	    >>> runs = [125, 99, 2888, 1447]
	    >>> jobs = cj.Jobs(2, runs=runs)
	    >>> jobs.create()
	    Creating:
	         2 jobs with 2 runs per job
	        Queue:     standard
            Wallclock: 24:00:00
            Cputime:   48:00:00
            Ppn:       3
            Path:      /home/user/Desktop/.../jobs

    In both examples so far what is actually being run is:

        python3 -c "import detecttrails as dt;
                    dt.DetectTrails(run=2888).process()"

    It is possible to edit the command that is going to be executed.
    Specifying aditional keyword arguments to Jobs class helps you
    utilize DetectTrails class run options. Sent kwargs are applied
    globaly across every job. It's not possible to specify separate
    kwargs for each job.

        >>> runs = [125, 99, 2888, 1447]
        >>> jobs = cj.Jobs(2, runs=runs, camcol=1)
        >>> jobs.create()

    would create 2 jobs with 2 runs per job as the above example. The
    invocation of the DetectTrails class would now look like:

        python3 -c "import detect_trails as dt;
                    dt.DetectTrails(run=125,camcol=1).process()"

    Which would process only the camcol 1 of run 125. Actual written
    job#.dqs file is not as readable/friendly as above examples.
    Another example:

        >>> jobs = cj.Jobs(2, runs=runs, camcol=1, filter="i")

    would execute 2 jobs with following 2 calls to DetectTrails class:

        python3 -c "import detect_trails as dt;
                    dt.DetectTrails(run=125,camcol=1,filter=i).process()"

    See help on DetectTrails class for a list of all options.

    To further fine tune your job behaviour it's possible to change
    the default execution command to supply additional execution
    parameters. By default keyword argument command is set to:

        python3 -c "import detecttrails as dt;
                    dt.DetectTrails($).process()"

    Where "$" sign gets automatically expanded by the writer module.
    There should also ALWAYS be a "$" character present in a command.
    "$" replaces arguments of DetectTrails class at instantiation,
    sort of as **kwargs usually do. Example:

        >>> jobs = cj.Jobs(2, runs=runs, camcol=1, filter="i")
        >>> jobs.command = 'python3 -c "import detecttrails as dt;' +\\
                           'x = dt.DetectTrails($);'                +\\
                           'x.params_bright[\'debug\'] = True;'     +\\
                           'x.process()"\n'
        >>> jobs.create()

   which will get written as:

       python3 -c "import detecttrails as dt;
                   x = dt.DetectTrails(run=125,camcol=1,filter=i);
                   x.params_bright['debug'] = True;
                   x.process()"

    Again, the actual written command in the job#.dqs file would not
    look as user friendly as here. In the above example notice that
    quotation-marks are trice nested as follows:

        '    ("  (\'  \')   ")    '

        outter ': declares a python string, this string becomes the
                  command attribute of Jobs class.
        inner  ": encloses the string that will be executed by the
                  python -c command in the actual job#.dqs file.
        innermost \\': mark a new string that will get interpreted as
                      an argument inside the string you're sending to
                      python -c.

    This complication is here because the command has to be sent as a
    string therefore the quotation marks used inside should not escape
    the outsidemost quotations. General usefull guidelines:

     1) the outter-most quotation as single '' marks
     2) everything past "-c" flag in double quotation marks ""
     3) further quotation marks should be escaped single quotations.
     4) A EXPLICIT newline character should ALWAYS be present at the end.

    Same applies when executing a custom command for all runs:

        >>> jobs = cj.Jobs(500)
        >>> jobs.command = 'python3 -c "import detecttrails as dt;' +\\
                           'x = dt.DetectTrails($);'               +\\
                           'x.params_bright[\'debug\'] = True;'    +\\
                           'x.process()"  \n'
        >>> jobs.create()

    would produce jobs for all runs as in 1) usage case, where each
    job would execute the following command(s):

	    python3 -c "import detecttrails as dt;
	               x = dt.DetectTrails(run=273);
	               x.params_bright['debug'] = True;
                   x.process()"

    To see the list of all changable execution parameters of
    DetectTrails class see help(detecttrails).

3) Former approach covers most basics about how to get the most out of
   DetectTrails class on QSUB. However, described approaches still do
   not let you create jobs per frames. Sollution for this problem is to
   send in a list of Event or Frame objects. Read docs of results package
   to see how to instatiate those objects.

        >>> import results as res
        >>> r = res.Results(folderpath="/home/user/Desktop/res1/res")
        >>> jobs = cj.Jobs(5, runs=r)
        >>> jobs.create()
        Creating:
            6 jobs with 1372 runs per job
        Queue:     standard
        Wallclock: 24:00:00
        Cputime:   48:00:00
        Ppn:       3
        Path:      /home/user/Desktop/bitbucket/refactor/createjobs/jobs

   This time it's not runs you're executing but frames, therefore you
   can let a larger number of them per job; i.e. the invocation of
   DetectTrails now looks like:

	python3 -c "import detect_trails as dt;
               dt.DetectTrails(run=125,camcol=1,filter='i',
                               field=69).process()"
"""

#PHOTO_REDUX = os.path.join(os.path.expanduser("~"), "Desktop/boss/photo/redux")

def setup(photoreduxpath=None):
    """Sets up the required environmental paths for createjobs module.

      Parameters
    --------------
    photoreduxpath : The path to which PHOTO_REDUX env. var. will be set to.
        If nothing is given it will default to $BOSS/photoObj but is left
        configurable if SDSS conventions are not followed.
    """
    import os

    if photoreduxpath is None:
        try: bosspath = os.environ["BOSS"]
        except KeyError: bosspath = os.path.join(os.path.expanduser("~"), "Desktop/boss")
        photoreduxpath = os.path.join(bosspath, "photo/redux")

    os.environ["PHOTO_REDUX"] = photoreduxpath

from .createjobs import *

