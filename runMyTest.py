import Mytest

print "Hello!"

if 6%2 == 0:
	print "Success"
	print Mytest.get_filepaths("MyTestCases")
 	exit(0)
else:
	print "Failure"	
	exit(1)
