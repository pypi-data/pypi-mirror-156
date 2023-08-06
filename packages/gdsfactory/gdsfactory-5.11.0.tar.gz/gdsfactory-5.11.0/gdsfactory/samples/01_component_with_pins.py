"""You can add pins in a pin layer to clearly see the component ports.
"""

import gdsfactory as gf


@gf.cell
def straight_sample(length: float = 5.0, width: float = 1.0) -> gf.Component:
    """Returns straight with ports."""
    wg = gf.Component("straight_sample")
    wg.add_polygon([(0, 0), (length, 0), (length, width), (0, width)], layer=(1, 0))
    wg.add_port(
        name="o1", midpoint=(0, width / 2), width=width, orientation=180, layer=(1, 0)
    )
    wg.add_port(
        name="o2",
        midpoint=(length, width / 2),
        width=width,
        orientation=0,
        layer=(1, 0),
    )
    return wg


if __name__ == "__main__":
    wg = straight_sample(decorator=gf.add_pins.add_pins)

    # By default show adds pins, so you don't need it to show_ports
    wg.show(show_ports=False)
