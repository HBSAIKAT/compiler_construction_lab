
#include <stdio.h>

int main() {
    int a, b, sum, product;

    printf("Enter first number: ");
    scanf("%d", &a);

    printf("Enter second number: ");
    scanf("%d", &b);

    sum = a + b;
    product = a * b;


    printf("Sum: %d\n", sum);
    printf("Product: %d\n", product);

    return 0;
}
