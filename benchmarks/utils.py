from rest_framework import serializers as rf_serializers
import serpy
import time


class Obj(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, dict):
                v = Obj(**v)
            if isinstance(v, list):
                v = [Obj(**attrs) for attrs in v]
            setattr(self, k, v)


def write_csv(name, data, drf, marshmallow, serpy, size):
    repetitions = 10
    with open('{0}.csv'.format(name), 'w+') as f:
        f.write(',DRF,Marshmallow,serpy\n')
        for i in range(10 * size, 101 * size, 10 * size):
            f.write(str(i * repetitions))
            for serializer in (drf, marshmallow, serpy):
                f.write(',')
                f.write(str(benchmark(serializer, repetitions, i, data=data)))
            f.write('\n')


def benchmark(serializer_fn, repetitions, num_objs=1, data=None):
    total_objs = repetitions * num_objs
    if not isinstance(serializer_fn, type):
        library = 'Marshmallow'
    elif issubclass(serializer_fn, serpy.Serializer):
        library = 'serpy'
    elif issubclass(serializer_fn, rf_serializers.Serializer):
        library = 'Django Rest Framework'
    print('Serializing {} objects using {}'.format(total_objs, library))

    if data is None:
        data = {}

    objs = [Obj(**data) for i in range(num_objs)]
    many = num_objs > 1
    if not many:
        objs = objs[0]

    t1 = time.time()
    for i in range(repetitions):
        serializer_fn(objs, many=many).data
    total_time = time.time() - t1
    print('Total time: {}'.format(total_time))
    print('Objs/s    : {}\n'.format(int(total_objs / total_time)))
    return total_time
