"""Local python-for-android recipe for the project's existing bcrypt version.

The upstream p4a bcrypt recipe builds bcrypt 3.1.7 with CFFI.  Its setup.py
invokes CFFI while compiling on the host; CFFI 2.x requires pycparser there.
The upstream recipe only provisions setuptools, so pycparser is absent from
hostpython and the build fails before Android compilation completes.

Keep the upstream recipe's source/version/dependencies and add the missing
host-side build prerequisite.  This does not change bcrypt hashes or runtime
password verification.
"""
from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe


class BCryptRecipe(CompiledComponentsPythonRecipe):
    name = "bcrypt"
    version = "3.1.7"
    url = "https://github.com/pyca/bcrypt/archive/{version}.tar.gz"
    depends = ["openssl", "cffi"]
    call_hostpython_via_targetpython = False
    hostpython_prerequisites = ["setuptools", "cffi", "pycparser"]

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        openssl_recipe = Recipe.get_recipe("openssl", self.ctx)
        env["CFLAGS"] += openssl_recipe.include_flags(arch)
        env["LDFLAGS"] += openssl_recipe.link_dirs_flags(arch)
        env["LIBS"] = openssl_recipe.link_libs_flags()
        return env


recipe = BCryptRecipe()
