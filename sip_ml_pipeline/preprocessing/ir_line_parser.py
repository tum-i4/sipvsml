import json
import re

import numpy as np


"""
    REFERENCE FROM https://llvm.org/docs/LangRef.html
"""


CMD_CLEANUP_PAD = 'cleanuppad'
CMD_LANDING_PAD = 'landingpad'
CMD_VA_ARG = 'va_arg'
CMD_INSERT_VALUE = 'insertvalue'
CMD_EXTRACT_VALUE = 'extractvalue'
CMD_SHUFFLE_VECTOR = 'shufflevector'
CMD_INSERT_ELEMENT = 'insertelement'
CMD_EXTRACT_ELEMENT = 'extractelement'
CMD_ASHR = 'ashr'
CMD_FREM = 'frem'
CMD_UDIV = 'udiv'
CMD_FNEG = 'fneg'
CMD_FREEZE = 'freeze'
CMD_PHI = 'phi'
CMD_ADDRESS_SPACE_CAST = 'addrspacecast'
CMD_PTR_TO_INT = 'ptrtoint'
CMD_SI_TO_FP = 'sitofp'
CMD_FENCE = 'fence'
CMD_CLEANUP_RET = 'cleanupret'
CMD_CATCH_RET = 'catchret'
CMD_CALLBR = 'callbr'
CMD_INVOKE = 'invoke'
CMD_INDIRECT_BR = 'indirectbr'
CMD_LSHR = 'lshr'
CMD_AND = 'and'
CMD_FPTRUNC = 'fptrunc'
CMD_FPEXT = 'fpext'
CMD_FSUB = 'fsub'
CMD_FDIV = 'fdiv'
CMD_FMUL = 'fmul'
CMD_FADD = 'fadd'
CMD_FCOMP = 'fcmp'
CMD_INT_TOP_TR = 'inttoptr'
CMD_SDIV = 'sdiv'
CMD_SREM = 'srem'
CMD_SELECT = 'select'
CMD_TRUNC = 'trunc'
CMD_SWITCH = 'switch'
CMD_SHL = 'shl'
CMD_XOR = 'xor'
CMD_OR = 'or'
CMD_UREM = 'urem'
CMD_MUL = 'mul'
CMD_SUB = 'sub'
CMD_SEXT = 'sext'
CMD_BITCAST = 'bitcast'
CMD_UNREACHABLE = 'unreachable'
CMD_RET = 'ret'
CMD_GET_ELEMENT_PTR = 'getelementptr'
CMD_ADD = 'add'
CMD_ZEXT = 'zext'
CMD_BR = 'br'
CMD_ICMP = 'icmp'
CMD_LOAD = 'load'
CMD_STORE = 'store'
CMD_ALLOC = 'alloca'
CMD_CALL = 'call'
CMD_RESUME = 'resume'
CMD_CATCH_SWITCH = 'catchswitch'


VOID_TY = 'voidTy'
POINTER_TY = 'pointerTy'
INTEGER_TY = 'integerTy'
STRUCT_TY = 'structTy'
VECTOR_TY = 'vectorTy'
FLOAT_TY = 'floatTy'


ARG_POINTER = 'pointer'
ARG_CONSTANT = 'constant'
ARG_FUNCTION = 'function'
ARG_VARIABLE = 'variable'
ARG_LABEL = 'label'


def parse_args(line):
    spl = [x for x in line.split(', ') if not x.startswith('!')]
    args = []
    for arg_txt in spl:
        args.append(parse_arg(arg_txt))
    return args


def parse_arg(arg_txt):
    if '%' in arg_txt:
        if '*' in arg_txt:
            return ARG_POINTER
        else:
            return ARG_VARIABLE
    else:
        return ARG_CONSTANT


def parse_cmp_args(txt_args):
    args = []
    for txt_arg in txt_args:
        if '%' in txt_arg:
            args.append(ARG_VARIABLE)
        else:
            args.append(ARG_CONSTANT)
    return args


def find_txt_args(line):
    return re.findall(r'i\d{1,2}\*{0,4} [@|%]?[a-zA-Z0-9_]+', line)


def parse_label_args(line):
    args = []
    spl = [x for x in line.split(', ') if not x.startswith('!')]
    for txt_arg in spl:
        if 'label' in txt_arg:
            args.append(ARG_LABEL)
        else:
            args.append(ARG_VARIABLE)
    return args


def parse_type(text):
    if text.endswith('*'):
        return POINTER_TY
    if text.startswith('i'):
        return INTEGER_TY
    if 'float' in text or 'double' in text or 'x86_fp' in text:
        return FLOAT_TY
    if '<' in text:
        return VECTOR_TY
    if '{' in text:
        return STRUCT_TY
    raise RuntimeError(text)


class Command:
    def __init__(self, name, line) -> None:
        self.type = None
        self.args = None
        self.name = name
        self.line = line
        self._parse_line()

    def _parse_line(self):
        raise NotImplementedError()

    def __repr__(self) -> str:
        args_str = '  '.join(self.args)
        return f'{self.name}  {self.type}  {args_str}'.strip()

    def __str__(self) -> str:
        return repr(self)


class AllocCommand(Command):
    """
    <result> = alloca [inalloca] <type> [, <ty> <NumElements>] [, align <alignment>] [, addrspace(<num>)]
        ; yields type addrspace(num)*:result

    %ptr = alloca i32                             ; yields i32*:ptr
    %ptr = alloca i32, i32 4                      ; yields i32*:ptr
    %ptr = alloca i32, i32 4, align 1024          ; yields i32*:ptr
    %ptr = alloca i32, align 1024                 ; yields i32*:ptr
    """
    def _parse_line(self):
        self.type = POINTER_TY
        self.args = [ARG_CONSTANT]


