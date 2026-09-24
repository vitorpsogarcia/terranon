from entities.obstacle import Obstacle


class Structure(Obstacle):
    def __init__(
        self,
        position,
        *groups,
        width=64,
        height=64,
        is_ghost=False,
        build_cost=0,
        **kwargs,
    ):
        super().__init__(position, *groups, width=width, height=height, **kwargs)
        self.build_cost = build_cost
        self.is_ghost = is_ghost
        if (
            self.is_ghost
            and hasattr(self, "render_component")
            and self.render_component
        ):
            self.render_component.opacity = 128
            self._fixed_opacity = True
