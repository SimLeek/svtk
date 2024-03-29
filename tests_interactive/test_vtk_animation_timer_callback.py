from svtk.vtk_classes.vtk_animation_timer_callback import VTKAnimationTimerCallback
from svtk.vtk_classes.vtk_displayer import VTKDisplayer
import unittest
import random
from threading import Thread
from threading import Lock
import time

# 20 seconds is the approximate amount of time it would take to use up the extra memory and crash
test_time = 5


class TimedAnimationTester(VTKAnimationTimerCallback):
    def __init__(self):
        super(TimedAnimationTester, self).__init__()

        self.time_remaining = test_time

    def loop(self, obj, event):
        super(TimedAnimationTester, self).loop(obj, event)
        if self.time_remaining > 0:
            self.time_remaining -= self.loop_change_in_time
        else:
            self.time_remaining = test_time
            self.exit()
        pass


class TestAnimationTimerCallback(unittest.TestCase):
    def test_point_add(self):
        class PointAddTester(TimedAnimationTester):
            def loop(self, obj, event):
                super(PointAddTester, self).loop(obj, event)
                self.add_points(
                    [[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                    [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                )

        point_displayer = VTKDisplayer(PointAddTester)
        point_displayer.visualize()

    def test_point_add_thread(self):
        on = True

        def loop_add_points(cls):
            while on:
                cls.add_points(
                    [[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                    [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                )

        point_displayer = VTKDisplayer(TimedAnimationTester)
        t = Thread(target=loop_add_points, args=[point_displayer.callback_instance])
        t.start()
        point_displayer.visualize()
        on = False
        t.join()

    def test_point_add_get_all(self):
        # note: doesn't matter. VTK stops all python while the user is interacting, including threads
        #   points would need to be added from a separate program.
        points = []
        point_colors = []
        num_points = 0
        on = True
        l = Lock()

        vtk_num_points = 0

        class PointAddTester(TimedAnimationTester):
            def loop(self, obj, event):
                nonlocal points, vtk_num_points, num_points, point_colors, l
                l.acquire()
                super(PointAddTester, self).loop(obj, event)
                self.add_points(
                    points,
                    point_colors,
                )
                self.fit_points_in_cam()
                points.clear()
                point_colors.clear()
                vtk_num_points = len(self.get_points()[2]) // 2
                print(f"num pts: {num_points}")
                print(f"vtk pts: {vtk_num_points}")
                print(f"Num pts vs vtk pts: {num_points-vtk_num_points}")
                l.release()
                time.sleep(0)

        def loop_add_points():
            nonlocal num_points, points, point_colors, l
            while on:
                l.acquire()
                points.append([random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)])
                point_colors.append([random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)])
                num_points += 1
                l.release()
                time.sleep(0)

        point_displayer = VTKDisplayer(PointAddTester)
        t = Thread(target=loop_add_points, args=[])
        t.start()
        point_displayer.visualize()
        on = False
        t.join()

    def test_line_add(self):
        class LineAddTester(TimedAnimationTester):
            def loop(self, obj, event):
                super(LineAddTester, self).loop(obj, event)
                self.add_points(
                    [[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                    [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                )
                if self.points.GetNumberOfPoints() > 2:
                    self.add_lines(
                        [
                            2,
                            random.randint(0, self.points.GetNumberOfPoints() - 1),
                            random.randint(0, self.points.GetNumberOfPoints() - 1),
                        ],
                        [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                    )
                pass

        line_displayer = VTKDisplayer(LineAddTester)
        line_displayer.visualize()

    def test_line_del_all(self):
        class LineDelAllTester(TimedAnimationTester):
            def loop(self, obj, event):
                super(LineDelAllTester, self).loop(obj, event)
                self.add_points(
                    [[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                    [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                )
                if self.points.GetNumberOfPoints() > 2:
                    self.add_lines(
                        [
                            2,
                            random.randint(0, self.points.GetNumberOfPoints() - 1),
                            random.randint(0, self.points.GetNumberOfPoints() - 1),
                        ],
                        [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                    )
                if random.randint(1, 10) == 2 and len(self.line_id_array) > 0:
                    self.del_all_lines()

        line_displayer = VTKDisplayer(LineDelAllTester)
        line_displayer.visualize()

    def test_line_del(self):
        class LineDelTester(TimedAnimationTester):
            def loop(self, obj, event):
                super(LineDelTester, self).loop(obj, event)
                self.add_points(
                    [[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                    [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                )
                if self.points.GetNumberOfPoints() > 2:
                    self.add_lines(
                        [
                            2,
                            random.randint(0, self.points.GetNumberOfPoints() - 1),
                            random.randint(0, self.points.GetNumberOfPoints() - 1),
                        ],
                        [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                    )
                if random.randint(1, 2) == 2 and len(self.line_id_array) > 0:
                    line_to_del = random.randint(0, len(self.line_id_array) - 1)
                    self.del_lines([line_to_del])

        line_displayer = VTKDisplayer(LineDelTester)
        line_displayer.visualize()

    def test_point_del(self):
        class PointDelTester(TimedAnimationTester):
            def loop(self, obj, event):
                super(PointDelTester, self).loop(obj, event)
                self.add_points(
                    [[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                    [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]],
                )
                if self.points.GetNumberOfPoints() > 2:
                    point_to_delete = random.randint(0, self.points.GetNumberOfPoints())
                    self.del_points([point_to_delete])

        line_displayer = VTKDisplayer(PointDelTester)
        line_displayer.visualize()

    def test_point_field_add(self):
        class PointFieldTester(TimedAnimationTester):
            def at_start(self):
                self.add_point_field([20, 20, 2], [0, 1, 0], [0, 1, 0], [[int(128), int(66), int(21)]])

        line_displayer = VTKDisplayer(PointFieldTester)
        line_displayer.visualize()

    def test_set_all_point_colors(self):
        class PointColorSetTester(TimedAnimationTester):
            def at_start(self):
                self.start_color = [[int(128), int(66), int(21)]]
                self.add_point_field([20, 20, 2], [0, 1, 0], [0, 1, 0], [[int(128), int(66), int(21)]])

            def loop(self, obj, event):
                super(PointColorSetTester, self).loop(obj, event)
                if self.start_color[0][2] < 255:
                    self.start_color[0][2] += 5
                else:
                    self.start_color[0][2] = 0
                self.set_all_point_colors(self.start_color)

        line_displayer = VTKDisplayer(PointColorSetTester)
        line_displayer.visualize()

    def test_set_bg_color(self):
        class BGColorSetTester(TimedAnimationTester):
            def at_start(self):
                self.start_bg_color = [[int(128), int(66), int(21)]]

            def loop(self, obj, event):
                super(BGColorSetTester, self).loop(obj, event)
                if self.start_bg_color[0][1] < 255:
                    self.start_bg_color[0][1] += 5
                else:
                    self.start_bg_color[0][1] = 0
                self.set_bg_color(self.start_bg_color)

        line_displayer = VTKDisplayer(BGColorSetTester)
        line_displayer.visualize()


"""def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestAnimationTimerCallback("test_point_field_add"))
    return suite"""

if __name__ == "__main__":
    """res = unittest.TestResult()
    suite_to_run = suite()
    suite_to_run.run(res)
    print(res)
    print(res.errors)
    print(res.failures)
    print(res.skipped)"""
    unittest.main()
