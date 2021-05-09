#include <stdio.h>

int add(int a, int b) {
  return a+b;
}

int foo() {
  int x = add(3,2);
  return x;
}

int main() {
  printf("%d\n", foo());
}

