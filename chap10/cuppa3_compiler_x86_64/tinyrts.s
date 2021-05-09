####################################################################
# tinyrts.s
#
# a minimal runtime system for the Cuppa3/x86_65
# compiler. it provides the functions:
#	
#   put(i) - print the integer i to the screen, where i is an 8 byte
#	     integer expected to be pushed on the stack before the
#            call to put	
#   get()  - prompts the user for input of an integer value
#            value is returned in %eax
#   exit   - shuts the process down cleanly	
#	
# this is a "bare metal" rts, no other libraries are required.
# runs right on top of the kernel. written in gas using AT&T
# syntax.
#
# syscall info was gleaned from:
# blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/	
#
# (c) Lutz Hamel, University of Rhode Island
####################################################################

	.data

	# general purpose buffer 
	.lcomm rtsbuf, 256

	# this buffer contains the prompt string
	# for function get
promptbuf:
	.string "? "

	# this buffer contains the newline character
	# used in function put
nlbuf:
	.string "\n"

	.text

	############################################################
	# convert a string to an integer
	# Note: internal routine not visible globally
	# Note: assembly generated from C code, see atoi.c
atoi:
	# %esi - length of string
	# %rdi - pointer to string buffer
	# returns integer value in %eax
	pushq	%rbp
	movq	%rsp, %rbp
	movq	%rdi, -24(%rbp)
	movl	%esi, -28(%rbp)
	movl	$0, -12(%rbp)
	movl	$1, -8(%rbp)
	movl	$0, -4(%rbp)
	movq	-24(%rbp), %rax
	movzbl	(%rax), %eax
	cmpb	$45, %al
	jne	.L3
	movl	$-1, -8(%rbp)
	addl	$1, -4(%rbp)
	jmp	.L3
.L4:
	movl	-12(%rbp), %edx
	movl	%edx, %eax
	sall	$2, %eax
	addl	%edx, %eax
	addl	%eax, %eax
	movl	%eax, %ecx
	movl	-4(%rbp), %eax
	movslq	%eax, %rdx
	movq	-24(%rbp), %rax
	addq	%rdx, %rax
	movzbl	(%rax), %eax
	movsbl	%al, %eax
	addl	%ecx, %eax
	subl	$48, %eax
	movl	%eax, -12(%rbp)
	addl	$1, -4(%rbp)
.L3:
	movl	-4(%rbp), %eax
	cmpl	-28(%rbp), %eax
	jl	.L4
	movl	-8(%rbp), %eax
	imull	-12(%rbp), %eax
	popq	%rbp
	ret

	############################################################
	# convert an integer to a string. string will be
	# returned in buffer, length returned in %eax
	# Note: internal routine not visible globally
	# Note: assembly generated from C code, see atoi.c
itoa:
	# %edi - val
	# %rsi - buffer
	# returns len in %eax
	pushq	%rbp
	movq	%rsp, %rbp
	movl	%edi, -52(%rbp)
	movq	%rsi, -64(%rbp)
	movl	$10, -28(%rbp)
	movq	-64(%rbp), %rax
	movq	%rax, -16(%rbp)
	cmpl	$0, -52(%rbp)
	jns	.L7
	movq	-16(%rbp), %rax
	leaq	1(%rax), %rdx
	movq	%rdx, -16(%rbp)
	movb	$45, (%rax)
	negl	-52(%rbp)
.L7:
	movl	-52(%rbp), %eax
	movl	%eax, -32(%rbp)
	movq	-16(%rbp), %rax
	movq	%rax, -8(%rbp)
.L8:
	movl	-32(%rbp), %eax
	movl	$0, %edx
	divl	-28(%rbp)
	movl	%edx, -24(%rbp)
	movl	-32(%rbp), %eax
	movl	$0, %edx
	divl	-28(%rbp)
	movl	%eax, -32(%rbp)
	movl	-24(%rbp), %eax
	leal	48(%rax), %ecx
	movq	-16(%rbp), %rax
	leaq	1(%rax), %rdx
	movq	%rdx, -16(%rbp)
	movl	%ecx, %edx
	movb	%dl, (%rax)
	cmpl	$0, -32(%rbp)
	jne	.L8
	movq	-16(%rbp), %rdx
	movq	-64(%rbp), %rax
	subq	%rax, %rdx
	movq	%rdx, %rax
	movl	%eax, -20(%rbp)
	movq	-16(%rbp), %rax
	leaq	-1(%rax), %rdx
	movq	%rdx, -16(%rbp)
	movb	$0, (%rax)
.L9:
	movq	-16(%rbp), %rax
	movzbl	(%rax), %eax
	movb	%al, -33(%rbp)
	movq	-8(%rbp), %rax
	movzbl	(%rax), %edx
	movq	-16(%rbp), %rax
	movb	%dl, (%rax)
	movq	-8(%rbp), %rax
	movzbl	-33(%rbp), %edx
	movb	%dl, (%rax)
	subq	$1, -16(%rbp)
	addq	$1, -8(%rbp)
	movq	-8(%rbp), %rax
	cmpq	-16(%rbp), %rax
	jb	.L9
	movl	-20(%rbp), %eax
	popq	%rbp
	ret

	############################################################
	# put: prints an integer value to the terminal
	# expects the integer value on the stack.
	.global put
put:
	### get int and convert it to str
	mov  	8(%rsp), %edi 		# int - actual argument
	mov 	$rtsbuf, %rsi 	        # buffer pointer
	call 	itoa
	### print str to stdout
	### Note: buffer pointer in %rsi still valid
	mov	%rax, %rdx 		# len
	mov 	$1, %rdi 		# fd == 1, stdout
	mov 	$1, %rax 		# 1, sys_write
	syscall
	### print newline char
	mov 	$nlbuf, %rsi 	        # buffer pointer
	mov 	$1, %rdx 		# len
	mov 	$1, %rdi 		# fd == 1, stdout
	mov 	$1, %rax 		# 1, sys_write
	syscall
	ret

	############################################################
	# get: prompts the user for an integer value and
	# returns the integer value in %eax
	.global get
get:
	### print prompt
	mov 	$promptbuf, %rsi 	# buffer pointer
	mov 	$2, %rdx 		# len of prompt
	mov 	$1, %rdi 		# fd == 1, stdout
	mov 	$1, %rax 		# 1, sys_write
	syscall
	### read str from stdin
	mov 	$rtsbuf, %rsi 		# buffer pointer
	mov 	$256, %rdx 		# len
	mov 	$0, %rdi 		# fd == 0, stdin
	mov 	$0, %rax 		# 0, sys_read
	syscall				# num char read in %eax
	sub 	$1, %eax 		# get rid of \n char
	### convert str to int
	mov  	%eax, %esi 		# len
	mov 	$rtsbuf, %rdi    	# buffer pointer
	call 	atoi			# result in %eax
	ret

	############################################################
	# exit: shut down process cleanly
	.global exit
exit:
	mov 	$60,%rax		# sys_exit
	mov 	$0,%rdi			# 0, no error
	syscall
	
