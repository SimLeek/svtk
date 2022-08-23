def vtk_tk_anchor_left(vtk_win, tk_win):
    # tk rect (mostly)
    x = tk_win.winfo_x()
    y = tk_win.winfo_y()
    h = tk_win.winfo_height()

    mid_y = y + h / 2

    s = vtk_win.GetSize()
    new_x = x - s[0]
    new_y = mid_y - s[1] / 2
    vtk_win.SetPosition(int(new_x), int(new_y))


def vtk_tk_match_height(vtk_win, tk_win, keep_aspect=True):
    h = tk_win.winfo_height()

    s = vtk_win.GetSize()
    if keep_aspect:
        vtk_win.SetSize(int((h / s[1]) * s[0]), h)
    else:
        vtk_win.SetSize(s[0], h)
