def interest(*args, **kwargs):
    # Signal that PyScript is alive by setting the ``Calculate``
    # button away from disabled.
    ec = Element("calc")  # noqa

    # Now get the various inputs
    ep = Element("principal")  # noqa
    er = Element("interest_rate")  # noqa
    et = Element("time")  # noqa
    p = float(ep.value)
    r = float(er.value)
    t = float(et.value)
    output1 = Element("simple_interest")  # noqa
    output2 = Element("compound_interest")  # noqa
    res1 = round(p + (p * r * t))
    res2 = round(p * ((1 + r) ** t))
    output1.write("simple interest: " + str(res1))
    output2.write("compound interest: " + str(res2))


def setup():
    """When Pyodide starts up, enable the Calculate button."""
    ec = Element("calc")  # noqa
    ec.element.removeAttribute("disabled")
