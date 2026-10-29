/**
 * Research Analyst Agents Frontend Client Logic
 * Coordinates 3-Agent visual pipeline, request submission, and report formatting.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const form = document.getElementById("legalForm");
  const questionInput = document.getElementById("questionInput");
  const charCount = document.getElementById("charCount");
  const submitBtn = document.getElementById("submitBtn");
  const clearBtn = document.getElementById("clearBtn");
  const copyBtn = document.getElementById("copyBtn");

  const systemStatus = document.getElementById("systemStatus");
  const statusLabel = document.getElementById("statusLabel");
  const modelTag = document.getElementById("modelTag");

  const emptyView = document.getElementById("emptyView");
  const loadingView = document.getElementById("loadingView");
  const loadingLabel = document.getElementById("loadingLabel");
  const loadingCaption = document.getElementById("loadingCaption");

  const errorView = document.getElementById("errorView");
  const errorMsg = document.getElementById("errorMsg");

  const responseView = document.getElementById("responseView");
  const sourcesBlock = document.getElementById("sourcesBlock");
  const sourcesTags = document.getElementById("sourcesTags");
  const answerArticle = document.getElementById("answerArticle");
  const disclaimerNotice = document.getElementById("disclaimerNotice");

  const pipe1 = document.getElementById("pipe1");
  const pipe2 = document.getElementById("pipe2");
  const pipe3 = document.getElementById("pipe3");

  const printBtn = document.getElementById("printBtn");
  const memoTimestamp = document.getElementById("memoTimestamp");

  let latestReportRaw = "";
  let pipelineTimer = null;

  // Initialize
  verifyBackendStatus();

  // Character counter
  questionInput.addEventListener("input", () => {
    charCount.textContent = questionInput.value.length;
  });

  // Suggestion chips
  document.querySelectorAll(".suggestion-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      questionInput.value = btn.getAttribute("data-query");
      charCount.textContent = questionInput.value.length;
      questionInput.focus();
    });
  });

  // Clear button
  clearBtn.addEventListener("click", () => {
    questionInput.value = "";
    charCount.textContent = "0";
    showView("empty");
    resetPipeline();
    questionInput.focus();
  });

  // Copy report
  copyBtn.addEventListener("click", async () => {
    if (!latestReportRaw) return;
    try {
      await navigator.clipboard.writeText(latestReportRaw);
      const originalText = copyBtn.querySelector("span").textContent;
      copyBtn.querySelector("span").textContent = "Copied!";
      setTimeout(() => {
        copyBtn.querySelector("span").textContent = originalText;
      }, 2000);
    } catch (e) {
      console.warn("Failed to copy report text: ", e);
    }
  });

  // Print button
  if (printBtn) {
    printBtn.addEventListener("click", () => {
      window.print();
    });
  }

  // Handle Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = questionInput.value.trim();
    if (!query || query.length < 4) return;

    // UI state: loading
    showView("loading");
    setSubmitState(true);
    startPipelineAnimation();

    try {
      const response = await fetch("/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: query }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Server error (${response.status})`);
      }

      finishPipelineAnimation();
      latestReportRaw = data.report || data.answer || "No report generated.";

      renderReport(latestReportRaw);
      renderSources(data.sources || []);
      renderDisclaimer(data.disclaimer);

      if (memoTimestamp) {
        memoTimestamp.textContent = new Date().toLocaleString(undefined, {
          dateStyle: "medium",
          timeStyle: "short",
        });
      }

      showView("response");
    } catch (err) {
      stopPipelineAnimation();
      errorMsg.textContent = err.message || "Failed to complete research analysis.";
      showView("error");
    } finally {
      setSubmitState(false);
    }
  });

  // Backend Healthcheck
  async function verifyBackendStatus() {
    try {
      const res = await fetch("/health");
      if (!res.ok) throw new Error("Health check failed");
      const health = await res.json();

      systemStatus.classList.remove("error");
      systemStatus.classList.add("healthy");
      statusLabel.textContent = "Multi-Agent System Ready";
      if (modelTag && health.model) {
        modelTag.textContent = health.model;
      }
    } catch (err) {
      systemStatus.classList.remove("healthy");
      systemStatus.classList.add("error");
      statusLabel.textContent = "Service Offline";
    }
  }

  // Pipeline visual state machine
  function resetPipeline() {
    [pipe1, pipe2, pipe3].forEach((el) => {
      if (el) el.classList.remove("active", "completed");
    });
  }

  function startPipelineAnimation() {
    resetPipeline();
    if (pipe1) pipe1.classList.add("active");
    loadingLabel.textContent = "Agent 1: Research Agent Gathering Information...";
    loadingCaption.textContent = "Searching research knowledge base, extracting benchmarks, and assembling evidence...";

    let step = 1;
    pipelineTimer = setInterval(() => {
      step++;
      if (step === 2) {
        if (pipe1) {
          pipe1.classList.remove("active");
          pipe1.classList.add("completed");
        }
        if (pipe2) pipe2.classList.add("active");
        loadingLabel.textContent = "Agent 2: Analysis & Verification Agent Auditing...";
        loadingCaption.textContent = "Validating empirical claims, detecting uncertainties, and extracting strategic insights...";
      } else if (step === 3) {
        if (pipe2) {
          pipe2.classList.remove("active");
          pipe2.classList.add("completed");
        }
        if (pipe3) pipe3.classList.add("active");
        loadingLabel.textContent = "Agent 3: Report Generation Agent Synthesizing...";
        loadingCaption.textContent = "Formatting publication-grade executive sections, recommendations, and citations...";
      }
    }, 4500);
  }

  function finishPipelineAnimation() {
    clearInterval(pipelineTimer);
    [pipe1, pipe2, pipe3].forEach((el) => {
      if (el) {
        el.classList.remove("active");
        el.classList.add("completed");
      }
    });
  }

  function stopPipelineAnimation() {
    clearInterval(pipelineTimer);
    resetPipeline();
  }

  function setSubmitState(isSubmitting) {
    submitBtn.disabled = isSubmitting;
    if (isSubmitting) {
      submitBtn.classList.add("btn-loading");
    } else {
      submitBtn.classList.remove("btn-loading");
    }
  }

  function showView(view) {
    emptyView.style.display = view === "empty" ? "flex" : "none";
    loadingView.style.display = view === "loading" ? "flex" : "none";
    errorView.style.display = view === "error" ? "flex" : "none";
    responseView.style.display = view === "response" ? "block" : "none";

    copyBtn.style.display = view === "response" ? "inline-flex" : "none";
    if (printBtn) {
      printBtn.style.display = view === "response" ? "inline-flex" : "none";
    }
  }

  function renderSources(sources) {
    if (!sources || sources.length === 0) {
      sourcesBlock.style.display = "none";
      return;
    }
    sourcesTags.innerHTML = "";
    sources.forEach((src) => {
      const tag = document.createElement("span");
      tag.className = "source-tag";
      tag.textContent = src;
      sourcesTags.appendChild(tag);
    });
    sourcesBlock.style.display = "block";
  }

  function renderDisclaimer(text) {
    if (disclaimerNotice) {
      disclaimerNotice.textContent = text || "";
    }
  }

  function renderReport(markdown) {
    answerArticle.innerHTML = parseMarkdownToHTML(markdown);
  }

  // Lightweight robust Markdown parser
  function parseMarkdownToHTML(md) {
    if (!md) return "";

    const lines = md.split("\n");
    let html = "";
    let inList = false;
    let inOrderedList = false;
    let inBlockquote = false;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];

      // Blockquotes
      if (line.startsWith("> ")) {
        if (!inBlockquote) {
          html += "<blockquote>";
          inBlockquote = true;
        }
        line = line.substring(2);
      } else if (inBlockquote) {
        html += "</blockquote>";
        inBlockquote = false;
      }

      // Headings
      if (line.startsWith("### ")) {
        closeLists();
        html += `<h3>${formatInline(line.substring(4))}</h3>`;
        continue;
      }
      if (line.startsWith("## ")) {
        closeLists();
        html += `<h2>${formatInline(line.substring(3))}</h2>`;
        continue;
      }
      if (line.startsWith("# ")) {
        closeLists();
        html += `<h1>${formatInline(line.substring(2))}</h1>`;
        continue;
      }

      // Unordered lists
      if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
        if (!inList) {
          if (inOrderedList) {
            html += "</ol>";
            inOrderedList = false;
          }
          html += "<ul>";
          inList = true;
        }
        const itemContent = line.trim().substring(2);
        html += `<li>${formatInline(itemContent)}</li>`;
        continue;
      }

      // Ordered lists (e.g. 1. )
      const orderedMatch = line.trim().match(/^(\d+)\.\s+(.*)/);
      if (orderedMatch) {
        if (!inOrderedList) {
          if (inList) {
            html += "</ul>";
            inList = false;
          }
          html += "<ol>";
          inOrderedList = true;
        }
        html += `<li>${formatInline(orderedMatch[2])}</li>`;
        continue;
      }

      // If we were in a list and hit a non-list item
      closeLists();

      // Empty line / paragraph separation
      if (!line.trim()) {
        continue;
      }

      // Horizontal rule
      if (line.trim() === "---" || line.trim() === "***") {
        html += "<hr>";
        continue;
      }

      // Standard paragraph
      html += `<p>${formatInline(line)}</p>`;
    }

    closeLists();
    if (inBlockquote) html += "</blockquote>";

    return html;

    function closeLists() {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      if (inOrderedList) {
        html += "</ol>";
        inOrderedList = false;
      }
    }

    function formatInline(text) {
      return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    }
  }
});
