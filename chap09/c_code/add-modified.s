	.file	"add.c"
	.text
	.globl	add
	.type	add, @function
add:
	pushq	%rbp            # save base ptr
	movq	%rsp, %rbp      # copy stack ptr to base ptr
  subq  $8, %rsp        # make new stack frame
	movl	%edi, -4(%rbp)  # copy first argument from %edi reg
	movl	%esi, -8(%rbp)  # copy second argument from %esi reg
	movl	-4(%rbp), %edx  # copy first arg into %edx reg
	movl	-8(%rbp), %eax  # copy second arge into %eax reg
	addl	%edx, %eax      # add %edx to %eax, %eax is return val
  movq  %rbp, %rsp      # remove stack frame
	popq	%rbp            # restore previous base ptr
	ret                   # return to caller, pop return addr
	.size	add, .-add
	.globl	foo
	.type	foo, @function
foo:
	pushq	%rbp            # save base ptr
	movq	%rsp, %rbp      # copy stack ptr to base ptr 
	subq	$4, %rsp        # make new stack frame
	movl	$2, %esi        # copy second arg to %esi reg
	movl	$3, %edi        # copy first arg to %edi reg
	call	add             # push return addr, jump to function
	movl	%eax, -4(%rbp)  # copy result to local variable
	movl	-4(%rbp), %eax  # copy local variable to %eax
	movq  %rbp, %rsp      # remove stack frame
	popq	%rbp            # restore previous base ptr
	ret                   # return to caller, pop return addr
	.size	foo, .-foo
	.section	.rodata
.LC0:
	.string	"%d\n"
	.text
	.globl	main
	.type	main, @function
main:
	pushq	%rbp
	movq	%rsp, %rbp
	movl	$0, %eax
	call	foo
	movl	%eax, %esi
	leaq	.LC0(%rip), %rdi
	movl	$0, %eax
	call	printf@PLT
	movl	$0, %eax
	popq	%rbp
	ret
	.size	main, .-main
	.ident	"GCC: (Ubuntu 7.5.0-3ubuntu1~18.04) 7.5.0"
	.section	.note.GNU-stack,"",@progbits
