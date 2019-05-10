import os

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


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'example1.py')

    with open(filepath, 'r') as f:
        source_code = f.read()

        print(astroid.parse(source_code))
