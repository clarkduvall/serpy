***********
Performance
***********

**serpy** was compared against two other popular serializer frameworks:

  - `marshmallow <http://marshmallow.readthedocs.org>`_
  - `Django Rest Framework Serializers
    <http://www.django-rest-framework.org/api-guide/serializers/>`_

These graphs show the results. The benchmark scripts are found in the
`benchmarks <https://github.com/clarkduvall/serpy/tree/master/benchmarks>`_
directory in the **serpy** `GitHub repository
<https://github.com/clarkduvall/serpy>`_. Run these benchmarks yourself with:

.. code-block:: bash

   $ git clone https://github.com/clarkduvall/serpy.git && cd serpy
   $ # make a virtualenv with your preferred method
   $ pip install -r benchmarks/requirements.txt
   $ python benchmarks/bm_simple.py  # or...
   $ python benchmarks/bm_complex.py

Results
=======

These benchmarks were run on a Lenovo T530 with a 2-core 2.5 GHz i5 processor
and 8G of memory.

Simple Benchmark
----------------

This benchmark serializes simple objects that have a single field.

.. image:: _static/bm_simple_time.png

.. image:: _static/bm_simple_objects.png

Complex Benchmark
-----------------

This benchmark serializes nested objects with multiple fields of different
types.

.. image:: _static/bm_complex_time.png

.. image:: _static/bm_complex_objects.png


Data
----

.. csv-table:: bm_simple.py time taken (in seconds)
   :header: "# objects","Django Rest Framework","marshmallow","serpy"

   10000,0.2414798737,0.1299209595,0.006773948669
   20000,0.4704430103,0.2919068336,0.01343297958
   30000,0.7049410343,0.4186880589,0.02005600929
   40000,0.9448800087,0.5500640869,0.02748799324
   50000,1.196242809,0.6857171059,0.03510689735
   60000,1.513856888,0.7901060581,0.04155898094
   70000,1.695443153,0.9453551769,0.05080986023
   80000,1.943806887,1.060761929,0.06843280792
   90000,2.189687967,1.189263105,0.07787084579
   100000,2.445794821,1.329367876,0.0864470005

.. csv-table:: bm_simple.py objects per second
   :header: "# objects","Django Rest Framework","marshmallow","serpy"

   10000,41411.31867,76969.87492,1476243.841
   20000,42513.11968,68515.01128,1488872.954
   30000,42556.7509,71652.38981,1495811.034
   40000,42333.41761,72718.79941,1455180.8
   50000,41797.53442,72916.36678,1424221.557
   60000,39633.86532,75939.1722,1443731.262
   70000,41287.14069,74046.2439,1377685.349
   80000,41156.35177,75417.48798,1169029.92
   90000,41101.74662,75677.11433,1155759.888
   100000,40886.50411,75223.72234,1156778.135

.. csv-table:: bm_complex.py time taken (in seconds)
   :header: "# objects","Django Rest Framework","marshmallow","serpy"

   100,0.06559991837,0.06082081795,0.003219127655
   200,0.1476380825,0.1639349461,0.006608009338
   300,0.171423912,0.1755890846,0.009553909302
   400,0.2272388935,0.2300069332,0.01268196106
   500,0.3147311211,0.2876529694,0.0157828331
   600,0.3746049404,0.3528439999,0.01907610893
   700,0.3846490383,0.4465448856,0.02250695229
   800,0.4846799374,0.4638659954,0.02613210678
   900,0.5376219749,0.5233578682,0.02945303917
   1000,0.5961399078,0.5829660892,0.03282499313

.. csv-table:: bm_complex.py objects per second
   :header: "# objects","Django Rest Framework","marshmallow","serpy"

   100,1524.392141,1644.173876,31064.3164
   200,1354.664031,1219.996131,30266.30105
   300,1750.047566,1708.534449,31400.75863
   400,1760.262048,1739.078011,31540.86329
   500,1588.65764,1738.205592,31679.99033
   600,1601.687365,1700.468196,31452.95522
   700,1819.840765,1567.591574,31101.50104
   800,1650.573788,1724.636011,30613.68173
   900,1674.038715,1719.664602,30557.11823
   1000,1677.458574,1715.365642,30464.59129
