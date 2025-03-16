# Reversing ELF by Tryhackme

## Challenge Description
An easy, introductory reverse engineering challenge. Get ready to flex those brain muscles!

### Category
Reverse engineering

### Difficulty
Introductory

<p align="center">
  <img src="https://i.programmerhumor.io/2024/08/programmerhumor-io-programming-memes-200870bc6f5ee66.jpe" width="200">
</p>

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

<p align="center">
  <img src="https://raw.githubusercontent.com/yusufsaka007/CTF/refs/heads/main/ReversingELF/img/1.png" width="200">
</p>

## 2 - Challenge 2
Let's use the `strings` command to see the hidden strings and snag the password. Piece of cake, right?

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/2.png?raw=true" width="200">
</p>

## 3 - Challenge 3
Run `strings` again for `crackme3` and we get an encoded password that looks like it’s in Base64. Time to decode it and reveal its secrets!

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/3_1.png?raw=true" width="200">
</p>
<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/3_2.png?raw=true" width="200">
</p>
## 4 - Challenge 4
Running `./crackme4` with a random password gives us a tip. This sneaky string is hidden and uses `strcmp`.

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/4_1.png?raw=true" width="200">
</p>


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
<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/4_2.png?raw=true" width="200">
</p>
<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/4_3.png?raw=true" width="200">
</p>
<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/4_4.png?raw=true" width="200">
</p>

## 5 - Challenge 5
Time to bring out the big guns: Ghidra. We see bytes being added to an array. Converting those bytes into characters, we can see the password. Enter the password and voilà, success!

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/5_1.png?raw=true" width="200">
</p>

## 6 - Challenge 6
Now we analyze the `my_secure_test` function called in `compare_pwd`. If `my_secure_test` returns 0, the password is correct. Let’s figure out what to provide to get that magical 0.

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/6_1.png?raw=true" width="200">
</p>

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/6_2.png?raw=true" width="200">
</p>
## 7 - Challenge 7
Executing the program, we face a menu with 3 options:
1. Say hello
2. Add numbers
3. Quit

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/7_1.png?raw=true" width="200">
</p>

The program claims we only have 3 options, but let’s see if we can find a secret fourth option using Ghidra. If we input the password corresponding to `0x7a69` (which is `31337`), we get the flag. Hacking is fun!

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/7_2.png?raw=true" width="200">
</p>
<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/7_3.png?raw=true" width="200">
</p>

## 8 - Challenge 8
Another straightforward challenge. The program takes an argument via `argv[1]`, converts it to a string with `atoi`, and checks if it equals `-889262067`. Let’s smash that check!

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/8_1.png?raw=true" width="200">
</p>
<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/8_2.png?raw=true" width="200">
</p>

And there you have it, the flag is ours!

<p align="center">
  <img src="https://github.com/yusufsaka007/CTF/blob/main/ReversingELF/img/end.png?raw=true" width="400">
</p>

**From now on I will be sharing my writeups online so that it may help other people who struggle to find the solution to the next step but most importantly I will be able to learn better by teaching others. Even if writeups can sometimes be quite useful it's important to remember that as a hacker we will constantly face challenges which will require us to solve them without any help (atleast in certain circumstances. So it is a good practice to not give up, research deeply and continue. I hope you enjoyed this writeup**
