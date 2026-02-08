// ========================================
// EduAgent AI - Frontend Logic
// ========================================

// DOM Elements
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingStep = document.getElementById('loadingStep');
const generateBtn = document.getElementById('generateBtn');
const emptyState = document.getElementById('emptyState');

// Pipeline step elements
const pipelineSteps = {
    step1: document.getElementById('step1'),
    step2: document.getElementById('step2'),
    step3: document.getElementById('step3'),
    step4: document.getElementById('step4')
};

// Output cards
const cards = {
    generator: document.getElementById('generatorCard'),
    reviewer: document.getElementById('reviewerCard'),
    refined: document.getElementById('refinedCard')
};

// State
let isGenerating = false;

// ========================================
// Main Pipeline Function
// ========================================
async function runPipeline() {
    if (isGenerating) return;

    const grade = document.getElementById('grade').value;
    const topic = document.getElementById('topic').value.trim();

    // Validation
    if (!topic) {
        showError('Please enter a topic');
        return;
    }

    if (!grade || grade < 1 || grade > 12) {
        showError('Please enter a valid grade (1-12)');
        return;
    }

    // Start loading
    isGenerating = true;
    showLoading(true);
    resetUI();

    // Animate pipeline: Input step active
    setActiveStep(1);
    updateLoadingStep('Processing input...');

    try {
        // Animate pipeline: Generator step
        await delay(500);
        setActiveStep(2);
        updateLoadingStep('Generator Agent creating content...');

        // Make API call
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grade: parseInt(grade), topic })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Generation failed');
        }

        // Show generator output
        await delay(300);
        setCompleteStep(1);
        setCompleteStep(2);
        displayGeneratorOutput(data.generator);

        // Animate pipeline: Reviewer step
        setActiveStep(3);
        updateLoadingStep('Reviewer Agent evaluating content...');
        await delay(800);

        // Show reviewer output
        setCompleteStep(3);
        displayReviewerOutput(data.reviewer);

        // If refined output exists, show it
        if (data.refined) {
            updateLoadingStep('Applying refinements...');
            await delay(500);
            displayRefinedOutput(data.refined);
        }

        // Complete pipeline
        setCompleteStep(4);
        setActiveStep(4);

    } catch (error) {
        console.error('Pipeline error:', error);
        showError(error.message || 'An error occurred. Please try again.');
    } finally {
        showLoading(false);
        isGenerating = false;
    }
}

// ========================================
// Display Functions
// ========================================
function displayGeneratorOutput(data) {
    emptyState.style.display = 'none';
    cards.generator.style.display = 'block';

    let explanation = "";
    let mcqs = [];

    // Smart Parsing Logic
    if (data.explanation) {
        // Standard success or partial parse
        explanation = data.explanation;
        mcqs = data.mcqs || [];
    } else if (data.parse_error && data.raw_response) {
        // Try to parse raw_response in JS if Python failed but it looks like JSON
        try {
            const parsed = JSON.parse(data.raw_response);
            if (parsed.explanation) {
                explanation = parsed.explanation;
                mcqs = parsed.mcqs || [];
            } else {
                // Formatting raw text nicely if not JSON
                explanation = data.raw_response;
            }
        } catch (e) {
            // If raw text is just text, use it as explanation
            explanation = data.raw_response.replace(/[{}]/g, ''); // Clean braces if messy
        }
    } else if (typeof data === 'string') {
        explanation = data;
    }

    // Display explanation
    document.getElementById('explanationText').textContent = explanation || 'No explanation generated.';

    // Display MCQs
    const mcqContainer = document.getElementById('mcqContainer');
    mcqContainer.innerHTML = '';

    if (mcqs && Array.isArray(mcqs) && mcqs.length > 0) {
        mcqs.forEach((mcq, index) => {
            mcqContainer.appendChild(createMcqElement(mcq, index + 1));
        });
    } else {
        mcqContainer.innerHTML = '<div class="feedback-item"><span>No MCQs generated due to format complexity.</span></div>';
    }

    // Animate card appearance
    setTimeout(() => cards.generator.classList.add('visible'), 50);
}