class CallCommand(Command):
    """
    <result> = [tail | musttail | notail ] call [fast-math flags] [cconv] [ret attrs] [addrspace(<num>)]
           <ty>|<fnty> <fnptrval>(<function args>) [fn attrs] [ operand bundles ]

    %retval = call i32 @test(i32 %argc)
    call i32 (i8*, ...)* @printf(i8* %msg, i32 12, i8 42)        ; yields i32
    %X = tail call i32 @foo()                                    ; yields i32
    %Y = tail call fastcc i32 @foo()  ; yields i32
    call void %foo(i8 97 signext)

    %struct.A = type { i32, i8 }
    %r = call %struct.A @foo()                        ; yields { i32, i8 }
    %gr = extractvalue %struct.A %r, 0                ; yields i32
    %gr1 = extractvalue %struct.A %r, 1               ; yields i8
    %Z = call void @foo() noreturn                    ; indicates that %foo never returns normally
    %ZZ = call zeroext i32 @bar()                     ; Return value is %zero extended
    """
    def _parse_line(self,):
        ret_type = self._parse_ret_type()
        args = self._parse_args()
        self.type = ret_type
        self.args = args

    def _parse_ret_type(self):
        spl = self.line.split()[1:]
        return {
            'void': VOID_TY
        }.get(spl[0], INTEGER_TY)

    def _parse_args(self):
        args_text = self.line[self.line.find('(') + 1: self.line.find(')')].strip()
        res = []
        if args_text != '':
            res = parse_args(args_text)

        res.append(ARG_FUNCTION)
        return res


class StoreCommand(Command):
    """
    store [volatile] <ty> <value>, <ty>* <pointer>[, align <alignment>][, !nontemporal !<nontemp_node>]
        [, !invariant.group !<empty_node>]        ; yields void
    store atomic [volatile] <ty> <value>, <ty>* <pointer> [syncscope("<target-scope>")] <ordering>, align <alignment>
        [, !invariant.group !<empty_node>] ; yields void
    !<nontemp_node> = !{ i32 1 }
    !<empty_node> = !{}

    %ptr = alloca i32                               ; yields i32*:ptr
    store i32 3, i32* %ptr                          ; yields void
    %val = load i32, i32* %ptr                      ; yields i32:val = i32 3
    """

    def _parse_line(self):
        self.type = VOID_TY
        args = []
        txt_args = find_txt_args(self.line)
        for txt_arg in txt_args:
            if '%' in txt_arg or '@' in txt_arg:
                if '*' in txt_arg:
                    args.append(ARG_POINTER)
                else:
                    args.append(ARG_VARIABLE)
            else:
                args.append(ARG_CONSTANT)
        self.args = args


class FenceCommand(Command):
    """
    fence [syncscope("<target-scope>")] <ordering>  ; yields void

    fence acquire                                        ; yields void
    fence syncscope("singlethread") seq_cst              ; yields void
    fence syncscope("agent") seq_cst                     ; yields void
    """
    def _parse_line(self):
        self.type = VOID_TY
        self.args = []


class CmpXChgCommand(Command):
    """
    cmpxchg [weak] [volatile] <ty>* <pointer>, <ty> <cmp>, <ty> <new> [syncscope("<target-scope>")]
        <success ordering> <failure ordering>[, align <alignment>] ; yields  { ty, i1 }

    entry:
      %orig = load atomic i32, i32* %ptr unordered, align 4                      ; yields i32
      br label %loop

    loop:
      %cmp = phi i32 [ %orig, %entry ], [%value_loaded, %loop]
      %squared = mul i32 %cmp, %cmp
      %val_success = cmpxchg i32* %ptr, i32 %cmp, i32 %squared acq_rel monotonic ; yields  { i32, i1 }
      %value_loaded = extractvalue { i32, i1 } %val_success, 0
      %success = extractvalue { i32, i1 } %val_success, 1
      br i1 %success, label %done, label %loop

    done:
      ...
    """
    def _parse_line(self):
        raise NotImplementedError()


class AtomicRmwCommand(Command):
    """
    atomicrmw [volatile] <operation> <ty>* <pointer>, <ty> <value> [syncscope("<target-scope>")]
        <ordering>[, align <alignment>]  ; yields ty

    %old = atomicrmw add i32* %ptr, i32 1 acquire                        ; yields i32

    """
    def _parse_line(self):
        raise NotImplementedError()


class LoadCommand(Command):
    """
    <result> = load [volatile] <ty>, <ty>* <pointer>[, align <alignment>][, !nontemporal !<nontemp_node>]
    [, !invariant.load !<empty_node>][, !invariant.group !<empty_node>][, !nonnull !<empty_node>]
    [, !dereferenceable !<deref_bytes_node>][, !dereferenceable_or_null !<deref_bytes_node>][, !align !<align_node>]
    [, !noundef !<empty_node>]

    <result> = load atomic [volatile] <ty>, <ty>* <pointer> [syncscope("<target-scope>")] <ordering>,
        align <alignment> [, !invariant.group !<empty_node>]
    !<nontemp_node> = !{ i32 1 }
    !<empty_node> = !{}
    !<deref_bytes_node> = !{ i64 <dereferenceable_bytes> }
    !<align_node> = !{ i64 <value_alignment> }


    %ptr = alloca i32                               ; yields i32*:ptr
    store i32 3, i32* %ptr                          ; yields void
    %val = load i32, i32* %ptr                      ; yields i32:val = i32 3
    """
    def _parse_line(self):
        spl = self.line.split(', ')
        self.type = POINTER_TY if spl[0].endswith('*') else INTEGER_TY
        txt_args = find_txt_args(self.line)
        self.args = [ARG_POINTER] * len(txt_args)


