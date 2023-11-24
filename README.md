# SmartReviewPad - An Enhanced Anki Add-on for Effective Reviewing 📚

## Introduction 🌟

SmartReviewPad is an Anki add-on that helps you review your cards more effectively. Now with added features like automatic answer checking and sound effects to improve your learning experience!

![image](https://github.com/Dor-sketch/Anki-SmartReviewPad/assets/138825033/25f219e9-173e-4ff1-96c3-cc756b1472a0)

---

## Motivation 🤔

Anki is a great tool for learning and memorizing information. However, it can be tedious to use, especially when reviewing large decks. SmartReviewPad aims to solve this problem by enhancing the Anki experience with new features and improvements.

## Architecture 🏗️

SmartReviewPad is implemented as an `Anki add-on`, extending Anki's internal functionality. It uses best practices for code readability and efficiency, including object-oriented programming and asynchronous event handling. 3 main components are used to implement the add-on:

1. `Hooking`: The code uses Anki's `gui_hooks` to append custom functions to existing events. For example, `gui_hooks.reviewer_did_show_question.append(my_update_card_review)` ensures that my_update_card_review gets called when the reviewer shows a question.

2. `Overriding`: The `MyReviewer` class inherits from Anki's Reviewer class. By defining methods in MyReviewer that also exist in the Reviewer class (like `onBridgeCmd`), the new class is overriding the base class's methods. This means when the method is called on an instance of MyReviewer, it will use your new definition instead of the original one.

3. `DOM Manipulation`: The code uses Anki's `webview.eval` function to execute JavaScript code in the reviewer window. This allows you to manipulate the DOM and change the HTML content of the page. For example, `webview.eval("document.getElementById('my-id').innerHTML = 'Hello World!'")` will change the inner HTML of the element with the id `my-id` to `Hello World!`.

## Features 🛠️

- **Interactive Front Side**: Now enhanced with automatic answer checking. Enter your answer on the front side of the card, and SmartReviewPad will automatically verify it against the back side. 🌍

- **Automatic Back Side**: The back side of your cards is auto-generated based on your input on the front side. 🔄

- **Automatic Review**: Review your cards directly in the editor. 🚀

- **Sound Effects**: Celebrate your correct answers with happy asynchronous sound effects. Compatible with Mac Sounds. 🔊

## New Updates 🆕

- **Performance-Monitoring Enhancement**: The new `Strike Counter` now tracks your streak of correct answers, helping you measure your progress more effectively.

- **New Hook**: We've migrated to a new hook for better event handling.

- **New Classes**: Introduced new classes for cleaner code and easier future enhancements.

- **New Logger**: Implemented a dedicated logger for better debugging and event tracking.

- **Cloze Support**: Cloze cards are now supported! 🎉
  - Note: Cloze cards are only partially supported. The add-on will only work with cloze cards that have a single cloze deletion. Multi-cloze cards are not supported at the moment.
  - The add-on will automatically detect cloze cards and enable the relevant features using `Cloze Detection`.

- **MathJax Support**: MathJax is now supported! 🎉
  - Note: To render MathJax, you need Pandoc installed on your machine. For more information, see [here](https://pandoc.org/installing.html).

## Installation 📥

1️⃣ Download the latest version of SmartReviewPad from [here](https://github.com/Dor-sketch/Anki-SmartReviewPad.git).

2️⃣ Copy the `SmartReviewPad` folder to your Anki add-ons folder. Navigate to `Tools > Add-ons > View Files...` in Anki to find the add-ons folder.

3️⃣ Restart Anki to complete the installation.

## Usage 📝

1️⃣ Open Anki and start reviewing a deck.

2️⃣ The add-on will automatically enhance your review session based on the SmartReviewPad features.

3️⃣ For more advanced settings, navigate to `Tools > Add-ons > SmartReviewPad > Config`.

## Code Overview 🖥️

The add-on is implemented in Python, extending Anki's internal functionality. It uses best practices for code readability and efficiency. For more information, see the [code comments](https://github.com/Dor-sketch/Anki-SmartReviewPad/blob/main/main.py).

## Contributing 🤝

If you find a bug or want to contribute to the code, feel free to open an issue or submit a pull request on GitHub.

## License 📜

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
