from .session import active


def get_variant(window_id=0):
    raise NotImplementedError


def page_down(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(82)


def arrow_down(window_id=0):
    raise NotImplementedError
    # Sessions._session.findById(f"wnd[{window_id}]").sendVKey(0)


def back(window_id=0):
    f3(window_id)


def execute(window_id=0):
    f8(window_id)


def f9(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(9)


def f4(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(4)


def f2(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(2)


def f12(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(12)


def f5(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(5)


def shift_f5(window_id=0):
    # shift + f3 = 15
    active.session.findById(f"wnd[{window_id}]").sendVKey(17)


def f6(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(6)


def f8(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(8)


def f3(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(3)
    # Sessions._session.findById(f"wnd[{window_id}]").sendVKey(0)


def save(window_id=0):
    raise NotImplementedError
    # Sessions._session.findById(f"wnd[{window_id}]").sendVKey(0)


def enter(window_id=0):
    active.session.findById(f"wnd[{window_id}]").sendVKey(0)
