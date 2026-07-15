(() => {
  "use strict";

  const optionLabel = (option) => option.textContent.trim();
  const asSentence = (text) => (/[^\s][.!?]$/.test(text) ? text : `${text}.`);
  const explanation = (option) =>
    option.dataset.explanation || "This option does not match the evidence in the lesson.";

  const resetQuiz = (quiz) => {
    const options = [...quiz.querySelectorAll(".quiz-option")];
    const feedback = quiz.querySelector(".quiz-feedback");
    const reset = quiz.querySelector(".quiz-reset");

    options.forEach((option) => {
      option.disabled = false;
      option.classList.remove("correct", "incorrect");
      option.removeAttribute("aria-label");
    });
    feedback.textContent = "";
    reset.hidden = true;
    options[0]?.focus();
  };

  const submitAnswer = (quiz, selected) => {
    const options = [...quiz.querySelectorAll(".quiz-option")];
    const correct = options.find((option) => option.dataset.correct === "true");
    const feedback = quiz.querySelector(".quiz-feedback");
    const reset = quiz.querySelector(".quiz-reset");

    if (!correct || !feedback || !reset) return;

    const isCorrect = selected === correct;
    options.forEach((option) => {
      option.disabled = true;
      option.classList.remove("correct", "incorrect");
    });

    correct.classList.add("correct");
    correct.setAttribute("aria-label", `${optionLabel(correct)} — correct answer`);

    if (isCorrect) {
      feedback.textContent = `Correct. ${explanation(correct)}`;
    } else {
      selected.classList.add("incorrect");
      selected.setAttribute("aria-label", `${optionLabel(selected)} — selected, incorrect`);
      feedback.textContent = `Not quite. ${explanation(selected)} Correct answer: ${asSentence(optionLabel(correct))} ${explanation(correct)}`;
    }

    reset.hidden = quiz.dataset.retry !== "true";
    feedback.focus();
  };

  document.querySelectorAll("[data-quiz]").forEach((quiz) => {
    quiz.querySelectorAll(".quiz-option").forEach((option) => {
      option.addEventListener("click", () => submitAnswer(quiz, option));
    });
    quiz.querySelector(".quiz-reset")?.addEventListener("click", () => resetQuiz(quiz));
  });
})();
