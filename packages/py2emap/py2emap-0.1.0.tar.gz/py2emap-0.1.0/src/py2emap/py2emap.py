def dumps(obj):
    def flatten(obj, path):
        def escape(s):
            return s.replace('\\', '\\\\').replace('$#', '$\\#')

        def inner(obj, path):
            if isinstance(obj, dict):
                for k in obj:
                    v = obj[k]
                    inner(v, '.'.join([path, k]))
            elif isinstance(obj, list):
                flt.append(('.'.join([path, 'length']), str(len(obj)), 'number'))
                for i, v in enumerate(obj):
                    inner(v, ''.join([path, f'_{i}_']))
            else:
                if isinstance(obj, bool):
                    t = 'bool'
                    obj = str(obj).lower()
                elif isinstance(obj, int):
                    t = 'number'
                    obj = str(obj)
                elif isinstance(obj, str):
                    t = 'string'
                else:
                    raise RuntimeError
                flt.append((str(path), escape(obj), t))

        flt = []
        inner(obj, '')
        return [(x[0][1:], x[1], x[2]) if x[0][0] == '.' else (x[0], x[1], x[2]) for x in flt]

    flt = flatten(obj, '')
    res = f'l$#{len(flt)}$#' + \
          'v$#' + \
          ''.join([f'k{i}$#{v[0]}$#v{i}$#{v[1]}$#t{i}$#{v[2]}$#' for i, v in enumerate(flt)])
    return res