class BRCommand(Command):
    """
    br i1 <cond>, label <iftrue>, label <iffalse>
    br label <dest>          ; Unconditional branch

    br i1 <cond>, label <iftrue>, label <iffalse>
    br label <dest>          ; Unconditional branch
    """
    def _parse_line(self):
        # TODO CHECK AGAIN
        self.type = VOID_TY

        if '%unifiedunreachableblock' in self.line.lower():
            self.name = 'unreachable'
            self.args = []
            return

        self.args = parse_label_args(self.line)


class IndirectBRCommand(Command):
    """
    indirectbr <somety>* <address>, [ label <dest1>, label <dest2>, ... ]

    indirectbr i8* %Addr, [ label %bb1, label %bb2, label %bb3 ]
    """
    def _parse_line(self):
        self.type = POINTER_TY
        self.args = parse_label_args(self.line)


class InvokeCommand(Command):
    """
    <result> = invoke [cconv] [ret attrs] [addrspace(<num>)] <ty>|<fnty> <fnptrval>(<function args>) [fn attrs]
              [operand bundles] to label <normal label> unwind label <exception label>

    %retval = invoke i32 @Test(i32 15) to label %Continue
            unwind label %TestCleanup              ; i32:retval set
    %retval = invoke coldcc i32 %Testfnptr(i32 15) to label %Continue
                unwind label %TestCleanup              ; i32:retval set
    """
    def _parse_line(self):
        # TODO
        raise NotImplementedError()


class CallBrCommand(Command):
    """
    <result> = callbr [cconv] [ret attrs] [addrspace(<num>)] <ty>|<fnty> <fnptrval>(<function args>) [fn attrs]
              [operand bundles] to label <fallthrough label> [indirect labels]

    ; "asm goto" without output constraints.
    callbr void asm "", "r,X"(i32 %x, i8 *blockaddress(@foo, %indirect))
                to label %fallthrough [label %indirect]

    ; "asm goto" with output constraints.
    <result> = callbr i32 asm "", "=r,r,X"(i32 %x, i8 *blockaddress(@foo, %indirect))
                to label %fallthrough [label %indirect]
    """
    def _parse_line(self):
        # TODO
        raise NotImplementedError()


class ResumeCommand(BRCommand):
    """
    resume <type> <value>

    resume { i8*, i32 } %exn
    """


class CatchSwitchCommand(Command):
    """
    <resultval> = catchswitch within <parent> [ label <handler1>, label <handler2>, ... ] unwind to caller
    <resultval> = catchswitch within <parent> [ label <handler1>, label <handler2>, ... ] unwind label <default>

    dispatch1:
      %cs1 = catchswitch within none [label %handler0, label %handler1] unwind to caller
    dispatch2:
      %cs2 = catchswitch within %parenthandler [label %handler0] unwind label %cleanup
    """
    def _parse_line(self):
        # TODO
        raise NotImplementedError()


class CatchRetCommand(Command):
    """
    catchret from <token> to label <normal>
    catchret from %catch label %continue

    catchret from %catch label %continue
    """
    def _parse_line(self):
        # TODO
        raise NotImplementedError()


class CleanUpRetCommand(Command):
    """
    cleanupret from <value> unwind label <continue>
    cleanupret from <value> unwind to caller

    cleanupret from %cleanup unwind to caller
    cleanupret from %cleanup unwind label %continue
    """
    def _parse_line(self):
        # TODO
        raise NotImplementedError()


class GetElementPtrCommand(Command):
    """
    <result> = getelementptr <ty>, <ty>* <ptrval>{, [inrange] <ty> <idx>}*
    <result> = getelementptr inbounds <ty>, <ty>* <ptrval>{, [inrange] <ty> <idx>}*
    <result> = getelementptr <ty>, <ptr vector> <ptrval>, [inrange] <vector index type> <idx>

    ; yields [12 x i8]*:aptr
    %aptr = getelementptr {i32, [12 x i8]}, {i32, [12 x i8]}* %saptr, i64 0, i32 1
    ; yields i8*:vptr
    %vptr = getelementptr {i32, <2 x i8>}, {i32, <2 x i8>}* %svptr, i64 0, i32 1, i32 1
    ; yields i8*:eptr
    %eptr = getelementptr [12 x i8], [12 x i8]* %aptr, i64 0, i32 1
    ; yields i32*:iptr
    %iptr = getelementptr [10 x i32], [10 x i32]* @arr, i16 0, i16 0
    """
    def _parse_line(self):
        self.type = POINTER_TY
        args = parse_args(self.line[self.line.find(',') + 1:])
        self.args = args


class ConversionCommand(Command):
    def _parse_line(self):
        spl = self.line.split(' to ')
        ty2 = spl[-1]
        first = spl[0]
        last_space, first_space = first.rfind(' '), first.find(' ')
        ty, val = first[first_space + 1: last_space], first[last_space + 1:]
        self.type = parse_type(ty)
        self.args = [parse_arg(f'{ty2} {val}')]


class TruncCommand(ConversionCommand):
    """
    <result> = trunc <ty> <value> to <ty2>             ; yields ty2

    %X = trunc i32 257 to i8                        ; yields i8:1
    %Y = trunc i32 123 to i1                        ; yields i1:true
    %Z = trunc i32 122 to i1                        ; yields i1:false
    %W = trunc <2 x i16> <i16 8, i16 7> to <2 x i8> ; yields <i8 8, i8 7>
    """


