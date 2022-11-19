def interest(*args, **kwargs):
    """Main interest calculation function."""
    # Signal that PyScript is alive by setting the ``Calculate``
    # button away from disabled.
    calculate_button = Element("calc")  # noqa
    # calculate_button.element.setAttribute("disabled")

    # Now get the various inputs
    element_principal = Element("principal")  # noqa
    element_rate = Element("interest_rate")  # noqa
    element_time = Element("time")  # noqa
    principal = float(element_principal.value)
    rate = float(element_rate.value)
    time = float(element_time.value)
    output1 = Element("simple_interest")  # noqa
    output2 = Element("compound_interest")  # noqa
    res1 = round(principal + (principal * rate * time))
    res2 = round(principal * ((1 + rate) ** time))
    output1.write(f"simple interest: {res1}")
    output2.write(f"compound interest: {res2}")


def setup():
    """When Pyodide starts up, enable the Calculate button."""
    calculate_button = Element("calc")  # noqa
    calculate_button.element.removeAttribute("disabled")
