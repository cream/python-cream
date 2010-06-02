def bus_name_to_path(bus_name):
    return '/' + bus_name.replace('.', '/')

def path_to_bus_name(path):
    return path.replace('/', '.').strip('.')


