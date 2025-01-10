from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json

app = Flask(__name__)

# Directory for storing posts
POSTS_DIR = "posts"
PASSWORD = "test"  # Default admin password

# Ensure the posts directory exists
os.makedirs(POSTS_DIR, exist_ok=True)

# Route for the homepage
@app.route("/")
def index():
    posts = []
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(POSTS_DIR, filename), "r") as f:
                post = json.load(f)
                posts.append({
                    "title": post["title"],
                    "description": post["description"],
                    "image": post.get("image"),
                    "filename": filename
                })
    return render_template("index.html", posts=posts)


# Route for the control panel (admin page)
@app.route("/control-panel")
def control_panel():
    return render_template("control-panel.html")


# Route for a single post
@app.route("/post/<filename>")
def post(filename):
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        return "Post not found", 404
    with open(filepath, "r") as f:
        post = json.load(f)
    return render_template("post.html", post=post)

# API to authenticate admin
@app.route("/api/auth", methods=["POST"])
def authenticate():
    data = request.json
    if data.get("password") == PASSWORD:
        return jsonify({"success": True})
    return jsonify({"error": "Invalid password"}), 403

# API to create or update a post
import re

@app.route("/api/posts", methods=["POST"])
def create_post():
    data = request.json
    title = data.get("title")
    description = data.get("description")
    content = data.get("content")
    image = data.get("image")

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    # Sanitize the title to create a valid filename
    filename = re.sub(r'[^a-zA-Z0-9 \n\.]', '', title)  # Remove non-alphanumeric characters
    filename = filename.replace(' ', '-').lower() + ".json"  # Replace spaces with dashes and convert to lowercase

    # Prepare post data
    post = {
        "title": title,
        "description": description,
        "content": content,
        "image": image
    }

    # Save post to the file
    try:
        with open(os.path.join(POSTS_DIR, filename), "w") as f:
            json.dump(post, f, indent=2)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": f"Failed to save post: {str(e)}"}), 500



# API to delete a post
@app.route("/api/posts/<filename>", methods=["DELETE"])
def delete_post(filename):
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Post not found"}), 404
    os.remove(filepath)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
