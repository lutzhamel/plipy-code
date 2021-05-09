////////////////////////////////////////////////////////
// this is part of tinyrts a runtime system for the
// Cuppa3/x86_64 compiler
//
// in order to generate appropriate assembly code
// compile this with:
//    gcc -S -fno-asynchronous-unwind-tables atoi.c
//
// (c) Lutz Hamel, University of Rhode Island
////////////////////////////////////////////////////////

// the following code in based on:
// www.geeksforgeeks.org/write-your-own-atoi/
int atoi(char* str, int len)
{
	int res = 0;
	int sign = 1;
	int i = 0;

	if (str[0] == '-') {
		sign = -1;
		i++;
	}

	for (; i < len; i++)
		res = res * 10 + str[i] - '0';

	return sign * res;
}

// the following code is based on
// code.google.com/archive/p/my-itoa/
int itoa(int val, char* buf)
{
  const unsigned int radix = 10;
  char* p;
  unsigned int a;        //every digit
  int len;
  char* b;            //start of the digit char
  char temp;
  unsigned int u;

  p = buf;

  if (val < 0)
  {
      *p++ = '-';
      val = 0 - val;
  }

  u = (unsigned int)val;
  b = p;

  do
  {
      a = u % radix;
      u /= radix;

      *p++ = a + '0';

  } while (u > 0);

  len = (int)(p - buf);

  *p-- = 0;

  //swap
  do
  {
      temp = *p;
      *p = *b;
      *b = temp;
      --p;
      ++b;

  } while (b < p);

  return len;
}
