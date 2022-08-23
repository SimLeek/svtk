import vtk
from svtk.lib.input_util.global_util.key_combinations import GlobalKeyCombinationDictionary as KeyComboClass
import math

global_interactor_parent = None

global_camera = None
global_camera_renderWindow = None


class VTKKeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera, KeyComboClass):
    def __init__(self, camera, render_window, parent=None):
        KeyComboClass.__init__(self)
        # should work with else statement, but doesnt for some reason

        global global_interactor_parent
        if parent is not None:
            global_interactor_parent = parent
        else:
            global_interactor_parent = vtk.vtkRenderWindowInteractor()

        # DO NOT REMOVE GLOBAL INSTANTIATIONS!
        # due to problems with vtk losing data when moving python classes through c++, these globals muse be used to pass
        # data between class functions
        # todo: try different python class types, such as inheriting from 'object' and defining class variables

        global global_camera
        global_camera = camera

        global global_camera_renderWindow
        global_camera_renderWindow = render_window

        # todo: add screenshot function:
        #   http://www.vtk.org/Wiki/VTK/Examples/Python/Screenshot
        #   http://doc.qt.io/qt-4.8/qpixmap.html#grabWindow
        # todo: add window record function if ffmpeg is installed
        self.append_input_combinations(
            {
                "w": self._move_forward,
                "s": self._move_backward,
                "a": self._yaw_left,
                "d": self._yaw_right,
                "Shift_L": self._pitch_up,
                "space": self._pitch_down,
            }
        )

        self.AddObserver("KeyPressEvent", self.keyPress)
        self.AddObserver("KeyReleaseEvent", self.keyRelease)
        self.AddObserver("ExitEvent", self.exit_event)
        self.is_exited = False
        # self.RemoveObservers("LeftButtonPressEvent")
        # self.AddObserver("LeftButtonPressEvent", self.dummy_func)

        # todo: dummy func
        # self.RemoveObservers("RightButtonPressEvent")
        # self.AddObserver("RightButtonPressEvent", self.dummy_func_2)

    def camera_for_bounds(self, bounds):
        #  https://stackoverflow.com/a/28147726
        viewAngle = math.radians(global_camera.GetViewAngle())
        # todo: optionally, instead of min/max of xyz, find longest eiganvector of all points and use that. no sqrt(3).
        min_bounds = min(b[0] for b in bounds)
        max_bounds = min(b[1] for b in bounds)
        height = max_bounds - min_bounds
        d = height / viewAngle
        d = d * math.sqrt(3)  # ensure we get all points in 3d in view no matter what
        norm = global_camera.GetViewPlaneNormal()
        if sum(norm) == 0:
            norm = (-1.0, 0.0, 0.0)
        global_camera.SetFocalPoint(0, 0, 0)
        global_camera.SetPosition(norm[0] * d, norm[1] * d, norm[2] * d)

    def dummy_func(self, obj, ev):
        self.OnLeftButtonDown()

    def dummy_func_2(self, obj, ev):
        pass

    def exit_event(self):
        # super(vtk.vtkInteractorStyleTrackballCamera, self).ExitEvent()
        self.is_exited = True

    def _move_forward(self):
        # todo: change this to a velocity function with drag and let something else
        # interpolate the velocity over time
        norm = global_camera.GetViewPlaneNormal()
        pos = global_camera.GetPosition()
        global_camera.SetPosition(pos[0] - norm[0] * 10, pos[1] - norm[1] * 10, pos[2] - norm[2] * 10)
        global_camera.SetFocalPoint(pos[0] - norm[0] * 20, pos[1] - norm[1] * 20, pos[2] - norm[2] * 20)

    def _move_backward(self):
        # todo: change this to a velocity function with drag and let something else
        # interpolate the velocity over time
        norm = global_camera.GetViewPlaneNormal()
        pos = global_camera.GetPosition()
        global_camera.SetPosition(pos[0] + norm[0] * 10, pos[1] + norm[1] * 10, pos[2] + norm[2] * 10)
        global_camera.SetFocalPoint(pos[0] - norm[0] * 20, pos[1] - norm[1] * 20, pos[2] - norm[2] * 20)

    def _yaw_right(self):
        global_camera.Yaw(-10)
        global_camera_renderWindow.GetInteractor().Render()

    def _yaw_left(self):
        global_camera.Yaw(10)
        global_camera_renderWindow.GetInteractor().Render()

    def _pitch_up(self):
        global_camera.Pitch(10)
        global_camera_renderWindow.GetInteractor().Render()

    def _pitch_down(self):
        global_camera.Pitch(-10)
        global_camera_renderWindow.GetInteractor().Render()

    # noinspection PyPep8Naming
    def keyPress(self, obj, event):
        key = global_interactor_parent.GetKeySym()
        self.key_down(key)

    def keyRelease(self, obj, event):
        key = global_interactor_parent.GetKeySym()
        self.key_up(key)
