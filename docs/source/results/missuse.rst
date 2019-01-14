Common misuse patterns
======================

DetachedInstanceError
---------------------

.. code-block:: python
   :linenos:

   with results.session_scope() as s:
       e = s.query(results.Event).first()
   e.run
   >>> Traceback : sqlalchemy.orm.exc.DetachedInstanceError

* Incorrect use: session scope is meant to be used as a Unit of Work pattern,
  grouping multiple operations into a single transaction. Outside of that
  session scope all additional database operations should not be possible.
* Inconsistency: Primary purpose of the reusults package is to offer users
  interactive introspection of data. If data does not live outside a narrow
  scope it's very hard to inspect interactively.

Solution is to do all required work in the scope, or expunge the items.

.. todo:: Create a auto-expunge scope. Very hard to generalize expunging,
   especially for circular definitions.
    

Passing values in/out
---------------------

.. code-block:: python
   :linenos:

   <in a script>
   <some code>
   e = results.Event.query().first()
   <some additional code, perhaps even changing e>

Incorrect use: the session persist untill the session is automatically deleted.
This should not be done as explained in the Examples section. If only bits
of data need to go out either store them somewhere, or query directly only for
them and not the whole row.
  
.. code-block:: python
   :linenos:

   <in a script>
   <some code>
   with results.session_scope() as s:
       e = s.query(results.Event).first()
       x1, x2 = e.x1, e.x2
   <some further code using x1, x2>

   # or
   with results.session_scope() as s:
       x1, x2 = s.query(results.Event.x1, results.Event.x2).first()
   <some further code using x1, x2>

or if modification of DB data is required:

.. code-block:: python
   :linenos:

   <code calculating new values of x1, x2>
   with results.session_scope() as s:
       e = s.query(results.Event).first()
       e.x1, e.x2 = x1, x2
   <some further code>
