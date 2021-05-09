####################################
# test harness

	.data
	.lcomm t$0, 8
	
	.text
	.global _start
_start:

	movq	$1, t$0
	call 	get		# prompt for int val
	add  	t$0, %rax	# add 1 to int val
	push 	%rax		# print incremented int val to terminal
	call 	put
	add 	$8, %rsp

	call 	exit
