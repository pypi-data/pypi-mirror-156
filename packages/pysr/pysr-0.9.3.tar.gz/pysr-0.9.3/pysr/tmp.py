from pysr import PySRRegressor
import numpy as np
import sympy

# X = np.random.rand(500, 1) * 1_000 - 500
X = np.random.rand(500, 1) * 20 - 10
# y = np.mod(x, 0.1) + np.mod(x, 0.15) * 3
X = np.sort(X, axis=0)
x = X
y = np.cos(x)

model = PySRRegressor(
    niterations=2000,
    maxsize=30,
    populations=40,
    ncyclesperiteration=1_000,
    binary_operators="+ * -".split(" "), #+ ["mod"],
    constraints={
        # "mod": (1, 1),
        "mod2pi": 3
    },
    unary_operators=["square", "mod2pi(x::T) where {T} = mod(x, 2 * T(3.1415926))"],
    warm_start=True,
    weight_randomize=0.1,
    extra_sympy_mappings={"mod2pi": lambda x: sympy.Mod(x, 2 * 3.1415926)},
)
model.fit(x, y)
