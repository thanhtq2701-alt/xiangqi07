<div align="center">

<img src="web/cover-co-chill.webp" alt="Cờ Chill" width="720">

# 帥 Cờ Chill

### Learn Xiangqi by thinking through the position, not by skipping to the answer.

*Chơi một ván, học từ nước đi của mình.*

[![Checks](https://github.com/thanhtq2701-alt/xiangqi07/actions/workflows/checks.yml/badge.svg?branch=codex-full)](https://github.com/thanhtq2701-alt/xiangqi07/actions/workflows/checks.yml)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![No build step](https://img.shields.io/badge/JavaScript-no%20build%20step-F7DF1E?logo=javascript&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-local%20data-003B57?logo=sqlite&logoColor=white)
![Tiếng Việt · English](https://img.shields.io/badge/UI-Ti%E1%BA%BFng%20Vi%E1%BB%87t%20%C2%B7%20English-c0392b)

### [🏮 Play now at cochill.vn](https://cochill.vn)

</div>

<br>

<p align="center">
  <img src="docs/images/exercise.webp" alt="A multi-move exercise: the learner answers three questions about the position before choosing a move" width="860">
  <br>
  <sub><b>Think first.</b> Every exercise asks what you see, what you want and how your opponent will reply, before any explanation appears.</sub>
</p>

## 🧧 Why Cờ Chill

Most puzzle apps tell you right or wrong and move on. Cờ Chill slows down at the moment that matters: you read the position, write down your plan, try your move, and only then see an explanation grounded in checked lines. Then you retry, practise a related position and come back for review a few days later.

```mermaid
flowchart LR
    A["車 Play or load a game"] --> B["⏸️ Critical moment"]
    B --> C["🤔 Reflect"]
    C --> D["💡 Grounded explanation"]
    D --> E["🔁 Retry"]
    E --> F["🧩 Related practice"]
    F --> G["📅 Spaced review"]
    G --> H["📈 Progress"]
```

## 🐉 Features

<table>
<tr>
<td width="50%" valign="top">

### 車 Play
Signed-in players face a **7-level bot** that moves up or down based on their last 10 games at a level; guests play a light bot on their own device. Or play two players on one device, or in friendly online rooms where the server owns moves, clocks and results.

</td>
<td width="50%" valign="top">

### 炮 Learn by chapter
Opening, middlegame and endgame chapters for the Rook, Cannon, Horse, Pawn, King safety and coordination, with multi-move exercises from a single decision up to five to seven.

</td>
</tr>
<tr>
<td valign="top">

### 兵 Reflection before answers
No solution is shown before you have thought it through, and no coaching appears during a live game.

</td>
<td valign="top">

### 馬 Spaced review
Positions you finish come back at growing intervals (1 / 2 / 7 / 14 / 30 days), and the ones you needed help with return sooner.

</td>
</tr>
<tr>
<td valign="top">

### 帥 Rules own the truth
Python and JavaScript rules are cross-checked on every change. Explanations are built only from checked lines, never invented moves or evaluations.

</td>
<td valign="top">

### 士 Your data, your call
Play as a guest with no account, or sign in to sync. Export, import with preview, and delete your own data at any time.

</td>
</tr>
</table>

## 📸 Screenshots

<table>
<tr>
<td width="50%"><img src="docs/images/play.webp" alt="A game against the bot, with clock and move list"></td>
<td width="50%"><img src="docs/images/lessons.webp" alt="The learning journey: chapters shown as carved pieces along a winding path"></td>
</tr>
<tr>
<td align="center"><sub><b>Play</b>: focus on the game; learning opens after it ends.</sub></td>
<td align="center"><sub><b>Learning journey</b>: pick any chapter, in any order.</sub></td>
</tr>
<tr>
<td width="50%"><img src="docs/images/home.webp" alt="Home page with the Cờ Chill cover"></td>
<td width="50%" align="center"><img src="docs/images/mobile.webp" alt="Cờ Chill on a phone" width="220"></td>
</tr>
<tr>
<td align="center"><sub><b>Home</b>: one tap to start, no account needed.</sub></td>
<td align="center"><sub><b>Phone</b>: the same app with a bottom tab bar.</sub></td>
</tr>
</table>

## 📚 What's inside

<div align="center">

| 🧩 **12** | 📖 **9** | 🎯 **72** | 🤖 **7** | 🌐 **2** |
|:---:|:---:|:---:|:---:|:---:|
| basic exercises | lessons | multi-move exercises | bot levels | languages |

</div>

70 of the multi-move exercises were written and reviewed by the project owner. The app checks their rules, checkmates and material, not their quality.

## 🔍 Honest by design

- The bot levels are not calibrated against real players and carry no Elo. The server bot uses [Pikafish](https://github.com/official-pikafish/Pikafish), a separate open-source engine that is not included in this repository.
- Explanations are templates or written by the project owner. There is no trained AI coach.
- The review schedule and progress signals are simple, experimental rules. No measured learning impact is claimed.

## 📜 License

No license has been chosen yet, so the code, content and artwork are not licensed for reuse.

<div align="center">
<br>

**[cochill.vn](https://cochill.vn)** · Vietnamese-first, with a full English mode · *Mỗi lần hiểu thêm một chút.*

</div>
