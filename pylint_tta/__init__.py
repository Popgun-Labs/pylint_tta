import astroid

from astroid.node_classes import Assign, AnnAssign, Expr

from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker


class TensorTypeAnnotationsChecker(BaseChecker):
    __implements__ = (IAstroidChecker, )

    name = 'tensor-annotations'

    msgs = {
        'C9001': (
            'Missing type annotations on tensor operation',
            'missing-tensor-annotations',
            'Emitted when a tensor reshaping operation is performed and no type annotation is attached'
        ),
        'C9002': (
            'Non tuple type annotations on tensor operation',
            'invalid-tensor-annotations',
            'Emitted when a tensor reshaping operation is performed and a non-tuple type annotation is attached'
        ),
        'C9003': (
            'Missing type annotations on slicing',
            'missing-slicing-annotations',
            'Emitted when a slicing operation is performed and no type annotation is attached'
        ),
        'C9004': (
            'Invalid type annotations on slicing',
            'invalid-slicing-annotations',
            'Emitted when a slicing operation is performed and a non-tuple type annotation is attached'
        ),
        'C9005': (
            'In-place operation detected',
            'disallow-inplace-tensor-operations',
            'Emitted when an inplace tensor operation is performed'
        ),
        'C9006': (
            'Assignment on in-place operation detected',
            'assignment-on-inplace-operations',
            'Emitted when an assignment occurs on an inplace operation'
        )
    }

    priority = -1

    # Want type annotations on these tensor operation names
    # also disllow inplace-operations
    tensor_op_func_attrnames = [
        'squeeze',
        'view',
        'transpose',
        'permute',
        'unsqueeze',
        'split',
        'cat',
        'gather',
        'index_select',
        'masked_select',
        'narrow',
        'nonzero',
        'reshape',
        't',
        'mean',
        'sum',
        'take',
        'unbind',
        'unfold',
        'chunk',
        'stack'
    ]

    inplace_op_func_attrnames = [
        'squeeze_',
        'view_',
        'transpose_',
        'permute_',
        'unsqueeze_',
        'split_',
        'cat_',
        'gather_',
        'index_select_',
        'masked_select_',
        'narrow_',
        'nonzero_',
        'reshape_',
        't_',
        'mean_',
        'sum_',
        'take_',
        'unbind_',
        'unfold_',
        'chunk_',
        'stack_'
    ]

    def visit_functiondef(self, node):
        for n in node.body:
            # Must have value
            if not hasattr(n, 'value'):
                return

            # Function calls
            if hasattr(n.value, 'func') and hasattr(n.value.func, 'attrname'):
                if type(n) == Expr:
                    if n.value.func.attrname in self.inplace_op_func_attrnames:
                        self.add_message(
                            'disallow-inplace-tensor-operations', node=n
                        )

                if type(n) == Assign:
                    if n.value.func.attrname in self.tensor_op_func_attrnames:
                        self.add_message('missing-tensor-annotations', node=n)

                    if n.value.func.attrname in self.inplace_op_func_attrnames:
                        self.add_message(
                            'assignment-on-inplace-operations', node=n)

            # Function calls with (invalid) annotations
            if hasattr(n, 'annotation') and hasattr(n.value, 'func') and hasattr(n.value.func, 'attrname'):
                if type(n) == AnnAssign:
                    # Check if tensor annotations are valid
                    if n.value.func.attrname in self.tensor_op_func_attrnames:
                        if not hasattr(n.annotation, 'elts'):
                            self.add_message(
                                'invalid-tensor-annotations', node=n)

                        elif type(n.annotation.elts) is not list:
                            self.add_message(
                                'invalid-tensor-annotations', node=n)

                    # In-place operations
                    if n.value.func.attrname in self.inplace_op_func_attrnames:
                        self.add_message(
                            'assignment-on-inplace-operations', node=n
                        )

            # Slicing
            if hasattr(n.value, 'slice'):
                if type(n) == Assign:
                    self.add_message('missing-slicing-annotations', node=n)

            # Slicing with (invalid) annotations
            if hasattr(n, 'annotation') and hasattr(n.value, 'slice'):
                if type(n) == AnnAssign:
                    if not hasattr(n.annotation, 'elts'):
                        self.add_message(
                            'invalid-slicing-annotations', node=n)

                    elif type(n.annotation.elts) is not list:
                        self.add_message(
                            'invalid-slicing-annotations', node=n)


def register(linter):
    linter.register_checker(TensorTypeAnnotationsChecker(linter))
