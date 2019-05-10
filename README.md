# pylint-tta
Pylint plugin to check for *PyTorch* tensor type annotations

Tested on Python 3.6+

---

| Branch | Status |
| --- | --- |
| Master | ![](https://travis-ci.org/Popgun-Labs/pylint_tta.svg?branch=master) |

---


# Quickstart
```bash
pip install pylint pylint_tta

# Use pylint defaults with the plugin
pylint --load-plugins=pylint_tta <directory>

# Only use the plugin
pylint --load-plugins=pylint_tta --disable=all --enable=C9001,C9002,C9003,C9004,C9005,C9006 <directory>
```

# What it checks for

Given file `example1.py`,
```python
import astroid
import torch


def fail_func():
    a = torch.randn(5, 5, 5)

    a.unsqueeze_(1)
    b_fail = a.view(5, 25, -1)
    c_fail = a[:, : 1]
    c_fail: str = a[:, : 1]
    d_fail: str = a.unsqueeze(1)
    e_fail = a.unsqueeze_(1)

    return None


def pass_func():
    a = torch.randn(5, 5, 5)

    c_pass: ('w', 'h', 'b') = a[:, :, 1]
    d_pass: ('width', 'batch', 'height') = a.unsqueeze(1)

    return None
```

pylint-tta will yield:

```
************* Module example1
example1.py:8:4: C9005: In-place operation detected (disallow-inplace-tensor-operations)
example1.py:9:4: C9001: Missing type annotations on tensor operation (missing-tensor-annotations)
example1.py:10:4: C9003: Missing type annotations on slicing (missing-slicing-annotations)
example1.py:11:4: C9004: Invalid type annotations on slicing (invalid-slicing-annotations)
example1.py:12:4: C9002: Non tuple type annotations on tensor operation (invalid-tensor-annotations)
example1.py:13:4: C9006: Assignment on in-place operation detected (assignment-on-inplace-operations)
```

# Codes
| Code  | Name |
| ----- |:-------------|
| C9001 | missing-tensor-annotations |
| C9002 | invalid-tensor-annotations |
| C9003 | missing-slicing-annotations |
| C9004 | invalid-slicing-annotations |
| C9005 | disallow-inplace-tensor-operations |
| C9006 | assignment-on-inplace-operations |


# Dev
## Run Example
```
export PYTHONPATH=`pwd`; pylint --load-plugins=pylint_tta --disable=all --enable=C9001,C9002,C9003,C9004 example1.py
```

## Testing
```
pytest -s
```