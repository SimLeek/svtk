import vtk
import math
import colorsys


def array_to_vtk_transform(arr):
    # https://www.programcreek.com/python/example/12960/vtk.vtkTransform
    T = vtk.vtkTransform()
    matrix = vtk.vtkMatrix4x4()
    for i in range(0, 4):
        for j in range(0, 4):
            matrix.SetElement(i, j, arr[i, j])
    T.SetMatrix(matrix)
    return T


def hue_from_index(i):
    u = math.floor(math.log2(i + 1))
    v = i - 2**u + 1
    a = 0
    b = 360
    h = a + (v + 0.5) * ((b - a) / (2**u))

    c = colorsys.hsv_to_rgb(h / 360.0, 1.0, 1.0)
    return c