class ZextCommand(ConversionCommand):
    """
    <result> = zext <ty> <value> to <ty2>             ; yields ty2

    %X = zext i32 257 to i64              ; yields i64:257
    %Y = zext i1 true to i32              ; yields i32:1
    %Z = zext <2 x i16> <i16 8, i16 7> to <2 x i32> ; yields <i32 8, i32 7>
    """


class SextCommand(ConversionCommand):
    """
    <result> = sext <ty> <value> to <ty2>             ; yields ty2

    %X = sext i8  -1 to i16              ; yields i16   :65535
    %Y = sext i1 true to i32             ; yields i32:-1
    %Z = sext <2 x i16> <i16 8, i16 7> to <2 x i32> ; yields <i32 8, i32 7>
    """


class FPTruncCommand(ConversionCommand):
    """
    <result> = fptrunc <ty> <value> to <ty2>             ; yields ty2

    %X = fptrunc double 16777217.0 to float    ; yields float:16777216.0
    %Y = fptrunc double 1.0E+300 to half       ; yields half:+infinity
    """


class FPextCommand(ConversionCommand):
    """
    <result> = fpext <ty> <value> to <ty2>             ; yields ty2

    %X = fpext float 3.125 to double         ; yields double:3.125000e+00
    %Y = fpext double %X to fp128            ; yields fp128:0xL00000000000000004000900000000000
    """


class FpToUiCommand(ConversionCommand):
    """
    <result> = fptoui <ty> <value> to <ty2>             ; yields ty2

    %X = fptoui double 123.0 to i32      ; yields i32:123
    %Y = fptoui float 1.0E+300 to i1     ; yields undefined:1
    %Z = fptoui float 1.04E+17 to i8     ; yields undefined:1
    """


class FPToSiCommand(ConversionCommand):
    """
    <result> = fptosi <ty> <value> to <ty2>             ; yields ty2

    %X = fptosi double -123.0 to i32      ; yields i32:-123
    %Y = fptosi float 1.0E-247 to i1      ; yields undefined:1
    %Z = fptosi float 1.04E+17 to i8      ; yields undefined:1
    """


class UiToFpCommand(ConversionCommand):
    """
    <result> = uitofp <ty> <value> to <ty2>             ; yields ty2

    %X = uitofp i32 257 to float         ; yields float:257.0
    %Y = uitofp i8 -1 to double          ; yields double:255.0
    """


class SiToFpCommand(ConversionCommand):
    """
    <result> = sitofp <ty> <value> to <ty2>             ; yields ty2

    %X = sitofp i32 257 to float         ; yields float:257.0
    %Y = sitofp i8 -1 to double          ; yields double:-1.0
    """


class PtrToIntCommand(ConversionCommand):
    """
    <result> = ptrtoint <ty> <value> to <ty2>             ; yields ty2

    %X = ptrtoint i32* %P to i8                         ; yields truncation on 32-bit architecture
    %Y = ptrtoint i32* %P to i64                        ; yields zero extension on 32-bit architecture
    %Z = ptrtoint <4 x i32*> %P to <4 x i64>; yields vector zero extension for a vector
    of addresses on 32-bit architecture
    """


class IntToPtrCommand(ConversionCommand):
    """
    <result> = inttoptr <ty> <value> to <ty2>[, !dereferenceable !<deref_bytes_node>]
    [, !dereferenceable_or_null !<deref_bytes_node>]             ; yields ty2


    %X = inttoptr i32 255 to i32*          ; yields zero extension on 64-bit architecture
    %Y = inttoptr i32 255 to i32*          ; yields no-op on 32-bit architecture
    %Z = inttoptr i64 0 to i32*            ; yields truncation on 32-bit architecture
    %Z = inttoptr <4 x i32> %G to <4 x i8*>; yields truncation of vector G to four pointers
    """


class BitCastCommand(ConversionCommand):
    """
    <result> = bitcast <ty> <value> to <ty2>             ; yields ty2

    %X = bitcast i8 255 to i8          ; yields i8 :-1
    %Y = bitcast i32* %x to sint*      ; yields sint*:%x
    %Z = bitcast <2 x int> %V to i64;  ; yields i64: %V (depends on endianess)
    %Z = bitcast <2 x i32*> %V to <2 x i64*> ; yields <2 x i64*>
    """


class AddressSpaceCastCommand(ConversionCommand):
    """
    <result> = addrspacecast <pty> <ptrval> to <pty2>       ; yields pty2

    %X = addrspacecast i32* %x to i32 addrspace(1)*    ; yields i32 addrspace(1)*:%x
    %Y = addrspacecast i32 addrspace(1)* %y to i64 addrspace(2)*    ; yields i64 addrspace(2)*:%y
    %Z = addrspacecast <4 x i32*> %z to <4 x float addrspace(3)*>   ; yields <4 x float addrspace(3)*>:%z
    """


class ICmpCommand(Command):
    """
    <result> = icmp <cond> <ty> <op1>, <op2>   ; yields i1 or <N x i1>:result

    <result> = icmp eq i32 4, 5          ; yields: result=false
    <result> = icmp ne float* %X, %X     ; yields: result=false
    <result> = icmp ult i16  4, 5        ; yields: result=true
    <result> = icmp sgt i16  4, 5        ; yields: result=false
    <result> = icmp ule i16 -4, 5        ; yields: result=false
    <result> = icmp sge i16  4, 5        ; yields: result=false
    """
    def _parse_line(self):
        self.type = INTEGER_TY
        txt_args = self.line.split(', ')[:2]
        self.args = parse_cmp_args(txt_args)


