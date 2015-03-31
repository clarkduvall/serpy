from rest_framework import serializers as rf_serializers
import serpy
import time


class Obj(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def write_csv(name, data, drf, marshmallow, serpy):
    with open('{}.csv'.format(name), 'w+') as f:
        f.write(',DRF,Marshmallow,serpy\n')
        for i in range(500, 10001, 500):
            f.write(str(i))
            for serializer in (drf, marshmallow, serpy):
                f.write(',')
                f.write(str(benchmark(serializer, 10, i, data=data)))
            f.write('\n')


def benchmark(serializer_fn, times, num_objs=1, data=None):
    total_objs = times * num_objs
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
    for i in range(times):
        serializer_fn(objs, many=many).data
    total_time = time.time() - t1
    print('Total time: {}'.format(total_time))
    print('Objs/s    : {}\n'.format(int(total_objs / total_time)))
    return total_time