function displayReviewerOutput(data) {
    cards.reviewer.style.display = 'block';

    const statusBadge = document.getElementById('reviewStatus');
    const content = document.getElementById('reviewerContent');

    // Handle raw response
    if (typeof data === 'string') {
        statusBadge.textContent = 'REVIEWED';
        statusBadge.className = 'status-badge pass';
        content.innerHTML = `<p class="explanation-text">${data}</p>`;
        setTimeout(() => cards.reviewer.classList.add('visible'), 50);
        return;
    }

    // Set status badge
    const status = data.status?.toLowerCase() || 'pass';
    statusBadge.textContent = status.toUpperCase();
    statusBadge.className = `status-badge ${status}`;

    // Display feedback
    if (status === 'pass' && (!data.feedback || data.feedback.length === 0)) {
        content.innerHTML = `
            <div class="explanation-text" style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 24px;">✅</span>
                <span>Content passed all quality checks! Ready for use.</span>
            </div>
        `;
    } else if (data.feedback && data.feedback.length > 0) {
        const feedbackHtml = data.feedback.map(item => `
            <div class="feedback-item">
                <span class="feedback-icon">⚠️</span>
                <span>${escapeHtml(item)}</span>
            </div>
        `).join('');
        content.innerHTML = `
            <h3 class="section-title">Issues Found</h3>
            <div class="feedback-list">${feedbackHtml}</div>
        `;
    } else {
        content.innerHTML = `<p class="explanation-text">Review completed.</p>`;
    }

    setTimeout(() => cards.reviewer.classList.add('visible'), 50);
}

function displayRefinedOutput(data) {
    cards.refined.style.display = 'block';

    let explanation = "";
    let mcqs = [];

    if (data.explanation) {
        explanation = data.explanation;
        mcqs = data.mcqs || [];
    } else if (data.parse_error) {
        explanation = data.raw_response || "Refinement processing error.";
    }

    // Display refined explanation
    document.getElementById('refinedExplanation').textContent = explanation;

    // Display refined MCQs
    const mcqContainer = document.getElementById('refinedMcqContainer');
    mcqContainer.innerHTML = '';

    if (mcqs && Array.isArray(mcqs)) {
        mcqs.forEach((mcq, index) => {
            mcqContainer.appendChild(createMcqElement(mcq, index + 1));
        });
    }

    setTimeout(() => cards.refined.classList.add('visible'), 50);
}

// ========================================
// UI Helper Functions
// ========================================
function createMcqElement(mcq, number) {
    const div = document.createElement('div');
    div.className = 'mcq-item';

    const question = mcq.question || 'No question';
    const options = mcq.options || [];
    const answer = mcq.answer || '';

    let optionsHtml = '';
    options.forEach((opt, i) => {
        const letter = String.fromCharCode(65 + i); // A, B, C, D
        const isCorrect = answer === letter || answer === opt || answer.includes(letter);
        const optionText = opt.startsWith(letter + ')') || opt.startsWith(letter + '.') ? opt : `${letter}) ${opt}`;
        optionsHtml += `<div class="mcq-option ${isCorrect ? 'correct' : ''}">${escapeHtml(optionText)}</div>`;
    });

    div.innerHTML = `
        <div class="mcq-question">Q${number}. ${escapeHtml(question)}</div>
        <div class="mcq-options">${optionsHtml}</div>
    `;

    return div;
}

function setActiveStep(stepNum) {
    // Remove active from all
    Object.values(pipelineSteps).forEach(step => {
        step.classList.remove('active');
    });
    // Set active
    const step = pipelineSteps[`step${stepNum}`];
    if (step) step.classList.add('active');
}

function setCompleteStep(stepNum) {
    const step = pipelineSteps[`step${stepNum}`];
    if (step) {
        step.classList.remove('active');
        step.classList.add('complete');
    }
}

function resetUI() {
    // Hide all cards
    Object.values(cards).forEach(card => {
        card.style.display = 'none';
        card.classList.remove('visible');
        card.classList.remove('fade-in'); // Ensure animations reset
    });

    // Reset pipeline steps
    Object.values(pipelineSteps).forEach(step => {
        step.classList.remove('active', 'complete');
    });

    // Show empty state (will be hidden when results come in)
    emptyState.style.display = 'block';

    // Clear content
    document.getElementById('explanationText').textContent = '';
    document.getElementById('mcqContainer').innerHTML = '';
}

function showLoading(show) {
    loadingOverlay.classList.toggle('visible', show);
    generateBtn.disabled = show;
}

function updateLoadingStep(text) {
    loadingStep.textContent = text;
}

function showError(message) {
    alert(message); // Simple error display - could be enhanced
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ========================================
// Event Listeners
// ========================================
document.getElementById('topic').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        runPipeline();
    }
});