class FCmpCommand(Command):
    """
    <result> = fcmp [fast-math flags]* <cond> <ty> <op1>, <op2>     ; yields i1 or <N x i1>:result

    <result> = fcmp oeq float 4.0, 5.0    ; yields: result=false
    <result> = fcmp one float 4.0, 5.0    ; yields: result=true
    <result> = fcmp olt float 4.0, 5.0    ; yields: result=true
    <result> = fcmp ueq double 1.0, 2.0   ; yields: result=false
    """
    def _parse_line(self):
        self.type = FLOAT_TY
        txt_args = self.line.split(', ')[:2]
        self.args = parse_cmp_args(txt_args)


class PhiCommand(Command):
    """
    <result> = phi [fast-math-flags] <ty> [ <val0>, <label0>], ...

    Loop:       ; Infinite loop that counts from 0 on up...
      %indvar = phi i32 [ 0, %LoopHeader ], [ %nextindvar, %Loop ]
      %nextindvar = add i32 %indvar, 1
      br label %Loop
    """
    def _parse_line(self):
        self.type = parse_type(self.line.split()[1])
        # TODO
        self.args = []


class SelectCommand(Command):
    """
    <result> = select [fast-math flags] selty <cond>, <ty> <val1>, <ty> <val2>             ; yields ty
        selty is either i1 or {<N x i1>}

    %X = select i1 true, i8 17, i8 42          ; yields i8:17
    """

    def _parse_line(self):
        self.type = INTEGER_TY
        self.args = parse_args(self.line)


class FreezeCommand(Command):
    """
    <result> = freeze ty <val>    ; yields ty:self.type = ''

    %w = i32 undef
    %x = freeze i32 %w
    %y = add i32 %w, %w         ; undef
    %z = add i32 %x, %x         ; even number because all uses of %x observe
                                ; the same value
    %x2 = freeze i32 %w
    %cmp = icmp eq i32 %x, %x2  ; can be true or false

    ; example with vectors
    %v = <2 x i32> <i32 undef, i32 poison>
    %a = extractelement <2 x i32> %v, i32 0    ; undef
    %b = extractelement <2 x i32> %v, i32 1    ; poison
    %add = add i32 %a, %a                      ; undef

    %v.fr = freeze <2 x i32> %v                ; element-wise freeze
    %d = extractelement <2 x i32> %v.fr, i32 0 ; not undef
    %add.f = add i32 %d, %d                    ; even number

    ; branching on frozen value
    %poison = add nsw i1 %k, undef   ; poison
    %c = freeze i1 %poison
    br i1 %c, label %foo, label %bar ; non-deterministic branch to %foo or %bar
    """
    def _parse_line(self):
        spl = self.line.split()
        self.type = parse_type(spl[1])
        self.args = [parse_arg(spl[-1])]


class RetCommand(Command):
    """
    ret <type> <value>       ; Return a value from a non-void function
    ret void                 ; Return from void function

    ret i32 5                       ; Return an integer value of 5
    ret void                        ; Return from a void function
    ret { i32, i8 } { i32 4, i8 2 } ; Return a struct of values 4 and 2
    """
    def _parse_line(self):
        self.type = VOID_TY
        self.args = []
        if self.line.strip() != 'ret void':
            spl = self.line.split()
            self.type = parse_type(spl[1])
            self.args = parse_args(spl[2])


class UnreachableCommand(Command):
    """
    unreachable
    """
    def _parse_line(self):
        self.type = VOID_TY
        self.args = []


class FNegUnaryOperatorCommand(Command):
    """
    <result> = fneg [fast-math flags]* <ty> <op1>   ; yields ty:result

    <result> = fneg float %val          ; yields float:result = -%var
    """
    def _parse_line(self):
        spl = self.line.split()
        self.type = parse_type(spl[-2])
        self.args = parse_args(spl[-1])


class BinaryCommand(Command):
    exclusion_pattern = re.compile(r'(\(.+\))')

    def _parse_line(self):
        find = self.exclusion_pattern.findall(self.line)
        if len(find) > 0:
            self.line = self.line.replace(find[0], '')

        spl = [x.strip() for x in self.line.split()]
        ty, op1, op2 = spl[-3:]
        self.type = parse_type(ty)
        self.args = [parse_arg(op1), parse_arg(op2)]


class AddCommand(BinaryCommand):
    """
    <result> = add <ty> <op1>, <op2>          ; yields ty:result
    <result> = add nuw <ty> <op1>, <op2>      ; yields ty:result
    <result> = add nsw <ty> <op1>, <op2>      ; yields ty:result
    <result> = add nuw nsw <ty> <op1>, <op2>  ; yields ty:result

    <result> = add i32 4, %var          ; yields i32:result = 4 + %var
    """


class FAddCommand(BinaryCommand):
    """
    <result> = fadd [fast-math flags]* <ty> <op1>, <op2>   ; yields ty:result

    <result> = fadd float 4.0, %var          ; yields float:result = 4.0 + %var
    """


class SubCommand(BinaryCommand):
    """
    <result> = sub <ty> <op1>, <op2>          ; yields ty:result
    <result> = sub nuw <ty> <op1>, <op2>      ; yields ty:result
    <result> = sub nsw <ty> <op1>, <op2>      ; yields ty:result
    <result> = sub nuw nsw <ty> <op1>, <op2>  ; yields ty:result

    <result> = sub i32 4, %var          ; yields i32:result = 4 - %var
    <result> = sub i32 0, %val          ; yields i32:result = -%var
    """


class FSubCommand(BinaryCommand):
    """
    <result> = fsub [fast-math flags]* <ty> <op1>, <op2>   ; yields ty:result

    <result> = fsub float 4.0, %var           ; yields float:result = 4.0 - %var
    <result> = fsub float -0.0, %val          ; yields float:result = -%var
    """


