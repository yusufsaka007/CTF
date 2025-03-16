# Reversing ELF by Tryhackme

## Challenge Description
An easy, introductory reverse engineering challenge. Get ready to flex those brain muscles and dive into the world of binary mysteries!

### Category
Reverse engineering

### Difficulty
Introductory

![Image of a meme](path_to_your_image)

This CTF room consists of 8 different challenges, each with its own fiendish files to crack. We’ll wield powerful tools like `gdb` and `ghidra`. Basic knowledge of reverse engineering, assembly, debuggers, and Linux commands will be our secret weapons.

### Some Useful Sources to Learn
- **Gray Hat Hacking 6th Edition**
- **Practical Reverse Engineering**
- **Malware Bible free course**: [Malcore.io](https://bible.malcore.io/) (Twitter: [@malcoreio](https://twitter.com/malcoreio))

## 0 - Installing the Files + Preparation
First, let's get our files in order:
```
mv ~/Downloads/crackme* .
```

## 1 - Challenge 1
Time to start our journey! Just execute the program (first `chmod +x` to make it executable) and you will get the flag. Easy peasy!

![Challenge 1](path_to_your_image)

## 2 - Challenge 2
Let's use the `strings` command to see the hidden strings and snag the password. Piece of cake, right?

![Challenge 2](path_to_your_image)

## 3 - Challenge 3
Run `strings` again for `crackme3` and we get an encoded password that looks like it’s in Base64. Time to decode it and reveal its secrets!

![Challenge 3](path_to_your_image)

## 4 - Challenge 4
Running `./crackme4` with a random password gives us a tip. This sneaky string is hidden and uses `strcmp`.

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
Time to bring out the big guns: Ghidra. We see bytes being added to an array. Converting those bytes into characters, we can see the password. Enter the password and voilà, success!

![Ghidra Analysis](path_to_your_image)

## 6 - Challenge 6
Now we analyze the `my_secure_test` function called in `compare_pwd`. If `my_secure_test` returns 0, the password is correct. Let’s figure out what to provide to get that magical 0.

![My Secure Test Analysis](path_to_your_image)

## 7 - Challenge 7
Executing the program, we face a menu with 3 options:
1. Say hello
2. Add numbers
3. Quit

The program claims we only have 3 options, but let’s see if we can find a secret fourth option using Ghidra. If we input the password corresponding to `0x7a69` (which is `31337`), we get the flag. Hacking is fun!

![Option Analysis](path_to_your_image)

## 8 - Challenge 8
Another straightforward challenge. The program takes an argument via `argv[1]`, converts it to a string with `atoi`, and checks if it equals `-889262067`. Let’s smash that check!

![Argument Analysis](path_to_your_image)

And there you have it, the flag is ours!

![Flag](path_to_your_image)
