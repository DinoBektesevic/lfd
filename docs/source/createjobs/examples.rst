Examples
--------

The simplest one is just specifying the number of jobs you want. Jobs will then
take the runs found in runlist.par (only reruns 301 are considered, special
reprocessings are not included), resolve the targeted data and create the jobs.

.. code-block:: python

     jobs = cj.Jobs(500)
     jobs.create()
     There are no runs to create jobs from.
       Creating jobs for all runs in runlist.par file.
  
     Creating:
       765 jobs with 1 runs per job
       Queue:     standard
  	 Wallclock: 24:00:00
  	 Cputime:   48:00:00
  	 Ppn:       3
  	 Path:      /home/user/Desktop/.../jobs
  
User will be notified about all important parameters that were set. Notice that
the default save path, queue, wallclock, ppn and cputime are set by default.
All parameters can be sent as keyword arguments at instantiation.

Notice also that we specified 500 jobs to be created but 765 jobs were created
instead. This is intentional. Jobs looks for the next larger whole number
divisor divisor to split the jobs between. It's better to send in more jobs
than to risk jobs failing.

Specifying certain runs by hand is possible by sending a list of runs of
interest:

.. code-block:: python

   runs = [125, 99, 2888, 1447]
   jobs = cj.Jobs(2, runs=runs)
   jobs.create()
   Creating:
	2 jobs with 2 runs per job
	Queue:     standard
    Wallclock: 24:00:00
    Cputime:   48:00:00
    Ppn:       3
    Path:      /home/user/Desktop/.../jobs

In both examples so far what is actually being written as a command that will
be executed at job submission:

.. code-block:: python

     python3 -c "import detecttrails as dt; dt.DetectTrails(run=2888).process()"

It is possible to edit the command that is going to be executed. Specifying
aditional keyword arguments to Jobs class helps you utilize DetectTrails class
run options. Sent kwargs are applied globaly across every job. It's not,
however, possible to specify separate kwargs for each command individually.

.. code-block:: python

   runs = [125, 99, 2888, 1447]
   jobs = cj.Jobs(2, runs=runs, camcol=1)
   jobs.create()

would create 2 jobs with 2 runs per job as the above example. The invocation of
the DetectTrails class would now look like:

.. code-block:: python

     python3 -c "import detect_trails as dt; dt.DetectTrails(run=125,camcol=1).process()"

Which would process only the camcol 1 of run 125. Actual written job#.dqs file
is not as readable/friendly as above examples. Another example:

.. code-block:: python

     jobs = cj.Jobs(2, runs=runs, camcol=1, filter="i")

would execute 2 jobs with following 2 calls to DetectTrails class:

.. code-block:: python

     python3 -c "import detect_trails as dt;
                 dt.DetectTrails(run=125,camcol=1,filter=i).process()"

See help on DetectTrails class for a complete set of allowable options.

To further fine tune your job behaviour it's possible to change the default
execution command to supply additional execution parameters. By default keyword
argument command is set to:

.. code-block:: python

     python3 -c "import detecttrails as dt; dt.DetectTrails($).process()"

Where "$" sign gets automatically expanded by the writer module. There should
also **ALWAYS** be a "$" character present in a command. "$" replaces arguments
of DetectTrails class at instantiation, sort of as `**kwargs` usually do.
Example:

.. code-block:: python

     jobs = cj.Jobs(2, runs=runs, camcol=1, filter="i")
     jobs.command = 'python3 -c "import detecttrails as dt;' +\\
                    'x = dt.DetectTrails($);'                +\\
                    'x.params_bright[\'debug\'] = True;'     +\\
                    'x.process()"\n'
     jobs.create()
  
which will get written as:

.. code-block:: python

     python3 -c "import detecttrails as dt; +\\
                 x = dt.DetectTrails(run=125,camcol=1,filter=i); +\\
                 x.params_bright['debug'] = True; +\\
                 x.process()"

Again, the actual written command in the job#.dqs file would not look as user
friendly and readabe as it is here. In the above example notice that quotation
marks are trice nested as follows::

  '    ("  (\'  \')   ")    '

where:

* outter ': declares a python string, this string becomes the command attribute
  of Jobs class.
* inner  ": encloses the string that will be executed by the python -c command
  in the actual job#.dqs file.
* innermost \\': mark a new string that will get interpreted as an argument
  inside the string you're sending to python -c.

This complication is here because the command has to be sent as a string
therefore the quotation marks used inside should not escape the outsidemost
quotations. General usefull guidelines:

1) the outter-most quotation as single '' marks
2) everything past "-c" flag in double quotation marks ""
3) further quotation marks should be escaped single quotations.
4) A EXPLICIT newline character should ALWAYS be present at the end.

.. tip::

   It is usually much simpler to declare the command as a multiline python comment
   by using the triple-quote mechanism:

   .. code-block:: python

        command = """python3 -c "import detecttrails as dt;
                   x = dt.DetectTrails($);
                   x.params_bright['debug']=True;
                   x.process()
        """
        jobs.command = command
        jobs.create()

   because there is no need to escape any of the special characters at all.


Same applies when executing a custom command for all runs:

.. code-block:: python

     jobs = cj.Jobs(500)
     jobs.command = 'python3 -c "import detecttrails as dt;' +\\
                    'x = dt.DetectTrails($);'               +\\
                    'x.params_bright[\'debug\'] = True;'    +\\
                    'x.process()"  \n\'
     jobs.create()

would produce jobs for all runs as in the first usage case, where each job
would execute the following command(s):

.. code-block:: python

     python3 -c "import detecttrails as dt; +\\
                x = dt.DetectTrails(run=273); +\\
                x.params_bright['debug'] = True; +\\
                x.process()"

To see the list of all changable execution parameters of DetectTrails class see
the tables of detection parameters described
:doc:`../detecttrails/paramsremovestars`, :doc:`../detecttrails/paramsbright`, and
:doc:`../detecttrails/paramsdim`.

Former approach covers most basics about how to get the most out of
DetectTrails class on QSUB. However, described approaches still do not let you
create jobs per frames. Sollution for this problem is to send in a list of
Event or Frame objects. Read docs of results package to see how to instatiate
those objects. Using them with createjobs module is quite straight-forward.

.. code-block:: python
  
     # mixing them in the same list/tuple is allowed
     r = [Event, Event, Frame, Event... ]
  
     jobs = cj.Jobs(5, runs=r)
     jobs.create()
       Creating:
           6 jobs with 1372 runs per job
       Queue:     standard
       Wallclock: 24:00:00
       Cputime:   48:00:00
       Ppn:       3
       Path:      /home/user/Desktop/.../jobs

This time it's not runs you're executing but frames, therefore you can let a
larger number of them per job; i.e. the invocation of DetectTrails now looks
like:

.. code-block:: python

     python3 -c "import detect_trails as dt;
                 dt.DetectTrails(run=125,camcol=1,filter='i', field=69).process()"
