
from .arithmetic import *
from .constant import *
from .delete import *
from .logical import *
from .loop import *
from .misc import *

all_mixins = [
    ArithmeticOperatorReplacement,
    NumberReplacement,
    StringReplacement,
    UnaryOperatorDeletion,
    StatementDeletion,
    ConditionalOperatorNegation,
    LogicalOperatorReplacement,
    BitwiseOperatorReplacement,
    ComparisonOperatorReplacement,
    BreakContinueReplacement,
    ZeroIterationLoop,
    OneIterationLoop,
    ReverseIterationLoop,
    SliceIndexRemove,
]
