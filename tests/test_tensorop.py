import pytest

import astroid
import pylint_tta

from pylint.testutils import CheckerTestCase, Message


class TestTensorTypeAnnotationsChecker(CheckerTestCase):
    CHECKER_CLASS = pylint_tta.TensorTypeAnnotationsChecker

    def test_missing_type_annotations(self):
        module = astroid.parse("""
        import torch

        def test_tensor_op():
            a = torch.randn(5, 5, 5)

            b = a.view(5, 25, -1)

            c = b.squeeze(2)

            d = c[:, 1, :]

            return c
        """)

        func_node = module.body[-1]

        self.checker.visit_functiondef(func_node)

        release_messages = self.linter.release_messages()

        assert release_messages[0].msg_id == 'missing-tensor-annotations'
        assert release_messages[0].node == func_node.body[1]

        assert release_messages[1].msg_id == 'missing-tensor-annotations'
        assert release_messages[1].node == func_node.body[2]

    def test_invalid_type_annotations(self):
        module = astroid.parse("""
        import torch

        def test_tensor_op():
            a = torch.randn(5, 5, 5)

            b: ('width', 'batch', 'height') = a.view(5, 25, -1)

            c: 'height' = b.squeeze(2)

            return c
        """)

        func_node = module.body[-1]

        self.checker.visit_functiondef(func_node)

        release_messages = self.linter.release_messages()

        assert release_messages[0].msg_id == 'invalid-tensor-annotations'
        assert release_messages[0].node == func_node.body[2]

    def test_inplace_operations(self):
        module = astroid.parse("""
        import torch

        def test_tensor_op():
            a = torch.randn(5, 5, 5)

            a.view_(5, 25, -1)

            a.squeeze_(2)

            return a
        """)

        func_node = module.body[-1]

        self.checker.visit_functiondef(func_node)

        release_messages = self.linter.release_messages()

        assert release_messages[0].msg_id == 'disallow-inplace-tensor-operations'
        assert release_messages[0].node == func_node.body[1]

        assert release_messages[1].msg_id == 'disallow-inplace-tensor-operations'
        assert release_messages[1].node == func_node.body[2]

    def test_slicing_operations(self):
        module = astroid.parse("""
        import torch

        def test_tensor_op():
            a = torch.randn(5, 5, 5)

            b = a[:, :, -1]
            b: str = a[:, :, -1]
            b: ('width', 'height', 'batch') = a[:, :, -1]

            return a
        """)

        func_node = module.body[-1]

        self.checker.visit_functiondef(func_node)

        release_messages = self.linter.release_messages()

        assert release_messages[0].msg_id == 'missing-slicing-annotations'
        assert release_messages[0].node == func_node.body[1]

        assert release_messages[1].msg_id == 'invalid-slicing-annotations'
        assert release_messages[1].node == func_node.body[2]

    def test_inplace_assignment_operations(self):
        module = astroid.parse("""
        import torch

        def test_tensor_op():
            a = torch.randn(5, 5, 5)

            b = a.view_(-1)

            return None
        """)

        func_node = module.body[-1]

        self.checker.visit_functiondef(func_node)

        release_messages = self.linter.release_messages()

        assert release_messages[0].msg_id == 'assignment-on-inplace-operations'
        assert release_messages[0].node == func_node.body[1]


    def test_all(self):
        module = astroid.parse("""
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
        """)

        fail_func_node = module.body[1]
        pass_func_node = module.body[2]

        self.checker.visit_functiondef(pass_func_node)
        release_messages = self.linter.release_messages()
        assert len(release_messages) == 0

        self.checker.visit_functiondef(fail_func_node)
        release_messages = self.linter.release_messages()

        assert release_messages[0].msg_id == 'disallow-inplace-tensor-operations'
        assert release_messages[0].node == fail_func_node.body[1]

        assert release_messages[1].msg_id == 'missing-tensor-annotations'
        assert release_messages[1].node == fail_func_node.body[2]

        assert release_messages[2].msg_id == 'missing-slicing-annotations'
        assert release_messages[2].node == fail_func_node.body[3]

        assert release_messages[3].msg_id == 'invalid-slicing-annotations'
        assert release_messages[3].node == fail_func_node.body[4]

        assert release_messages[4].msg_id == 'invalid-tensor-annotations'
        assert release_messages[4].node == fail_func_node.body[5]

        assert release_messages[5].msg_id == 'assignment-on-inplace-operations'
        assert release_messages[5].node == fail_func_node.body[6]