import vtk
import tkinter
from svtk.vtk_classes.vtk_keypress_interactor_style import VTKKeyPressInteractorStyle
from typing import Optional


class VTKDisplayer:
    # adapted from:
    # http://www.vtk.org/Wiki/VTK/Examples/Python/GeometricObjects/Display/Point
    def __init__(self, callback_class, *args, **kwargs):
        self.points = vtk.vtkPoints()
        self.vertices = vtk.vtkCellArray()

        self.point_colors = vtk.vtkUnsignedCharArray()
        self.point_colors.SetNumberOfComponents(3)
        self.point_colors.SetName("Colors")

        self.lines = vtk.vtkCellArray()

        self.line_colors = vtk.vtkUnsignedCharArray()
        self.line_colors.SetNumberOfComponents(3)
        self.line_colors.SetName("Colors")

        # assert issubclass(callback_class, VTKAnimationTimerCallback)
        self.callback_class = callback_class
        self.callback_class_args = args
        self.callback_class_kwargs = kwargs
        self.callback_instance = self.callback_class(*self.callback_class_args, **self.callback_class_kwargs)

        if "point_size" in kwargs.keys():
            self.point_size = kwargs["point_size"]
        else:
            self.point_size = 6

        self.set_poly_data()

        self.callback_instance.points = self.points
        self.callback_instance.point_vertices = self.vertices
        self.callback_instance.points_poly = self.points_poly
        self.callback_instance.point_colors = self.point_colors
        self.callback_instance.lines = self.lines
        self.callback_instance.lines_poly = self.lines_poly
        self.callback_instance.line_colors = self.line_colors

        self.render_window_interactor = None

    def set_poly_data(self):

        self.points_poly = vtk.vtkPolyData()
        self.points_poly.SetPoints(self.points)
        self.points_poly.SetVerts(self.vertices)

        self.points_poly.GetPointData().SetScalars(self.point_colors)

        self.lines_poly = vtk.vtkPolyData()
        self.lines_poly.SetPoints(self.points)
        self.lines_poly.SetLines(self.lines)

        self.lines_poly.GetCellData().SetScalars(self.line_colors)

    def tk_visualize(self, loop=False, borders=False):
        if loop == True:
            raise ValueError("If you want tk and vtk to work together, you need to set up the main loop.")
        if borders == True:
            raise ValueError(
                "So far there's no way to tell if VTK was closed with the x button. "
                "Removing the borders is a quick fix"
            )
        self.visualize(loop=False, borders=False)

    def visualize(self, loop=True, borders=True):
        point_mapper = vtk.vtkPolyDataMapper()
        line_mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            point_mapper.SetInput(self.points_poly)
            line_mapper.SetInput(self.lines_poly)
        else:
            point_mapper.SetInputData(self.points_poly)
            line_mapper.SetInputData(self.lines_poly)

        point_actor = vtk.vtkActor()
        line_actor = vtk.vtkActor()

        point_actor.SetMapper(point_mapper)
        line_actor.SetMapper(line_mapper)
        point_actor.GetProperty().SetPointSize(self.point_size)
        # actor.GetProperty().SetPointColor

        self.renderer = vtk.vtkRenderer()

        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetBorders(borders)
        self.render_window.AddRenderer(self.renderer)
        self.render_window_interactor = vtk.vtkRenderWindowInteractor()
        interactor_style = VTKKeyPressInteractorStyle(
            camera=self.renderer.GetActiveCamera(),
            render_window=self.render_window,
            parent=self.render_window_interactor,
        )
        self.render_window_interactor.SetInteractorStyle(interactor_style)

        self.render_window_interactor.SetRenderWindow(self.render_window)

        self.renderer.AddActor(point_actor)
        self.renderer.AddActor(line_actor)

        # light brown = .6,.6,.4
        # light brown = .2,.2,.1
        # dark brown = .2, .1, 0
        # dusk = .05, .05, .1
        # calm blue sky = .1, .2, .4
        # day blue sky = .2, .4, .8
        # bright blue sky = .6, .8, 1.0 (bg attention activation)
        self.renderer.SetBackground(66 / 255.0, 132 / 255.0, 125 / 255.0)

        self.render_window.Render()

        self.render_window_interactor.Initialize()

        # allows adding/removing input functions, and mapping cam to points
        self.callback_instance.interactor_style = interactor_style
        self.callback_instance.renderer = self.renderer

        self.render_window_interactor.AddObserver("TimerEvent", self.callback_instance.execute)
        timer_id = self.render_window_interactor.CreateRepeatingTimer(10)
        if loop:
            self.render_window_interactor.Start()

            # cleanup after loop
            self.callback_instance.at_end()

    def process_events(self):
        if self.render_window_interactor is not None:
            self.render_window_interactor.ProcessEvents()

    def at_end(self):
        self.callback_instance.at_end()

    def visualize_ext_gl(self):
        expl = """
        Visualizing vtk in an external UI is possible, but would require a few weeks of work.
        You may need to override GetGenericDisplayId (otherwise how does vtk use the context?)
            You can see it done in the SDL2 implementation: https://gitlab.kitware.com/vtk/vtk/-/blob/master/Rendering/OpenGL2/vtkSDL2OpenGLRenderWindow.cxx
        you could provide an example external context for tkinter with pyopengltk: https://github.com/jonwright/pyopengltk
            The context there would be self.__context, which you may need to return from GetGenericDisplayId: https://github.com/jonwright/pyopengltk/blob/2df4fca4da54923f5dbfaa49c084e4857f2d6f67/pyopengltk/win32.py
        Alternatively, vtk could just get the "current" context, but then you need to guarantee that.
        """
        raise NotImplementedError(expl)
