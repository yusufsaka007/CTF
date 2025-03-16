# Reversing ELF by Tryhackme

## Challenge Description
An easy, introductory reverse engineering challenge.

### Category
Reverse engineering

### Difficulty
Introductory

![Image of a meme](path_to_your_image)

This CTF room consists of 8 different challenges, each containing its own files which we need to crack. We will use different tools such as `gdb` and `ghidra`. Basic knowledge of reverse engineering, assembly, debuggers, and Linux commands are required.

### Some Useful Sources to Learn
- **Gray Hat Hacking 6th Edition**
- **Practical Reverse Engineering**
- **Malware Bible free course**: [Malcore.io](https://bible.malcore.io/) (Twitter: [@malcoreio](https://twitter.com/malcoreio))

## 0 - Installing the Files + Preparation
```
mv ~/Downloads/crackme* .
```

## 1 - Challenge 1
Just execute the program (first `chmod +x` to make it executable) and you will get the flag.

![Challenge 1](path_to_your_image)

## 2 - Challenge 2
Run the `strings` command to see the strings and you will get the password.

![Challenge 2](path_to_your_image)

## 3 - Challenge 3
Run `strings` again for `crackme3` which gives us an encoded password that looks like it is encoded in Base64. Decoding it with Base64:

![Challenge 3](path_to_your_image)

## 4 - Challenge 4
Running `./crackme4` with a random password, we get a tip. This time the string is hidden and it uses `strcmp`.

![Challenge 4](path_to_your_image)

Using `gdb`:
```
gdb crackme4
set args random_password
info functions  # We see there is a compare_pwd function
disassemble compare_pwd  # strcmp is called at address 0x4006d5
break *0x4006d5  # So that we can read the values of rsi and rdi
run  # Will stop at strcmp so that we can read the passed arguments
x/s $rsi
x/s $rdi
```
![GDB Analysis](path_to_your_image)

## 5 - Challenge 5
This time we bring the big gun: Ghidra. We see to an array bytes are added. Converting those bytes into chars, we can see the password. We enter the password and it is correct.

![Ghidra Analysis](path_to_your_image)

## 6 - Challenge 6
We will now analyze the `my_secure_test` function which is called in `compare_pwd`. If the return value of `my_secure_test` is 0, the password is correct. So what do we need to provide in order to get 0 as the return value? Looking at the decompiler of `my_secure_test`, we can easily understand what the password is.

![My Secure Test Analysis](path_to_your_image)

## 7 - Challenge 7
Executing the following command, we face a program that gives us 3 options: 
1. Say hello
2. Add numbers
3. Quit

The program tells us that we only have 3 options. But we, as hackers, can't be satisfied with such saying, so we open Ghidra. We see that the option we give is stored in the offset `[EBP + local_14]`. If we give as input the password corresponding to `0x7a69` which is `31337`, we can get the flag.

![Option Analysis](path_to_your_image)

## 8 - Challenge 8
Another easy challenge. We see it will take the argument given through `argv[1]`, use `atoi` to convert it to string, and check whether it is equal to `-889262067`.

![Argument Analysis](path_to_your_image)

And it is, hence we get the flag.

![Flag](path_to_your_image)