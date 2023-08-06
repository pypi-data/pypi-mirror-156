rm -rf target/*
maturin build
pip uninstall target/wheels/*.whl
pip install target/wheels/*.whl