class MulCommand(BinaryCommand):
    """
    <result> = mul <ty> <op1>, <op2>          ; yields ty:result
    <result> = mul nuw <ty> <op1>, <op2>      ; yields ty:result
    <result> = mul nsw <ty> <op1>, <op2>      ; yields ty:result
    <result> = mul nuw nsw <ty> <op1>, <op2>  ; yields ty:result

    <result> = mul i32 4, %var          ; yields i32:result = 4 * %var
    """


class FMulCommand(BinaryCommand):
    """
    <result> = fmul [fast-math flags]* <ty> <op1>, <op2>   ; yields ty:result

    <result> = fmul float 4.0, %var          ; yields float:result = 4.0 * %var
    """


class UDivCommand(BinaryCommand):
    """
    <result> = udiv <ty> <op1>, <op2>         ; yields ty:result
    <result> = udiv exact <ty> <op1>, <op2>   ; yields ty:result

    <result> = udiv i32 4, %var          ; yields i32:result = 4 / %var
    """


class SDivCommand(BinaryCommand):
    """
    <result> = sdiv <ty> <op1>, <op2>         ; yields ty:result
    <result> = sdiv exact <ty> <op1>, <op2>   ; yields ty:result

    <result> = sdiv i32 4, %var          ; yields i32:result = 4 / %var
    """


class FDivCommand(BinaryCommand):
    """
    <result> = fdiv [fast-math flags]* <ty> <op1>, <op2>   ; yields ty:result

    <result> = fdiv float 4.0, %var          ; yields float:result = 4.0 / %var
    """


class URemCommand(BinaryCommand):
    """
    <result> = urem <ty> <op1>, <op2>   ; yields ty:result

    <result> = urem i32 4, %var          ; yields i32:result = 4 % %var
    """


class SRemCommand(BinaryCommand):
    """
    <result> = srem <ty> <op1>, <op2>   ; yields ty:result

    <result> = srem i32 4, %var          ; yields i32:result = 4 % %var
    """


class FRemCommand(BinaryCommand):
    """
    <result> = frem [fast-math flags]* <ty> <op1>, <op2>   ; yields ty:result

    <result> = frem float 4.0, %var          ; yields float:result = 4.0 % %var
    """


class ShlCommand(BinaryCommand):
    """
    <result> = shl <ty> <op1>, <op2>           ; yields ty:result
    <result> = shl nuw <ty> <op1>, <op2>       ; yields ty:result
    <result> = shl nsw <ty> <op1>, <op2>       ; yields ty:result
    <result> = shl nuw nsw <ty> <op1>, <op2>   ; yields ty:result

    <result> = shl i32 4, %var   ; yields i32: 4 << %var
    <result> = shl i32 4, 2      ; yields i32: 16
    <result> = shl i32 1, 10     ; yields i32: 1024
    <result> = shl i32 1, 32     ; undefined
    <result> = shl <2 x i32> < i32 1, i32 1>, < i32 1, i32 2>   ; yields: result=<2 x i32> < i32 2, i32 4>
    """


class LshrCommand(BinaryCommand):
    """
    <result> = lshr <ty> <op1>, <op2>         ; yields ty:result
    <result> = lshr exact <ty> <op1>, <op2>   ; yields ty:result

    <result> = lshr i32 4, 1   ; yields i32:result = 2
    <result> = lshr i32 4, 2   ; yields i32:result = 1
    <result> = lshr i8  4, 3   ; yields i8:result = 0
    <result> = lshr i8 -2, 1   ; yields i8:result = 0x7F
    <result> = lshr i32 1, 32  ; undefined
    <result> = lshr <2 x i32> < i32 -2, i32 4>, < i32 1, i32 2>   ; yields: result=<2 x i32> < i32 0x7FFFFFFF, i32 1>
    """


class AshrCommand(BinaryCommand):
    """
    <result> = ashr <ty> <op1>, <op2>         ; yields ty:result
    <result> = ashr exact <ty> <op1>, <op2>   ; yields ty:result

    <result> = ashr i32 4, 1   ; yields i32:result = 2
    <result> = ashr i32 4, 2   ; yields i32:result = 1
    <result> = ashr i8  4, 3   ; yields i8:result = 0
    <result> = ashr i8 -2, 1   ; yields i8:result = -1
    <result> = ashr i32 1, 32  ; undefined
    <result> = ashr <2 x i32> < i32 -2, i32 4>, < i32 1, i32 3>   ; yields: result=<2 x i32> < i32 -1, i32 0>
    """


class AndCommand(BinaryCommand):
    """
    <result> = and <ty> <op1>, <op2>   ; yields ty:result

    <result> = and i32 4, %var         ; yields i32:result = 4 & %var
    <result> = and i32 15, 40          ; yields i32:result = 8
    <result> = and i32 4, 8            ; yields i32:result = 0
    """


class OrCommand(BinaryCommand):
    """
    <result> = or <ty> <op1>, <op2>   ; yields ty:result

    <result> = or i32 4, %var         ; yields i32:result = 4 | %var
    <result> = or i32 15, 40          ; yields i32:result = 47
    <result> = or i32 4, 8            ; yields i32:result = 12
    """


class XorCommand(BinaryCommand):
    """
    <result> = xor <ty> <op1>, <op2>   ; yields ty:result

    <result> = xor i32 4, %var         ; yields i32:result = 4 ^ %var
    <result> = xor i32 15, 40          ; yields i32:result = 39
    <result> = xor i32 4, 8            ; yields i32:result = 12
    <result> = xor i32 %V, -1          ; yields i32:result = ~%V
    """


