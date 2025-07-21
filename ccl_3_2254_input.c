#include <stdio.h>

int main() {
    int a, b, sum, product;
// input first number
    printf("Enter first number: ");
    scanf("%d", &a);
// input second number
    printf("Enter second number: ");
    scanf("%d", &b);


// Check a condition
  if(a == 0 && b == 0) return 0;
  if(a > 0 && b>0){
    sum = a + b;
    product = a * b;
  }
    
/* Final Result */
    printf("Sum: %d\n", sum);
    printf("Product: %d\n", product);

    return 0;

 print(" Here result will be come in int number, not float or double")

}