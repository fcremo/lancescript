int plaintext[10];
int ciphertext[10];
int i;
int p;
int key = 42;

plaintext[0] = 67;
plaintext[1] = 105;
plaintext[2] = 97;
plaintext[3] = 111;
plaintext[4] = 32;
plaintext[5] = 65;
plaintext[6] = 108;
plaintext[7] = 101;
plaintext[8] = 120;
plaintext[9] = 33;

for (i=0; i<10; i=i+1) {
    ciphertext[i] = plaintext[i] ^ key;
}


for (i=0; i<10; i=i+1) {
    p = ciphertext[i] ^ key;
    write(p);
}