class ExtractElementCommand(Command):
    """
    <result> = extractelement <n x <ty>> <val>, <ty2> <idx>  ; yields <ty>
    <result> = extractelement <vscale x n x <ty>> <val>, <ty2> <idx> ; yields <ty>

    <result> = extractelement <4 x i32> %vec, i32 0    ; yields i32

    """
    def _parse_line(self):
        self.type = VECTOR_TY
        spl = self.line.split()
        self.args = [ARG_VARIABLE, parse_arg(spl[-1])]


class InsertElementCommand(Command):
    """
    <result> = insertelement <n x <ty>> <val>, <ty> <elt>, <ty2> <idx>    ; yields <n x <ty>>
    <result> = insertelement <vscale x n x <ty>> <val>, <ty> <elt>, <ty2> <idx> ; yields <vscale x n x <ty>>

    <result> = insertelement <4 x i32> %vec, i32 1, i32 0    ; yields <4 x i32>
    """
    def _parse_line(self):
        self.type = VECTOR_TY
        elt, idx = self.line.split()[-2:]
        self.args = [ARG_VARIABLE, parse_arg(elt), parse_arg(idx)]


class ShuffleVectorCommand(Command):
    """
    <result> = shufflevector <n x <ty>> <v1>, <n x <ty>> <v2>, <m x i32> <mask>    ; yields <m x <ty>>
    <result> = shufflevector <vscale x n x <ty>> <v1>, <vscale x n x <ty>> v2, <vscale x m x i32> <mask>  ;
        yields <vscale x m x <ty>>

    <result> = shufflevector <4 x i32> %v1, <4 x i32> %v2,
                        <4 x i32> <i32 0, i32 4, i32 1, i32 5>  ; yields <4 x i32>
    <result> = shufflevector <4 x i32> %v1, <4 x i32> undef,
                            <4 x i32> <i32 0, i32 1, i32 2, i32 3>  ; yields <4 x i32> - Identity shuffle.
    <result> = shufflevector <8 x i32> %v1, <8 x i32> undef,
                            <4 x i32> <i32 0, i32 1, i32 2, i32 3>  ; yields <4 x i32>
    <result> = shufflevector <4 x i32> %v1, <4 x i32> %v2,
                            <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7 >  ; yields <8 x i32>
    """
    def _parse_line(self):
        self.type = VECTOR_TY
        self.args = [ARG_VARIABLE, ARG_VARIABLE]


class ExtractValueCommand(Command):
    """
    <result> = extractvalue <aggregate type> <val>, <idx>{, <idx>}*

    <result> = extractvalue {i32, float} %agg, 0    ; yields i32
    """

    def _parse_line(self):
        raise NotImplementedError()


class InsertValueCommand(Command):
    """
    <result> = insertvalue <aggregate type> <val>, <ty> <elt>, <idx>{, <idx>}*    ; yields <aggregate type>

    %agg1 = insertvalue {i32, float} undef, i32 1, 0              ; yields {i32 1, float undef}
    %agg2 = insertvalue {i32, float} %agg1, float %val, 1         ; yields {i32 1, float %val}
    %agg3 = insertvalue {i32, {float}} undef, float %val, 1, 0    ; yields {i32 undef, {float %val}}
    """
    def _parse_line(self):
        self.type = STRUCT_TY
        spl = self.line[self.line.rfind('}') + 1:].split(', ')[1:]
        self.args = [parse_arg(s) for s in spl]


class VaArgCommand(Command):
    """
    <resultval> = va_arg <va_list*> <arglist>, <argty>
    """
    def _parse_line(self):
        raise NotImplementedError()


class LandingPadCommand(Command):
    """
    <resultval> = landingpad <resultty> <clause>+
    <resultval> = landingpad <resultty> cleanup <clause>*

    <clause> := catch <type> <value>
    <clause> := filter <array constant type> <array constant>


    ;; A landing pad which can catch an integer.
    %res = landingpad { i8*, i32 }
             catch i8** @_ZTIi
    ;; A landing pad that is a cleanup.
    %res = landingpad { i8*, i32 }
             cleanup
    ;; A landing pad which can catch an integer and can only throw a double.
    %res = landingpad { i8*, i32 }
             catch i8** @_ZTIi
             filter [1 x i8**] [@_ZTId]
    """

    def _parse_line(self):
        self.type = VECTOR_TY
        self.args = []


class CatchPadCommand(Command):
    """
    <resultval> = catchpad within <catchswitch> [<args>*]

    dispatch:
      %cs = catchswitch within none [label %handler0] unwind to caller
      ;; A catch block which can catch an integer.
    handler0:
      %tok = catchpad within %cs [i8** @_ZTIi]
    """

    def _parse_line(self):
        raise NotImplementedError()


class CleanUpPadCommand(Command):
    """
    <resultval> = cleanuppad within <parent> [<args>*]

    %tok = cleanuppad within %cs []
    """
    def _parse_line(self):
        raise NotImplementedError()


class SwitchCommand(Command):
    """
    switch <intty> <value>, label <defaultdest> [ <intty> <val>, label <dest> ... ]

    ; Emulate a conditional br instruction
    %Val = zext i1 %value to i32
    switch i32 %Val, label %truedest [ i32 0, label %falsedest ]

    ; Emulate an unconditional br instruction
    switch i32 0, label %dest [ ]

    ; Implement a jump table:
    switch i32 %val, label %otherwise [ i32 0, label %onzero
                                        i32 1, label %onone
                                        i32 2, label %ontwo ]
    """
    def _parse_line(self):
        self.type = INTEGER_TY
        ln = self.line[: self.line.find('[')]
        self.args = parse_label_args(ln)
        if '[' in self.line:
            ln = self.line[self.line.find('[')+1: self.line.find(']')].strip()
            self.args += parse_label_args(ln)


