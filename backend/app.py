from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from generator_agent import GeneratorAgent
from reviewer_agent import ReviewerAgent
import json

app = Flask(__name__)
CORS(app)

# Product configuration
PRODUCT_NAME = "EduAgent AI"
PRODUCT_TAGLINE = "Intelligent Educational Content Generation"

generator = GeneratorAgent()
reviewer = ReviewerAgent()

@app.route("/")
def home():
    return render_template("index.html", product_name=PRODUCT_NAME, tagline=PRODUCT_TAGLINE)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        grade = data.get("grade", 4)
        topic = data.get("topic", "")

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # Step 1: Generate content
        generator_output = generator.generate(grade, topic)
        
        # Step 2: Review content
        review_output = reviewer.review(generator_output, grade)
        
        # Step 3: Refine if failed (only one pass allowed)
        refined_output = None
        if isinstance(review_output, dict) and review_output.get("status") == "fail":
            feedback_text = "\n".join(review_output.get("feedback", []))
            refined_output = generator.generate(grade, topic, feedback_text)

        return jsonify({
            "success": True,
            "product_name": PRODUCT_NAME,
            "generator": generator_output,
            "reviewer": review_output,
            "refined": refined_output
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "product": PRODUCT_NAME})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
