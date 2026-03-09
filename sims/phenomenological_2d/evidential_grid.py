from __future__ import annotations

import numpy as np


class EvidentialGrid:
    """Dempster-Shafer evidential occupancy grid with three channels.

    grid[:, :, 0] -> m(O) occupied
    grid[:, :, 1] -> m(F) free
    grid[:, :, 2] -> m(Omega) unknown
    """

    OCC = 0
    FREE = 1
    UNKNOWN = 2

    def __init__(self, size: tuple[int, int] = (50, 50)) -> None:
        self.size = size
        self.grid = np.zeros((size[0], size[1], 3), dtype=float)
        self.reset()

    def reset(self) -> None:
        self.grid.fill(0.0)
        self.grid[:, :, self.UNKNOWN] = 1.0

    @staticmethod
    def inject_phenomenological_data(
        cam_free_prob: float,
        lid_occ_prob: float,
        *,
        is_depth_void: bool = False,
    ) -> tuple[float, float]:
        """Inject phenomenological measurements for transparent boundaries."""
        if is_depth_void:
            lid_occ_prob = 0.0
            cam_free_prob = 0.9
        return float(np.clip(cam_free_prob, 0.0, 1.0)), float(np.clip(lid_occ_prob, 0.0, 1.0))

    def get_cell(self, row: int, col: int) -> np.ndarray:
        return self.grid[row, col].copy()

    def set_cell(self, row: int, col: int, value: np.ndarray) -> None:
        self.grid[row, col] = self._normalize(value)

    @staticmethod
    def _normalize(v: np.ndarray) -> np.ndarray:
        v = np.clip(v.astype(float), 0.0, None)
        s = float(v.sum())
        if s <= 1e-12:
            return np.array([0.0, 0.0, 1.0], dtype=float)
        return v / s

    def door_evr(self, door_cells: list[tuple[int, int]]) -> float:
        values = [self.grid[r, c, self.FREE] for r, c in door_cells]
        return float(np.mean(values))

    def front_unknown(self, row: int, col: int) -> float:
        return float(self.grid[row, col, self.UNKNOWN])