CMD_CMP_X_CHG = 'cmpxchg'
CMD_ATOMIC_RMW = 'atomicrmw'
CMD_FP_TO_UI = 'fptoui'
CMD_FP_TO_SI = 'fptosi'
CMD_UI_TO_FP = 'uitofp'
CMD_CATCH_PAD = 'catchpad'
COMMAND_CLASS_MAP = {
    CMD_CLEANUP_RET: CleanUpRetCommand,
    CMD_CATCH_RET: CatchRetCommand,
    CMD_CALLBR: CallBrCommand,
    CMD_INVOKE: InvokeCommand,
    CMD_INDIRECT_BR: IndirectBRCommand,
    CMD_LSHR: LshrCommand,
    CMD_AND: AndCommand,
    CMD_FPTRUNC: FPTruncCommand,
    CMD_FPEXT: FPextCommand,
    CMD_FSUB: FSubCommand,
    CMD_FDIV: FDivCommand,
    CMD_FMUL: FMulCommand,
    CMD_FADD: FAddCommand,
    CMD_FCOMP: FCmpCommand,
    CMD_INT_TOP_TR: IntToPtrCommand,
    CMD_SDIV: SDivCommand,
    CMD_SREM: SRemCommand,
    CMD_SELECT: SelectCommand,
    CMD_TRUNC: TruncCommand,
    CMD_SWITCH: SwitchCommand,
    CMD_SHL: ShlCommand,
    CMD_XOR: XorCommand,
    CMD_OR: OrCommand,
    CMD_UREM: URemCommand,
    CMD_MUL: MulCommand,
    CMD_SUB: SubCommand,
    CMD_SEXT: SextCommand,
    CMD_BITCAST: BitCastCommand,
    CMD_UNREACHABLE: UnreachableCommand,
    CMD_RET: RetCommand,
    CMD_GET_ELEMENT_PTR: GetElementPtrCommand,
    CMD_ADD: AddCommand,
    CMD_ZEXT: ZextCommand,
    CMD_BR: BRCommand,
    CMD_ICMP: ICmpCommand,
    CMD_LOAD: LoadCommand,
    CMD_STORE: StoreCommand,
    CMD_ALLOC: AllocCommand,
    CMD_CALL: CallCommand,
    CMD_RESUME: ResumeCommand,
    CMD_CATCH_SWITCH: CatchSwitchCommand,
    CMD_FENCE: FenceCommand,
    CMD_CMP_X_CHG: CmpXChgCommand,
    CMD_ATOMIC_RMW: AtomicRmwCommand,
    CMD_FP_TO_UI: FpToUiCommand,
    CMD_FP_TO_SI: FPToSiCommand,
    CMD_UI_TO_FP: UiToFpCommand,
    CMD_SI_TO_FP: SiToFpCommand,
    CMD_PTR_TO_INT: PtrToIntCommand,
    CMD_ADDRESS_SPACE_CAST: AddressSpaceCastCommand,
    CMD_PHI: PhiCommand,
    CMD_FREEZE: FreezeCommand,
    CMD_FNEG: FNegUnaryOperatorCommand,
    CMD_UDIV: UDivCommand,
    CMD_FREM: FRemCommand,
    CMD_ASHR: AshrCommand,
    CMD_EXTRACT_ELEMENT: ExtractElementCommand,
    CMD_INSERT_ELEMENT: InsertElementCommand,
    CMD_SHUFFLE_VECTOR: ShuffleVectorCommand,
    CMD_EXTRACT_VALUE: ExtractValueCommand,
    CMD_INSERT_VALUE: InsertValueCommand,
    CMD_VA_ARG: VaArgCommand,
    CMD_LANDING_PAD: LandingPadCommand,
    CMD_CATCH_PAD: CatchPadCommand,
    CMD_CLEANUP_PAD: CleanUpPadCommand
}


def generalize_ir_line(line):
    if ' = ' in line:
        line = line.split(' = ')[1]

    if ';' in line:
        line = line[:line.find(';')]

    if '!' in line:
        line = line[:line.find('!')].strip(', ')

    if line.startswith('unreachable'):
        line = 'unreachable'

    spl = line.split()
    cmd_str = spl[0]
    command = COMMAND_CLASS_MAP[cmd_str](cmd_str, line)
    return str(command)


def read_vocab(file_path):
    with open(file_path) as inp:
        res = {}
        for line in map(str.strip, inp):
            if line != '':
                key, val = line.split(':')
                res[key] = np.array(json.loads(val.strip(',')))
        return res


def read_file(file_name):
    with open(file_name) as inp:
        return [line.strip() for line in inp if line.strip() != '']


def run_test(g_ir_file, ir_file):
    ir = read_file(ir_file)
    gir = read_file(g_ir_file)
    for i, gir in zip(ir, gir):
        gi = generalize_ir_line(i)
        assert gi == gir


def add(one, two):
    res = []
    for a, b in zip(one, two):
        res.append(a + b)
    return res


def get_instruction_embedding(ir, vocab, w0=1.0, wt=0.5, wa=0.25):
    gir = generalize_ir_line(ir)
    words = gir.split('  ')
    cmd, tp, *args = map(lambda word: np.array(vocab[word]), words)
    return w0*cmd + wt*tp + (np.array(args) * wa).sum(axis=0)


def main():
    ir_file = 'test_files/test_ir.txt'
    g_ir_file = 'test_files/test_gir.txt'
    run_test(g_ir_file, ir_file)


if __name__ == '__main__':
    main()
