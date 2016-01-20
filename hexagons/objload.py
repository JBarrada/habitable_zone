class OBJ:
    vertices = []
    vertex_normals = []
    vertex_texture = []
    faces = []

    vertexbufferdata = []
    normalbufferdata = []
    texturebufferdata = []


def load(filename):
    f = open(filename)

    obj = OBJ()

    for line in f:
        if line[:2] == 'v ':
            comps = line[2:].strip().split(' ')
            vertex = (float(comps[0]), float(comps[1]), float(comps[2]))
            obj.vertices += [vertex]

        if line[:2] == 'vt':
            comps = line[2:].strip().split(' ')
            texture = (float(comps[0]), float(comps[1]))
            obj.vertex_texture += [texture]

        if line[:2] == 'vn':
            comps = line[2:].strip().split(' ')
            normal = (float(comps[0]), float(comps[1]), float(comps[2]))
            obj.vertex_normals += [normal]

        if line[:2] == 'f ':
            comps = line[2:].strip().split(' ')
            face = []
            for comp in comps:
                vcomps = comp.split('/')
                face += [(int(vcomps[0]) if vcomps[0] != '' else -1,
                          int(vcomps[1]) if vcomps[1] != '' else -1,
                          int(vcomps[2]) if vcomps[2] != '' else -1)]
            obj.faces += [face]

        for face in obj.faces:
            for vertex in face:
                v = obj.vertices[vertex[0]-1][:] if vertex[0] != -1 else (0, 0, 0)
                t = obj.vertex_texture[vertex[1]-1][:] if vertex[1] != -1 else (0, 0)
                n = obj.vertex_normals[vertex[2]-1][:] if vertex[2] != -1 else (0, 0, 0)

                obj.vertexbufferdata += [v[0], v[1], v[2]]
                obj.normalbufferdata += [n[0], n[1], n[2]]
                obj.texturebufferdata += [t[0], t[1]]

    return obj
