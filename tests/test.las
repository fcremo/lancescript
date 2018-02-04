define answer_to_everything 42

// asd asd

int a_scalar = 123, another_scalar;
int a_third_scalar, an_array[5];
int single_scalar;

def int my_function (int a_scalar, int b, int c[]){
    write(a_scalar);
    write(b);
    write(c[2]);
}

write(1 + (- 1) + answer_to_everything);

an_array[0] = 1;
an_array[1] = 2;
an_array[2] = 3;
an_array[3] = 4;
an_array[4] = 5;

my_function(1, 3 - 1, an_array);

another_scalar = an_array[1];
write(another_scalar);

a_scalar = 1 + 2;
write(a_scalar);

if (answer_to_everything == 42) {
    write(1);
}
else {
    write(0);
}

while(a_scalar > 0) {
    write(a_scalar);
    a_scalar = a_scalar - 1;
}

for (a_scalar=10; a_scalar > 0; a_scalar = a_scalar - 1;) {
    write(a_scalar);
}