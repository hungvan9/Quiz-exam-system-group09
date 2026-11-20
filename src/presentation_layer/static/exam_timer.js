/* Student exam countdown and AJAX autosave.
 * Expected page contract:
 *   data-attempt-id on #exam-timer, data-remaining-seconds on #exam-timer
 *   inputs use data-question-id and either data-answer-id or data-written-answer
 * The server remains authoritative for the deadline.
 */
(() => {
  "use strict";

  const timer = document.querySelector("#exam-timer");
  if (!timer) return;

  const attemptId = timer.dataset.attemptId;
  const saveUrl = timer.dataset.saveUrl || `/student/exams/attempts/${attemptId}/answers`;
  const submitUrl = timer.dataset.submitUrl || `/student/exams/attempts/${attemptId}/submit`;
  let remaining = Math.max(0, Number(timer.dataset.remainingSeconds || 0));
  let submitting = false;
  const pending = new Map();

  const render = () => {
    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;
    timer.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    timer.classList.toggle("time-warning", remaining <= 300);
    timer.classList.toggle("time-critical", remaining <= 60);
  };

  async function save(input) {
    const questionId = Number(input.dataset.questionId);
    if (!questionId) return;
    const body = { question_id: questionId };
    if (input.dataset.answerId) {
      body.selected_answer_id = Number(input.dataset.answerId);
    } else if (input.dataset.writtenAnswer !== undefined || input.name) {
      const field = input.dataset.writtenAnswer !== undefined
        ? input : document.querySelector(`[name="${CSS.escape(input.name)}"]`);
      body.answer_content = field ? field.value : input.value;
    } else {
      return;
    }

    const key = String(questionId);
    pending.set(key, body);
    try {
      const response = await fetch(saveUrl, {
        method: "PUT",
        headers: { "Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest" },
        body: JSON.stringify(body),
        credentials: "same-origin"
      });
      if (!response.ok) throw new Error(`Autosave failed (${response.status})`);
      pending.delete(key);
      input.dataset.saved = "true";
      input.dispatchEvent(new CustomEvent("answer:saved", { bubbles: true }));
    } catch (error) {
      input.dataset.saved = "false";
      input.dispatchEvent(new CustomEvent("answer:save-error", {
        bubbles: true, detail: { message: error.message }
      }));
    }
  }

  document.addEventListener("change", event => {
    const input = event.target.closest("[data-question-id]");
    if (input) save(input);
  });
  document.addEventListener("input", event => {
    const input = event.target.closest("[data-question-id][data-written-answer]");
    if (!input) return;
    clearTimeout(input._autosaveTimer);
    input._autosaveTimer = setTimeout(() => save(input), 500);
  });

  async function submitAutomatically() {
    if (submitting) return;
    submitting = true;
    try {
      // Flush any latest written response before submitting.
      const unsaved = Array.from(document.querySelectorAll("[data-question-id]"));
      for (const input of unsaved) {
        if (input.matches("[data-written-answer]")) await save(input);
      }
      await fetch(submitUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ automatic: true }),
        credentials: "same-origin"
      });
    } finally {
      window.location.reload();
    }
  }

  render();
  const interval = window.setInterval(() => {
    remaining = Math.max(0, remaining - 1);
    render();
    if (remaining <= 0) {
      window.clearInterval(interval);
      submitAutomatically();
    }
  }, 1000);

  window.addEventListener("online", () => {
    // Retry current visible answers after connectivity is restored.
    document.querySelectorAll("[data-question-id]").forEach(input => {
      if (input.dataset.saved === "false") save(input);
    });
  });
})();
